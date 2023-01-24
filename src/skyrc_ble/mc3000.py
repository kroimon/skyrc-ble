from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from struct import Struct

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTCharacteristic
from bleak.exc import BleakError
from bleak_retry_connector import establish_connection

from .const import MC3000_CHANNEL_COUNT, MC3000_CHARACTERISTIC_UUID
from .models import (
    BatteryType,
    ChannelMode,
    ChannelStatus,
    LedColor,
    Mc3000BasicData,
    Mc3000ChannelData,
    Mc3000State,
    Mc3000VersionInfo,
)

_LOGGER = logging.getLogger(__name__)

PACKET_MAGIC = 0x0F

CMD_GET_CHANNEL_DATA = 0x55
CMD_GET_VOLTAGE_CURVE = 0x56
CMD_GET_VERSION_INFO = 0x57
CMD_GET_BASIC_DATA = 0x61
CMD_START_CHARGE = 0x05
CMD_STOP_CHARGE = 0xFE

STRUCT_GET_CHANNEL_DATA = Struct(">BBBBBHHHHBHB")
STRUCT_GET_VERSION_INFO = Struct(">xxxxxxxxxxxxBBB")
STRUCT_GET_BASIC_DATA = Struct(">B?B?BH")


class Mc3000:
    def __init__(self, ble_device: BLEDevice) -> None:
        """Init the MC3000 device."""
        self._ble_device = ble_device
        self._client: BleakClient = None
        self._client_lock: asyncio.Lock = asyncio.Lock()
        self._packet_received: asyncio.Event = asyncio.Event()
        self._state: Mc3000State = Mc3000State()

    def set_ble_device(self, ble_device: BLEDevice) -> None:
        """Update the BLE device."""
        self._ble_device = ble_device

    @property
    def name(self) -> str:
        """Get the name of the device."""
        return self._ble_device.name or self._ble_device.address

    @property
    def address(self) -> str:
        """Get the address of the device."""
        return self._ble_device.address

    @property
    def is_connected(self) -> bool:
        """Get the connection state."""
        return self._client is not None

    @property
    def state(self) -> Mc3000State:
        """Get the state of the device."""
        return self._state

    async def connect(self) -> None:
        """Connect to the device."""

        if self.is_connected or self._client_lock.locked():
            return

        async with self._client_lock:
            try:
                _LOGGER.debug(
                    "%s: Connecting to address %s", self.name, self._ble_device.address
                )

                def disconnected_callback(
                    client: BleakClient,
                ) -> None:  # pylint: disable=unused-argument
                    _LOGGER.warning(
                        "%s: Disconnected from address %s",
                        self.name,
                        self._ble_device.address,
                    )
                    self._client = None

                self._client = await establish_connection(
                    client_class=BleakClient,
                    device=self._ble_device,
                    name=self.name,
                    disconnected_callback=disconnected_callback,
                )

                await self._client.start_notify(
                    MC3000_CHARACTERISTIC_UUID, self._notification_callback
                )

                _LOGGER.debug(
                    "%s: Successfully connected to address %s",
                    self.name,
                    self._ble_device.address,
                )

            except BleakError:
                _LOGGER.error(
                    "%s: Failed to connect to address %s",
                    self.name,
                    self._ble_device.address,
                )
                self._client = None

        await self._send_packet(CMD_GET_VERSION_INFO)

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self.is_connected:
            async with self._client_lock:
                _LOGGER.debug(
                    "%s: Disconnecting from address %s",
                    self.name,
                    self._ble_device.address,
                )
                await self._client.disconnect()

    async def update(self) -> None:
        """Update the state of the device."""

        if not self.is_connected:
            await self.connect()

        try:
            await self._send_packet(CMD_GET_BASIC_DATA)
            for channel in range(0, MC3000_CHANNEL_COUNT):
                await self._send_packet(CMD_GET_CHANNEL_DATA, [channel])

        except BleakError as error:
            if self.is_connected:
                raise error

    async def start_charge(self, channel: int) -> None:
        """Start charging the battery in the specified channel."""
        if channel not in range(0, MC3000_CHANNEL_COUNT):
            raise ValueError("Invalid channel")
        await self._send_packet(CMD_START_CHARGE, [channel + 1])

    async def stop_charge(self, channel: int) -> None:
        """Stop charging the battery in the specified channel."""
        if channel not in range(0, MC3000_CHANNEL_COUNT):
            raise ValueError("Invalid channel")
        await self._send_packet(CMD_STOP_CHARGE, [channel + 1])

    async def _send_packet(self, command: int, payload: list[int] = []) -> None:
        """Send a packet to the device."""

        # Pad payload with zeros
        payload = payload + [0] * (17 - len(payload))

        # Format packet and calculate checksum
        packet = [PACKET_MAGIC, command, *payload, 0]
        packet[-1] = sum(packet) & 255
        packet_bytes = bytes(packet)

        # Send packet and wait for response
        _LOGGER.debug("%s: Sending packet: %s", self.name, packet_bytes.hex())
        async with self._client_lock:
            self._packet_received.clear()
            await self._client.write_gatt_char(MC3000_CHARACTERISTIC_UUID, packet_bytes)
            with suppress(TimeoutError):
                await asyncio.wait_for(self._packet_received.wait(), 2)

    async def _notification_callback(
        self, sender: BleakGATTCharacteristic, packet: bytearray
    ) -> None:
        """Handle a GATT notification."""
        await self._parse_packet(packet)
        self._packet_received.set()

    async def _parse_packet(self, packet: bytearray) -> None:
        """Parse single-packet messages and update the data model.

        Multi-packet messages like voltage-curves are currently not supported.
        """

        _LOGGER.debug("%s: Received packet: %s", self.name, packet.hex())

        if len(packet) < 3:
            _LOGGER.warn("%s: Packet is too short", self.name)
            return
        if packet[0] != PACKET_MAGIC:
            _LOGGER.warn("%s: Packet does not start with magic number", self.name)
            return

        checksum = sum(packet[0:-1]) & 255
        if packet[-1] != checksum:
            if (
                packet[1] != CMD_GET_VERSION_INFO
            ):  # Version info packets have invalid checksums, looks like a bug in the firmware
                _LOGGER.warn(
                    "%s: Packet checksum (%x) does not match expected checksum (%x)",
                    self.name,
                    packet[-1],
                    checksum,
                )
                return

        if packet[1] == CMD_GET_CHANNEL_DATA:
            (
                channel,
                type,
                mode,
                count,
                status,
                time,
                voltage,
                current,
                capacity,
                temperature,
                resistance,
                leds,
            ) = STRUCT_GET_CHANNEL_DATA.unpack_from(packet, 2)
            if channel >= MC3000_CHANNEL_COUNT:
                _LOGGER.warn(
                    "%s: Received channel data for invalid channel %d",
                    self.name,
                    channel,
                )
                return
            self._state.channels[channel] = Mc3000ChannelData(
                BatteryType(type),
                ChannelMode(mode),
                count,
                ChannelStatus(status),
                time,
                voltage / 1000.0,
                current / 1000.0,
                capacity,
                temperature,
                resistance,
                self._resolve_channel_led(leds, channel),
            )
            return

        elif packet[1] == CMD_GET_VERSION_INFO:
            (
                fw_version_major,
                fw_version_minor,
                hw_version,
            ) = STRUCT_GET_VERSION_INFO.unpack_from(packet, 2)
            self._state.version_info = Mc3000VersionInfo(
                f"{fw_version_major}.{fw_version_minor}",
                f"{hw_version // 10}.{hw_version % 10}",
            )

        elif packet[1] == CMD_GET_BASIC_DATA:
            (
                temp_unit,
                system_beep,
                display,
                screensaver,
                cooling_fan,
                input_voltage,
            ) = STRUCT_GET_BASIC_DATA.unpack_from(packet, 2)
            self._state.basic_data = Mc3000BasicData(
                temp_unit, system_beep, display, screensaver, cooling_fan, input_voltage
            )

        elif packet[1] not in [CMD_START_CHARGE, CMD_STOP_CHARGE]:
            _LOGGER.info("%s: Unknown packet type %d", self.name, packet[1])

    def _resolve_channel_led(self, value: int, channel: int) -> LedColor:
        if (value >> channel) & 1:
            return LedColor.RED
        elif (value >> (channel + MC3000_CHANNEL_COUNT)) & 1:
            return LedColor.GREEN
        return LedColor.OFF
