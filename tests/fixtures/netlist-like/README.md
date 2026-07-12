# Synthetic label-heavy fixture

`connectivity.json` is the only authoritative electrical source. No editable
schematic exists. The desired review drawing should show local power,
programming, sensor, and indicator relationships without changing connectivity.

Product description: a 3.3 V microcontroller reads an I2C temperature sensor,
is programmed through a four-pin header, and drives one status LED. The input
connector supplies 5 V to an LDO. Interface rate, current budget, exact packages,
and protection requirements are not specified.
