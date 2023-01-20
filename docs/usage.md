# Usage

To use this package:

- import the package
- search for a compatible device using Bleak
- create a new `Mc3000` instance based on the found `BLEDevice`
- call `update()` to fetch the latest device state
- call `start_charge()` or `stop_charge()` to start or stop charging a battery in one of the four channels (indexed 0-3)

## Example code

```{eval-rst}
.. literalinclude:: ../examples/run.py
   :language: python
   :linenos:
```
