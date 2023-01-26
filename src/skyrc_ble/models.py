from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from .const import MC3000_CHANNEL_COUNT


class TemperatureUnit(IntEnum):
    CELSIUS = 0
    FAHRENHEIT = 1


class DisplayMode(IntEnum):
    OFF = 0
    AUTO = 1
    TIME_1MIN = 2
    TIME_2MIN = 3
    TIME_5MIN = 4
    ALWAYS_ON = 5


class CoolingFanMode(IntEnum):
    AUTO = 0
    OFF = 1
    ON = 2
    TEMP_20C = 3
    TEMP_25C = 4
    TEMP_30C = 5
    TEMP_35C = 6
    TEMP_40C = 7
    TEMP_45C = 8
    TEMP_50C = 9


class BatteryType(IntEnum):
    LIION = 0
    LIFE = 1
    LIION_4_35 = 2
    NIMH = 3
    NICD = 4
    NIZN = 5
    ENELOOP = 6
    RAM = 7
    BATLTO = 8


class ChannelMode(IntEnum):
    CHARGE = 0
    REFRESH = 1
    STORAGE = 2  # for LiIon, LiFe, LiIon_4.35
    BREAKIN = 2  # for NiMH, NiCd, NiZn, Eneloop, Ram, Batlto
    DISCHARGE = 3
    CYCLE = 4


class ChannelStatus(IntEnum):
    STANDBY = 0
    CHARGE = 1
    DISCHARGE = 2
    PAUSE = 3
    DONE = 4
    INPUT_VOLTAGE_LOW = 128
    INPUT_VOLTAGE_HIGH = 129
    MCP3424_1_ERROR = 130
    MCP3424_2_ERROR = 131
    CONNECTION_BREAK = 132
    CHECK_VOLTAGE = 133
    CAPACITY_PROTECTION = 134
    TIME_PROTECTION = 135
    TEMP_HIGH = 136
    BATTERY_TEMP_HIGH = 137
    BATTERY_SHORT_CIRCUIT = 138
    REVERSE_POLARITY = 139


class LedColor(IntEnum):
    OFF = 0
    RED = 1
    GREEN = 2


@dataclass(frozen=True)
class Mc3000BasicData:

    temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS
    system_beep: bool = False
    display: DisplayMode = DisplayMode.OFF
    screensaver: bool = False
    cooling_fan: CoolingFanMode = CoolingFanMode.AUTO
    input_voltage: float = 0.0


@dataclass(frozen=True)
class Mc3000ChannelData:

    type: BatteryType = BatteryType.LIION
    mode: ChannelMode = ChannelMode.CHARGE
    count: int = 0
    status: ChannelStatus = ChannelStatus.STANDBY
    time: int = 0
    voltage: float = 0.0
    current: float = 0.0
    capacity: int = 0
    temperature: float = 0.0
    resistance: float = 0.0
    led: LedColor = LedColor.OFF

    def is_working(self) -> bool:
        return self.status in [
            ChannelStatus.CHARGE,
            ChannelStatus.DISCHARGE,
            ChannelStatus.PAUSE,
        ]


@dataclass
class Mc3000State:

    basic_data: Mc3000BasicData | None = None
    channels: list[Mc3000ChannelData | None] = field(
        default_factory=lambda: [None for _ in range(MC3000_CHANNEL_COUNT)]
    )
