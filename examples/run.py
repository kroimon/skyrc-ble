import asyncio
import logging

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from skyrc_ble import MC3000_BLUETOOTH_NAMES, MC3000_SERVICE_UUID, Mc3000

_LOGGER = logging.getLogger(__name__)


async def run() -> None:
    _LOGGER.info("Searching for device...")

    def filter_mc3000(device: BLEDevice, adv: AdvertisementData) -> bool:
        return (
            device.name in MC3000_BLUETOOTH_NAMES
            and MC3000_SERVICE_UUID in adv.service_uuids
        )

    device = await BleakScanner.find_device_by_filter(filter_mc3000, None)
    _LOGGER.info("Found device: %r", device)

    mc3000 = Mc3000(device)
    await mc3000.connect()
    _LOGGER.info("Hardware version: %s", mc3000.hw_version)
    _LOGGER.info("Software version: %s", mc3000.sw_version)

    await mc3000.update()
    _LOGGER.info("Current state: %r", mc3000.state)

    await mc3000.start_charge(0)

    await mc3000.update()
    _LOGGER.info("Current state: %r", mc3000.state)

    await mc3000.disconnect()


logging.basicConfig(level=logging.INFO)
logging.getLogger("skyrc_ble").setLevel(logging.DEBUG)
asyncio.run(run())
