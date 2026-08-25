# SPDX-License-Identifier: MIT
"""Use an external button to control an external LED for five seconds.

Purpose:
    Turn an external LED on while an external button is pressed.
Settings:
    Choose two different GPIO numbers (numbered board connections) and values
    that match the button and LED circuits. The checks and wait are ready.
Before you run:
    Ask a teacher or adult to check the pin map, resistor, button, and LED for
    your exact board. Turn board power off before changing wires. Use only the
    board's safe logic voltage.
Prerequisites:
    Use two different numeric GPIOs that the board guide marks safe. Check each
    pin's job, current limit, and whether the board needs it while starting.
Wiring:
    The beginner recipe connects button GPIO -> button -> GND and connects LED
    GPIO -> resistor -> LED -> GND. GND means ground. Use different GPIOs.
Try this:
    Hold the button, then release it. Check that the LED follows your hand.
Persistent effects:
    No files or settings are left behind.
Expected:
    For five seconds, the LED is active exactly while the button is pressed.
Stop and cleanup:
    Stop may interrupt the checks; cleanup turns the LED off, disables the
    button pull, and leaves both pins as inputs that do not send power.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while a required
# setting is None. Ask a teacher or adult to check your exact board guide.
# Never guess GPIO numbers or copy them from a different board.
#
# Complete example only if the guide approves GPIO 7 for the button and GPIO 8
# for the LED circuit:
# BUTTON_PIN = 7
# BUTTON_PULL = "up"
# PRESSED_LEVEL = 0
# LED_PIN = 8
# LED_ACTIVE_LEVEL = 1
# Do not copy 7 or 8 unless the exact board guide approves both jobs.
BUTTON_PIN = None  # Replace with the checked numeric input GPIO.
LED_PIN = None  # Replace with a different checked numeric output GPIO.
BUTTON_PULL = None  # Choose "up", "down", or "none" to match the circuit.
PRESSED_LEVEL = None  # Choose 0 or 1 to mean "pressed."
# For the shown LED circuit, 1 means on.
# Use 0 only for an adult-checked active-low LED circuit.
LED_ACTIVE_LEVEL = None
# The quoted word "none" disables the built-in pull and needs an external
# resistor. It is different from Python's unquoted None above.

# These lesson settings are ready for the first run.
SAMPLE_COUNT = 50  # Check the button 50 times.
SAMPLE_INTERVAL_MS = 100  # Wait one tenth-second between checks.
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


def validate_level(name, value):
    """Return an explicit binary level without accepting bool as an integer."""
    if value is None:
        raise ValueError(
            "%s is still None; use 0 or 1 to match the checked circuit" % name
        )
    if isinstance(value, bool) or value not in (0, 1):
        raise ValueError("Set %s to 0 or 1 for the reviewed circuit" % name)
    return value


def validate_config(
    button_pin,
    button_pull,
    pressed_level,
    led_pin,
    led_active_level,
    count,
    interval_ms,
):
    """Validate every setting before callers import or construct hardware."""
    button_pin = validate_pin("BUTTON_PIN", button_pin)
    led_pin = validate_pin("LED_PIN", led_pin)
    if type(button_pin) is not int or type(led_pin) is not int:
        raise ValueError("multi-pin examples require numeric GPIO identifiers")
    if button_pin == led_pin:
        raise ValueError("BUTTON_PIN and LED_PIN must be distinct")
    if button_pull is None:
        raise ValueError(
            'BUTTON_PULL is still None; use "up" for the GPIO-to-GND recipe'
        )
    if button_pull not in ("up", "down", "none"):
        raise ValueError('Set BUTTON_PULL to "up", "down", or "none"')
    pressed_level = validate_level("PRESSED_LEVEL", pressed_level)
    led_active_level = validate_level("LED_ACTIVE_LEVEL", led_active_level)
    if button_pull == "up" and pressed_level != 0:
        raise ValueError("pull-up wiring requires PRESSED_LEVEL = 0")
    if button_pull == "down" and pressed_level != 1:
        raise ValueError("pull-down wiring requires PRESSED_LEVEL = 1")
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 200:
        raise ValueError("SAMPLE_COUNT must be an integer from 1 to 200")
    if (
        isinstance(interval_ms, bool)
        or not isinstance(interval_ms, int)
        or not 20 <= interval_ms <= 1000
    ):
        raise ValueError("SAMPLE_INTERVAL_MS must be from 20 to 1000")
    if (count - 1) * interval_ms > 5_000:
        raise ValueError("paced button and LED work must remain within 5 seconds")
    return (
        button_pin,
        button_pull,
        pressed_level,
        led_pin,
        led_active_level,
        count,
        interval_ms,
    )


def led_level_for_button(raw_level, pressed_level, led_active_level):
    """Return the LED level for one validated button reading."""
    raw_level = validate_level("raw_level", raw_level)
    pressed_level = validate_level("pressed_level", pressed_level)
    led_active_level = validate_level("led_active_level", led_active_level)
    if raw_level == pressed_level:
        return led_active_level
    return 1 - led_active_level


def mirror_button(
    button,
    led,
    pressed_level,
    led_active_level,
    count,
    interval_ms,
    sleep_ms,
):
    """Run the bounded button-to-LED logic with Pin-like objects."""
    for index in range(count):
        led.value(
            led_level_for_button(
                button.value(),
                pressed_level,
                led_active_level,
            )
        )
        if index + 1 < count:
            sleep_ms(interval_ms)


def machine_pull(pin_class, pull):
    """Map a validated pull name to the port's Pin constant."""
    if pull == "up":
        return pin_class.PULL_UP
    if pull == "down":
        return pin_class.PULL_DOWN
    return None


def main():
    """Validate configuration, run the mapping, and release both pins."""
    config = validate_config(
        BUTTON_PIN,
        BUTTON_PULL,
        PRESSED_LEVEL,
        LED_PIN,
        LED_ACTIVE_LEVEL,
        SAMPLE_COUNT,
        SAMPLE_INTERVAL_MS,
    )

    from machine import Pin
    from time import sleep_ms

    (
        button_pin,
        button_pull,
        pressed_level,
        led_pin,
        led_active_level,
        count,
        interval_ms,
    ) = config
    inactive_level = 1 - led_active_level
    button = None
    led = None
    try:
        button = Pin(button_pin, Pin.IN, machine_pull(Pin, button_pull))
        led = Pin(led_pin, Pin.OUT, value=inactive_level)
        print("The button controls the LED for a short, fixed time.")
        mirror_button(
            button,
            led,
            pressed_level,
            led_active_level,
            count,
            interval_ms,
            sleep_ms,
        )
        print("Button and LED example complete.")
    finally:
        try:
            if led is not None:
                try:
                    led.value(inactive_level)
                finally:
                    led.init(Pin.IN, None)
        finally:
            if button is not None:
                button.init(Pin.IN, None)


if __name__ == "__main__":
    main()
