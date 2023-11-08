# Changelog

## v2.1.0 (2023-11-08)

### Feature

- Add functions to start/stop charging multiple channels at once ([`47d0eff`](https://github.com/kroimon/skyrc-ble/commit/47d0eff2c6a67c24be4f22b04131b3ad01bbab2f))

### Documentation

- Switch docs theme to furo ([`4513026`](https://github.com/kroimon/skyrc-ble/commit/451302663edbf01f9aa87570bedb2d29d0ad7348))
- Fix changelog generation ([`f260cd9`](https://github.com/kroimon/skyrc-ble/commit/f260cd93d859fb7b4f2f0638d0cbce48a10e4cd4))

## v2.0.1 (2023-11-08)

### Build

- Update ci workflows ([`eacabd8`](https://github.com/kroimon/skyrc-ble/commit/eacabd8d9ac9f306f0c35804f3e73c836930be26))
- Update dependencies ([`6ae878a`](https://github.com/kroimon/skyrc-ble/commit/6ae878aa2a2c5a2b1001050e154b80efb2da5c99))

### Test

- Fix typeerrors when running tests ([`02091e6`](https://github.com/kroimon/skyrc-ble/commit/02091e689985e7014d5729507b21b64e2f7ab221))

### Style

- Fix formatting ([`4d80e2a`](https://github.com/kroimon/skyrc-ble/commit/4d80e2aa2001e38da89790a386d33b3d9d5208d8))

### Fix

- Send correct channel index to start and stop charging ([`a69fd52`](https://github.com/kroimon/skyrc-ble/commit/a69fd525d7611eaf304261bc2bf9f1433ef0f26d))

## v2.0.0 (2023-01-26)

### Test

- Add tests for mc3000 ([`3e98fed`](https://github.com/kroimon/skyrc-ble/commit/3e98fed4c62b6fc9e73c402f1efa9b9bece60ffb))
- Update test dependencies ([`12c3c79`](https://github.com/kroimon/skyrc-ble/commit/12c3c798cbf34be53799fe3b568674f87aa4af37))

### Fix

- Datatypes in basic state data must be enums ([`e369a32`](https://github.com/kroimon/skyrc-ble/commit/e369a32b1416a25d64ee688a6ca262ef111ed069))

### Feature

- Log timeout when waiting for response ([`b8129d8`](https://github.com/kroimon/skyrc-ble/commit/b8129d8b9dd673fe1fa3e9a1beac4e39d4e737f6))
- Add manufacturer and model properties ([`bf9997e`](https://github.com/kroimon/skyrc-ble/commit/bf9997ed4c2b1575984f20911226d049e06455de))

### Refactor

- Re-order packet parsing for mc3000 ([`5b0fdbb`](https://github.com/kroimon/skyrc-ble/commit/5b0fdbbc5fb107e59d73238e181edbbb26819d68))
- Extract superclass skyrcdevice ([`dae627d`](https://github.com/kroimon/skyrc-ble/commit/dae627d7e51786c1e74c00130fac39b60d75065e))

### Breaking

- Move version info to generic device ([`6ce40d1`](https://github.com/kroimon/skyrc-ble/commit/6ce40d171462f0ce7d843c23aa171ab43471ec67))

## v1.0.0 (2023-01-24)

### Breaking

- Rename/move purely mc3000 related code ([`bc60769`](https://github.com/kroimon/skyrc-ble/commit/bc6076992ffe019d6f35ed329fa91f6563a18a6d))

### Feature

- Add address property to mc3000 class ([`d7c2d3b`](https://github.com/kroimon/skyrc-ble/commit/d7c2d3bbbf3a2019ee634db5f91b59828509f5ca))

## v0.2.0 (2023-01-24)

### Feature

- Allow replacing the bledevice instance ([`6fa18f6`](https://github.com/kroimon/skyrc-ble/commit/6fa18f6c799b986807a2138610155a1fba407452))

### Documentation

- Fix ci badge ([`6732020`](https://github.com/kroimon/skyrc-ble/commit/6732020b2732e963f979444671a5028a1cfc75d8))
- Fix readme include ([`41593f5`](https://github.com/kroimon/skyrc-ble/commit/41593f56f52a57b73fc09d0d64836672442201db))
- Add protocol analysis ([`59fa789`](https://github.com/kroimon/skyrc-ble/commit/59fa789dc98b3fa981a7f4babe68b82b7db592ec))
- Document usage ([`186cae5`](https://github.com/kroimon/skyrc-ble/commit/186cae58744a6708b6812542bc41cf05a3b43101))

## v0.1.0 (2023-01-19)

### Feature

- Initial commit ([`1d91c5a`](https://github.com/kroimon/skyrc-ble/commit/1d91c5a3cab17631147c8cdde7a87057729645fe))

## v2.0.0 (2023-01-26)
### Feature
* Log timeout when waiting for response ([`b8129d8`](https://github.com/kroimon/skyrc-ble/commit/b8129d8b9dd673fe1fa3e9a1beac4e39d4e737f6))
* Add manufacturer and model properties ([`bf9997e`](https://github.com/kroimon/skyrc-ble/commit/bf9997ed4c2b1575984f20911226d049e06455de))

### Fix
* Datatypes in basic state data must be enums ([`e369a32`](https://github.com/kroimon/skyrc-ble/commit/e369a32b1416a25d64ee688a6ca262ef111ed069))

### Breaking
* move version info to generic device ([`6ce40d1`](https://github.com/kroimon/skyrc-ble/commit/6ce40d171462f0ce7d843c23aa171ab43471ec67))

## v1.0.0 (2023-01-24)
### Feature
* Add address property to Mc3000 class ([`d7c2d3b`](https://github.com/kroimon/skyrc-ble/commit/d7c2d3bbbf3a2019ee634db5f91b59828509f5ca))

### Breaking
* rename/move purely MC3000 related code ([`bc60769`](https://github.com/kroimon/skyrc-ble/commit/bc6076992ffe019d6f35ed329fa91f6563a18a6d))

## v0.2.0 (2023-01-24)
### Feature
* Allow replacing the BLEDevice instance ([`6fa18f6`](https://github.com/kroimon/skyrc-ble/commit/6fa18f6c799b986807a2138610155a1fba407452))

### Documentation
* Fix CI badge ([`6732020`](https://github.com/kroimon/skyrc-ble/commit/6732020b2732e963f979444671a5028a1cfc75d8))
* Fix README include ([`41593f5`](https://github.com/kroimon/skyrc-ble/commit/41593f56f52a57b73fc09d0d64836672442201db))
* Add protocol analysis ([`59fa789`](https://github.com/kroimon/skyrc-ble/commit/59fa789dc98b3fa981a7f4babe68b82b7db592ec))
* Document usage ([`186cae5`](https://github.com/kroimon/skyrc-ble/commit/186cae58744a6708b6812542bc41cf05a3b43101))

## v0.1.0 (2023-01-19)
### Feature
* Initial commit ([`1d91c5a`](https://github.com/kroimon/skyrc-ble/commit/1d91c5a3cab17631147c8cdde7a87057729645fe))
