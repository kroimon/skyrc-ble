from __future__ import annotations

__version__ = "2.0.0"

from .const import (
    MC3000_BLUETOOTH_NAMES,
    MC3000_CHANNEL_COUNT,
    MC3000_CHARACTERISTIC_UUID,
    MC3000_SERVICE_UUID,
)
from .device import SkyRcDevice
from .mc3000 import Mc3000, Mc3000BasicData, Mc3000ChannelData, Mc3000State

__all__ = [
    "SkyRcDevice",
    "MC3000_BLUETOOTH_NAMES",
    "MC3000_SERVICE_UUID",
    "MC3000_CHARACTERISTIC_UUID",
    "MC3000_CHANNEL_COUNT",
    "Mc3000",
    "Mc3000BasicData",
    "Mc3000ChannelData",
    "Mc3000State",
]
