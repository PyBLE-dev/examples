# SPDX-License-Identifier: MIT
"""Play a short set of patterns on the Raspberry Pi Pico 2 W onboard LED.

Purpose:
    Compose reusable pattern data and a playback function on the named LED.
Prerequisites:
    A Raspberry Pi Pico 2 W running PyBLE board software named ``rpi-pico2-w``.
Wiring:
    No extra wires are needed. The program uses only the small LED built into
    the board through ``machine.Pin("LED")``.
Settings:
    In each step, ``1`` means LED on, ``0`` means LED off, and the second
    number is the time in milliseconds. ``1_000`` ms equals one second.
Before you run:
    Check that the board is a Raspberry Pi Pico 2 W with the
    ``rpi-pico2-w`` board software. You do not need to choose a pin.
Try this:
    On this exact board, rename ``"long pulse"`` to ``"slow glow"``. Or use
    the one-pattern example shown in SETUP GUIDE.
Persistent effects:
    No files or settings are saved. The LED finishes off.
Expected:
    The LED plays three labeled patterns, then remains off.
Stop and cleanup:
    The program turns the LED off when it finishes, meets an error, or you tap
    PyBLE Stop.

Validation:
    Built only for the exact Pico 2 W. Physical tests are not recorded yet.
"""

# SETUP GUIDE
# Each pattern is (name, steps). Each step is (LED state, time in ms).
# For example, (1, 100) means "LED on for 100 milliseconds".
# A complete one-pattern example for this exact Pico 2 W is:
# PATTERNS = (("quick flash", ((1, 100), (0, 300))),)
# Keep 1 to 8 patterns, 1 to 12 steps each, and at most 4 seconds total.
PATTERNS = (
    ("short pulses", ((1, 100), (0, 150), (1, 100), (0, 500))),
    ("long pulse", ((1, 700), (0, 400))),
    ("double pulse", ((1, 180), (0, 180), (1, 180), (0, 400))),
)
# END OF SETUP GUIDE


def validate_patterns(patterns):
    """Validate and return immutable, bounded pattern data."""
    if not isinstance(patterns, (tuple, list)) or not 1 <= len(patterns) <= 8:
        raise ValueError("patterns must contain 1..8 entries")

    checked = []
    total_ms = 0
    for name, steps in patterns:
        if type(name) is not str or not name or len(name) > 32:
            raise ValueError("each pattern needs a short name")
        if not isinstance(steps, (tuple, list)) or not 1 <= len(steps) <= 12:
            raise ValueError("each pattern needs 1..12 steps")
        checked_steps = []
        for level, duration_ms in steps:
            if type(level) is not int or level not in (0, 1):
                raise ValueError("LED levels must be 0 or 1")
            if type(duration_ms) is not int or not 20 <= duration_ms <= 2_000:
                raise ValueError("step duration must be 20..2000 milliseconds")
            total_ms += duration_ms
            checked_steps.append((level, duration_ms))
        checked.append((name, tuple(checked_steps)))

    if total_ms > 4_000:
        raise ValueError("paced pattern work must last at most 4 seconds")
    return tuple(checked)


def play_pattern(led, sleep_ms, steps):
    """Play one already-validated sequence using injected hardware seams."""
    for level, duration_ms in steps:
        led.value(level)
        sleep_ms(duration_ms)


def main():
    """Play each pattern once and always leave the named LED off."""
    patterns = validate_patterns(PATTERNS)

    from machine import Pin
    from time import sleep_ms

    led = Pin("LED", Pin.OUT, value=0)
    try:
        for name, steps in patterns:
            print("Pattern: {}".format(name))
            play_pattern(led, sleep_ms, steps)
        print("Patterns complete; onboard LED is off.")
    finally:
        led.value(0)


if __name__ == "__main__":
    main()
