# SPDX-License-Identifier: MIT
"""Blink the Raspberry Pi Pico 2 W onboard LED a few times.

Purpose:
    Verify the exact Pico 2 W onboard LED with its documented named pin.
Prerequisites:
    A Raspberry Pi Pico 2 W running PyBLE board software named ``rpi-pico2-w``.
Wiring:
    No extra wires are needed. The program uses the small LED built into the
    board through ``machine.Pin("LED")``. Do not replace ``"LED"`` with a
    number.
Settings:
    The three values in SETUP GUIDE choose the blink count and blink speed.
    ``1_000`` milliseconds (ms) equals one second.
Before you run:
    Check that the board name is Raspberry Pi Pico 2 W and that its PyBLE board
    software is named ``rpi-pico2-w``. You do not need to choose a pin.
Try this:
    On a Raspberry Pi Pico 2 W, try ``BLINK_COUNT = 3``. The program checks
    your changes and stops safely if the complete pattern is too long.
Persistent effects:
    No files or settings are saved. The LED finishes off.
Expected:
    The onboard LED blinks five times and the console reports completion.
Stop and cleanup:
    The program turns the LED off when it finishes or when you tap PyBLE Stop.

Validation:
    Built only for the exact Pico 2 W. Physical tests are not recorded yet.
"""

# SETUP GUIDE
# These settings are ready for the Raspberry Pi Pico 2 W. No pin is needed.
# 1_000 milliseconds (ms) is 1 second.
# Example for this exact board: BLINK_COUNT = 3 makes three blinks.
# Keep the count from 1 to 20 and each time from 20 to 2_000 ms.
# The program also keeps the complete blink sequence within 5 seconds.
BLINK_COUNT = 5
ON_TIME_MS = 250
OFF_TIME_MS = 250
# END OF SETUP GUIDE


def blink_steps(count, on_time_ms, off_time_ms):
    """Return validated, finite LED steps for host-side behavior tests."""
    if type(count) is not int or not 1 <= count <= 20:
        raise ValueError("count must be an integer from 1 to 20")
    for name, value in (("on_time_ms", on_time_ms), ("off_time_ms", off_time_ms)):
        if type(value) is not int or not 20 <= value <= 2_000:
            raise ValueError("{} must be 20..2000 milliseconds".format(name))
    if count * (on_time_ms + off_time_ms) > 5_000:
        raise ValueError("the paced blink work must remain within 5 seconds")

    steps = []
    for _ in range(count):
        steps.append((1, on_time_ms))
        steps.append((0, off_time_ms))
    return tuple(steps)


def main():
    """Run the bounded blink sequence and always leave the LED off."""
    steps = blink_steps(BLINK_COUNT, ON_TIME_MS, OFF_TIME_MS)

    from machine import Pin
    from time import sleep_ms

    led = Pin("LED", Pin.OUT, value=0)
    try:
        print("Blinking the Pico 2 W onboard LED {} times.".format(BLINK_COUNT))
        for level, duration_ms in steps:
            led.value(level)
            sleep_ms(duration_ms)
        print("Blink complete; onboard LED is off.")
    finally:
        led.value(0)


if __name__ == "__main__":
    main()
