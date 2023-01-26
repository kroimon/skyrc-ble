from __future__ import annotations

import asyncio
import logging
from typing import Generic, TypeVar

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import establish_connection

_LOGGER = logging.getLogger(__name__)
_T = TypeVar("_T")


class SkyRcDevice(Generic[_T]):

    _manufacturer: str = "SkyRC"
    _model: str = "Unknown"

    def __init__(self, ble_device: BLEDevice) -> None:
        """Init the SkyRC device."""
        self._ble_device = ble_device
        self._client: BleakClient = None
        self._client_lock: asyncio.Lock = asyncio.Lock()
        self._packet_received: asyncio.Event = asyncio.Event()
        self._state: _T
        self._hw_version: str = ""
        self._sw_version: str = ""

    def set_ble_device(self, ble_device: BLEDevice) -> None:
        """Update the BLE device."""
        self._ble_device = ble_device

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @property
    def model(self) -> str:
        return self._model

    @property
    def name(self) -> str:
        """Get the name of the device."""
        return self._ble_device.name or self._ble_device.address

    @property
    def address(self) -> str:
        """Get the address of the device."""
        return self._ble_device.address

    @property
    def hw_version(self) -> str:
        """Get the hardware version of the device."""
        return self._hw_version

    @property
    def sw_version(self) -> str:
        """Get the software version of the device."""
        return self._sw_version

    @property
    def is_connected(self) -> bool:
        """Get the connection state."""
        return self._client is not None

    @property
    def state(self) -> _T:
        """Get the state of the device."""
        return self._state

    async def connect(self) -> bool:
        """Connect to the device."""

        if self.is_connected or self._client_lock.locked():
            return False

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

                _LOGGER.debug(
                    "%s: Successfully connected to address %s",
                    self.name,
                    self._ble_device.address,
                )

                return True

            except BleakError:
                _LOGGER.error(
                    "%s: Failed to connect to address %s",
                    self.name,
                    self._ble_device.address,
                )
                self._client = None
                return False

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
