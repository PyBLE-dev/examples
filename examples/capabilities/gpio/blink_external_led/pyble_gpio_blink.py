# SPDX-License-Identifier: MIT
"""Blink an externally wired LED, then stop by itself.

Purpose:
    Make a small external LED blink, then stop by itself.
Settings:
    Choose the LED's GPIO number (a numbered board connection) and whether 1
    or 0 turns it on. The blink count and wait time are ready for a first run.
Before you run:
    Ask a teacher or adult to check the pin map and LED circuit for your exact
    board. Turn board power off before changing wires. Never connect an LED
    without a current-limiting resistor.
Prerequisites:
    Use a GPIO that the board guide marks safe as an output. Check its voltage,
    current limit, and whether the board needs it while starting.
Wiring:
    For the simple circuit where 1 means on, connect GPIO -> resistor -> LED ->
    GND (ground). An adult must check the resistor value. A circuit where 0
    means on needs a different, adult-checked recipe.
Try this:
    After one safe run, set BLINK_COUNT to 3 and count three blinks.
Persistent effects:
    No files or settings are left behind.
Expected:
    The LED blinks five times and the console reports completion.
Stop and cleanup:
    Stop may interrupt the sequence; cleanup turns the LED off and leaves the
    pin as an input that does not send power to the circuit.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while a required
# setting is None. Ask a teacher or adult to check your exact board guide.
# Never guess a GPIO number or copy one from a different board.
#
# Complete example only if the guide approves GPIO 7 for this LED circuit:
# LED_PIN = 7
# LED_ACTIVE_LEVEL = 1
# Do not copy 7 unless your exact board guide says to use it.
LED_PIN = None  # Replace with the checked GPIO number.
# For GPIO -> resistor -> LED -> GND, 1 means on.
# Use LED_ACTIVE_LEVEL = 0 only for an adult-checked active-low circuit.
LED_ACTIVE_LEVEL = None

# These lesson settings are ready for the first run.
BLINK_COUNT = 5  # Blink five times; allowed range: 1 to 20.
STEP_DELAY_MS = 250  # Wait one quarter-second after each on/off change.
# END OF SETUP GUIDE
# Later uses of None are safety bookkeeping or mean "no internal pull."
# They are not setup choices. Do not edit the program below.


def validate_pin(name, value):
    """Return a structurally valid, explicitly supplied Pin identifier."""
    if value is None:
        raise ValueError(
            "%s is still None; use the GPIO chosen from your board guide" % name
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


def validate_level(name, value):
    """Return an explicit binary level without accepting bool as an integer."""
    if value is None:
        raise ValueError(
            "%s is still None; use 1 for the wiring shown above or 0 for "
            "a checked active-low circuit" % name
        )
    if isinstance(value, bool) or value not in (0, 1):
        raise ValueError("Set %s to 0 or 1 for the reviewed circuit" % name)
    return value


def validate_config(pin_id, active_level, count, delay_ms):
    """Validate every setting before callers import or construct hardware."""
    pin_id = validate_pin("LED_PIN", pin_id)
    active_level = validate_level("LED_ACTIVE_LEVEL", active_level)
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 20:
        raise ValueError("BLINK_COUNT must be an integer from 1 to 20")
    if (
        isinstance(delay_ms, bool)
        or not isinstance(delay_ms, int)
        or not 50 <= delay_ms <= 2000
    ):
        raise ValueError("STEP_DELAY_MS must be an integer from 50 to 2000")
    if count * 2 * delay_ms > 5_000:
        raise ValueError("the paced blink work must remain within 5 seconds")
    return pin_id, active_level, count, delay_ms


def run_blinks(led, active_level, count, delay_ms, sleep_ms):
    """Run the bounded blink logic against a Pin-like object."""
    inactive_level = 1 - active_level
    for _ in range(count):
        led.value(active_level)
        sleep_ms(delay_ms)
        led.value(inactive_level)
        sleep_ms(delay_ms)


def main():
    """Validate configuration, then run and safely release the output."""
    config = validate_config(
        LED_PIN,
        LED_ACTIVE_LEVEL,
        BLINK_COUNT,
        STEP_DELAY_MS,
    )

    from machine import Pin
    from time import sleep_ms

    pin_id, active_level, count, delay_ms = config
    inactive_level = 1 - active_level
    led = None
    try:
        led = Pin(pin_id, Pin.OUT, value=inactive_level)
        print("Blinking external LED %d times." % count)
        run_blinks(led, active_level, count, delay_ms, sleep_ms)
        print("Blink complete.")
    finally:
        if led is not None:
            try:
                led.value(inactive_level)
            finally:
                led.init(Pin.IN, None)


if __name__ == "__main__":
    main()
