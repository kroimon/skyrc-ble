"""Session fixtures."""

import asyncio
from typing import Any, Awaitable, Callable
from unittest import mock

import pytest
from bleak import BleakGATTCharacteristic

from skyrc_ble.mc3000 import (
    CMD_GET_BASIC_DATA,
    CMD_GET_CHANNEL_DATA,
    CMD_GET_VERSION_INFO,
    CMD_START_CHARGE,
    CMD_STOP_CHARGE,
)


class MockMc3000BleakClient:
    """Mock BleakClient."""

    def __init__(self, *args, **kwargs):
        """Mock BleakClient."""
        self.packets_sent: int = 0

    async def connect(self, *args, **kwargs):
        """Mock BleakClient.connect."""

    async def disconnect(self, *args, **kwargs):
        """Mock BleakClient.disconnect."""

    async def start_notify(
        self,
        char_specifier: str,
        callback: Callable[[BleakGATTCharacteristic, bytearray], Awaitable[None]],
        **kwargs: Any,
    ) -> None:
        """Mock BleakClient.start_notify."""

        def wrapped_callback(data):
            asyncio.ensure_future(callback(None, data))

        self._callback = wrapped_callback

    async def write_gatt_char(
        self, char_specifier: str, data: bytes, response: bool = False
    ) -> None:
        """Mock BleakClient.write_gatt_char."""

        if data[1] == CMD_GET_VERSION_INFO:
            value = bytearray.fromhex("0f57003130303038330100000000010f1600adfc")
        elif data[1] == CMD_GET_BASIC_DATA:
            value = bytearray.fromhex("0f6100000200002af80000000000000000000094")
        elif data[1] == CMD_GET_CHANNEL_DATA and data[2] == 0:
            value = bytearray.fromhex("0f55000000000013f30e3a000004b718001b07a7")
        elif data[1] == CMD_GET_CHANNEL_DATA and data[2] == 1:
            value = bytearray.fromhex("0f55010000000100360e6e03e9000d1800190749")
        elif data[1] == CMD_GET_CHANNEL_DATA and data[2] == 2:
            value = bytearray.fromhex("0f5502000000041416103a000004c418001e704c")
        elif data[1] == CMD_GET_CHANNEL_DATA and data[2] == 3:
            value = bytearray.fromhex("0f550300000000154c0000000004bb1800887097")
        elif data[1] == CMD_START_CHARGE and data[2] == 1:
            value = bytearray.fromhex("0f05010000000000000000000000000000000015")
        elif data[1] == CMD_STOP_CHARGE and data[2] == 1:
            value = bytearray.fromhex("0ffe01f0ffff00000000000000000000000000fc")
        else:
            value = bytearray([0])

        self.packets_sent += 1

        asyncio.get_running_loop().call_soon(self._callback, value)
        await asyncio.sleep(0)


@pytest.fixture()
def mock_mc3000_bleak():
    """Mock BleakClient."""

    with mock.patch("skyrc_ble.device.BleakClient", MockMc3000BleakClient):
        yield
