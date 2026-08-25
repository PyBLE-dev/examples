# SPDX-License-Identifier: MIT
"""Scan one explicitly configured software I2C bus.

Purpose:
    Find the address of a connected I2C device. SDA is the data wire, and SCL
    is the clock wire.
Settings:
    Choose two different GPIO numbers (numbered board connections) and a bus
    speed that every device supports. The short timeout is ready for a run.
Before you run:
    Ask a teacher or adult to check the board pin map, every device guide, logic
    voltage, and pull-up resistors. Turn all power off before changing wires.
Prerequisites:
    Use two numeric GPIOs that the exact board guide marks safe for software
    I2C. Check voltage, current, speed, and whether the board needs either pin
    while starting.
Wiring:
    Connect each checked SDA and SCL wire to the matching device wire. Suitable
    pull-up resistors gently hold both wires high. All parts share GND (ground).
Try this:
    Run once and write down the address, such as 0x3C, shown in the console.
Persistent effects:
    No files or settings are left behind. Scanning does not intentionally
    change a device's stored settings.
Expected:
    One scan prints either no devices or a short list such as 0x3C.
Stop and cleanup:
    Stop may interrupt the scan; cleanup leaves both wires as inputs that do
    not send power. The final pin step performs the needed cleanup.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while a required
# setting is None. Ask a teacher or adult to check your exact board guide.
# Never guess GPIO numbers or copy them from a different board.
#
# Complete example only if the guide approves GPIO 7 for SDA and GPIO 8 for SCL:
# SDA_PIN = 7
# SCL_PIN = 8
# I2C_FREQUENCY_HZ = 100_000
# Do not copy these values unless the board and device guides approve them.
# The two GPIO numbers must be different.
SDA_PIN = None  # Replace with the checked numeric data-wire GPIO.
SCL_PIN = None  # Replace with the checked numeric clock-wire GPIO.
I2C_FREQUENCY_HZ = None

# This safety timeout is ready for the first run.
I2C_TIMEOUT_US = 1_000  # One thousand microseconds is one millisecond.
# END OF SETUP GUIDE
# Later uses of None are safety bookkeeping or mean "no internal pull."
# They are not setup choices. Do not edit the program below.


def validate_pin(name, value):
    """Return a structurally valid, explicitly supplied Pin identifier."""
    if value is None:
        raise ValueError(
            "%s is still None; use the numeric GPIO chosen from your board guide"
            % name
        )
    if isinstance(value, bool):
        raise ValueError("%s must not be a boolean" % name)
    if isinstance(value, int):
        if value < 0 or value > 255:
            raise ValueError("%s must be between 0 and 255" % name)
        return value
    if isinstance(value, str):
        if not value or value != value.strip() or len(value) > 32:
            raise ValueError("%s must be a short, nonblank Pin name" % name)
        return value
    raise ValueError("%s must be an integer or Pin name" % name)


def validate_frequency(value):
    """Return a deliberately bounded, explicitly supplied I2C frequency."""
    if value is None:
        raise ValueError(
            "I2C_FREQUENCY_HZ is still None; if every device allows it, "
            "use 100_000"
        )
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 10000 <= value <= 400000
    ):
        raise ValueError("Set I2C_FREQUENCY_HZ from 10000 to 400000")
    return value


def validate_timeout(value):
    """Keep every SCL-release clock-stretch wait bounded during the scan."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 100 <= value <= 1_000
    ):
        raise ValueError("I2C_TIMEOUT_US must be from 100 to 1000")
    return value


def validate_config(sda_pin, scl_pin, frequency_hz, timeout_us):
    """Validate every setting before callers import or construct hardware."""
    sda_pin = validate_pin("SDA_PIN", sda_pin)
    scl_pin = validate_pin("SCL_PIN", scl_pin)
    if type(sda_pin) is not int or type(scl_pin) is not int:
        raise ValueError("multi-pin examples require numeric GPIO identifiers")
    if sda_pin == scl_pin:
        raise ValueError("SDA_PIN and SCL_PIN must be distinct")
    return (
        sda_pin,
        scl_pin,
        validate_frequency(frequency_hz),
        validate_timeout(timeout_us),
    )


def format_addresses(addresses):
    """Validate and format the bounded result returned by I2C.scan()."""
    if len(addresses) > 112:
        raise ValueError("an I2C scan cannot return more than 112 addresses")
    formatted = []
    for address in addresses:
        if (
            isinstance(address, bool)
            or not isinstance(address, int)
            or not 0x08 <= address <= 0x77
        ):
            raise ValueError("scan returned an invalid 7-bit I2C address")
        formatted.append("0x%02X" % address)
    return ", ".join(formatted)


def scan_once(bus):
    """Perform one bounded scan through an I2C-like object."""
    return tuple(bus.scan())


def main():
    """Validate configuration, scan once, and release both bus pins."""
    config = validate_config(
        SDA_PIN,
        SCL_PIN,
        I2C_FREQUENCY_HZ,
        I2C_TIMEOUT_US,
    )

    from machine import Pin, SoftI2C

    sda_id, scl_id, frequency_hz, timeout_us = config
    sda = None
    scl = None
    bus = None
    try:
        sda = Pin(sda_id)
        scl = Pin(scl_id)
        bus = SoftI2C(
            sda=sda,
            scl=scl,
            freq=frequency_hz,
            timeout=timeout_us,
        )
        addresses = scan_once(bus)
        if addresses:
            print("I2C devices: %s" % format_addresses(addresses))
        else:
            print("No I2C devices responded.")
        print("I2C scan complete.")
    finally:
        # Qualified SoftI2C exposes no portable deinit; release its Pin objects.
        try:
            if sda is not None:
                sda.init(Pin.IN, None)
        finally:
            if scl is not None:
                scl.init(Pin.IN, None)


if __name__ == "__main__":
    main()
