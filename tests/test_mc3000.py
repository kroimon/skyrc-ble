import pytest
from bleak import BLEDevice

from skyrc_ble import Mc3000
from skyrc_ble.models import (
    BatteryType,
    ChannelMode,
    ChannelStatus,
    CoolingFanMode,
    DisplayMode,
    LedColor,
    Mc3000BasicData,
    Mc3000ChannelData,
    TemperatureUnit,
)


@pytest.mark.asyncio
async def test_mc3000_state(mock_mc3000_bleak):
    ble_device = BLEDevice("00:01:02:03:04:05", "Charger")
    mc3000 = Mc3000(ble_device)

    await mc3000.connect()
    assert mc3000.name == "Charger"
    assert mc3000.address == "00:01:02:03:04:05"
    assert mc3000.hw_version == "2.2"
    assert mc3000.sw_version == "1.15"

    await mc3000.update()
    assert mc3000.state.basic_data == Mc3000BasicData(
        temp_unit=TemperatureUnit.CELSIUS,
        system_beep=False,
        display=DisplayMode.TIME_1MIN,
        screensaver=False,
        cooling_fan=CoolingFanMode.AUTO,
        input_voltage=11.0,
    )
    assert mc3000.state.channels[0] == Mc3000ChannelData(
        type=BatteryType.LIION,
        mode=ChannelMode.CHARGE,
        count=0,
        status=ChannelStatus.STANDBY,
        time=5107,
        voltage=3.642,
        current=0.0,
        capacity=1207,
        temperature=24,
        resistance=27,
        led=LedColor.RED,
    )
    assert mc3000.state.channels[1] == Mc3000ChannelData(
        type=BatteryType.LIION,
        mode=ChannelMode.CHARGE,
        count=0,
        status=ChannelStatus.CHARGE,
        time=54,
        voltage=3.694,
        current=1.001,
        capacity=13,
        temperature=24,
        resistance=25,
        led=LedColor.RED,
    )
    assert mc3000.state.channels[2] == Mc3000ChannelData(
        type=BatteryType.LIION,
        mode=ChannelMode.CHARGE,
        count=0,
        status=ChannelStatus.DONE,
        time=5142,
        voltage=4.154,
        current=0.0,
        capacity=1220,
        temperature=24,
        resistance=30,
        led=LedColor.GREEN,
    )
    assert mc3000.state.channels[3] == Mc3000ChannelData(
        type=BatteryType.LIION,
        mode=ChannelMode.CHARGE,
        count=0,
        status=ChannelStatus.STANDBY,
        time=5452,
        voltage=0.0,
        current=0.0,
        capacity=1211,
        temperature=24,
        resistance=136,
        led=LedColor.OFF,
    )


@pytest.mark.asyncio
async def test_mc3000_start_stop(mock_mc3000_bleak):
    ble_device = BLEDevice("00:01:02:03:04:05", "Charger")
    mc3000 = Mc3000(ble_device)

    await mc3000.connect()

    sent = mc3000._client.packets_sent
    await mc3000.start_charge(0)
    await mc3000.stop_charge(0)
    assert mc3000._client.packets_sent == sent + 2
