from __future__ import annotations

import asyncio
import logging
from struct import Struct

from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTCharacteristic
from bleak.exc import BleakError

from .const import MC3000_CHANNEL_COUNT, MC3000_CHARACTERISTIC_UUID
from .device import SkyRcDevice
from .models import (
    BatteryType,
    ChannelMode,
    ChannelStatus,
    CoolingFanMode,
    DisplayMode,
    LedColor,
    Mc3000BasicData,
    Mc3000ChannelData,
    Mc3000State,
    TemperatureUnit,
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


class Mc3000(SkyRcDevice[Mc3000State]):

    _model = "MC3000"

    def __init__(self, ble_device: BLEDevice) -> None:
        super().__init__(ble_device)

        self._state = Mc3000State()

    async def connect(self) -> bool:
        """Connect to the device."""
        if result := await super().connect():

            async with self._client_lock:
                await self._client.start_notify(
                    MC3000_CHARACTERISTIC_UUID, self._notification_callback
                )
            await self._send_packet(CMD_GET_VERSION_INFO)

        return result

    async def update(self) -> None:
        """Update the state of the device."""
        await super().update()

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
            try:
                await asyncio.wait_for(self._packet_received.wait(), 2)
            except TimeoutError:
                _LOGGER.warn("%s: Timeout waiting for response notification")

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
                TemperatureUnit(temp_unit),
                system_beep,
                DisplayMode(display),
                screensaver,
                CoolingFanMode(cooling_fan),
                input_voltage / 1000.0,
            )

        elif packet[1] == CMD_GET_VERSION_INFO:
            (
                fw_version_major,
                fw_version_minor,
                hw_version,
            ) = STRUCT_GET_VERSION_INFO.unpack_from(packet, 2)
            self._sw_version = f"{fw_version_major}.{fw_version_minor}"
            self._hw_version = f"{hw_version // 10}.{hw_version % 10}"

        elif packet[1] not in [CMD_START_CHARGE, CMD_STOP_CHARGE]:
            _LOGGER.info("%s: Unknown packet type %d", self.name, packet[1])

    def _resolve_channel_led(self, value: int, channel: int) -> LedColor:
        if (value >> channel) & 1:
            return LedColor.RED
        elif (value >> (channel + MC3000_CHANNEL_COUNT)) & 1:
            return LedColor.GREEN
        return LedColor.OFF
