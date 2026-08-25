# SPDX-License-Identifier: MIT
"""Count external button presses for ten seconds without double-counting.

Purpose:
    Count real button presses without counting the tiny shakes inside a button.
Prerequisites:
    Ask a teacher or another adult to check the board guide and circuit. Then
    set ``BUTTON_PIN``, ``BUTTON_PULL``, and ``PRESSED_LEVEL``.
Wiring:
    Use a low-voltage momentary button and a shared ground. Choose ``"up"``
    with a button to ground, ``"down"`` with a button to the board logic
    supply, or ``"none"`` only with a suitable external pull resistor. Never
    apply 5 V; check pin ability and avoid pins that help the board start.
Settings:
    ``BUTTON_PIN`` is the GPIO/GP label, not the metal header-pin position.
    ``BUTTON_PULL`` chooses a built-in resistor. ``PRESSED_LEVEL`` says which
    signal, 0 or 1, means pressed.
Before you run:
    Turn off board power before changing wires. Check every wire, use only the
    board's logic voltage, share ground, and fill all three ``None`` settings.
Try this:
    SETUP GUIDE shows one complete Raspberry Pi Pico 2 W example using GP15.
    Use it only on that named board with a button from GP15 to GND.
Persistent effects:
    No files or settings are saved. The selected pin is used only as an input.
Expected:
    Debounced presses are counted for ten seconds. The first 12 are reported
    individually, then output is suppressed until the final total.
Stop and cleanup:
    The program checks the button for a fixed time. When it finishes or you tap
    Stop, it leaves the button pin as an input with no built-in pull resistor.

Validation:
    Written for all five PyBLE board-software types with checked wiring.
    Physical tests are not recorded yet.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops before touching a pin.
# Python None has no quote marks. The text "none" has quotes and means that a
# checked external resistor, not the board, holds the button signal steady.
# Use the GPIO/GP label from the board guide, not the header-pin position.
# Complete example only for a Raspberry Pi Pico 2 W, button GP15 to GND:
# BUTTON_PIN = 15
# BUTTON_PULL = "up"
# PRESSED_LEVEL = 0
# Ask a teacher or another adult to check the board and wires before Run.
BUTTON_PIN = None
BUTTON_PULL = None
PRESSED_LEVEL = None

# 10_000 ms is 10 seconds. Debouncing waits through tiny contact shakes.
OBSERVATION_MS = 10_000
POLL_MS = 20
DEBOUNCE_MS = 60
# This is a fixed console-output safety limit. Do not increase it.
MAX_REPORTED_PRESSES = 12
# END OF SETUP GUIDE


def _valid_pin_id(value):
    return (
        type(value) is int
        and 0 <= value <= 255
        or type(value) is str
        and 0 < len(value) <= 32
        and value.strip() == value
    )


def validate_configuration(pin_id, pull, pressed_level):
    """Reject every unset or malformed hardware choice before construction."""
    if not _valid_pin_id(pin_id):
        raise ValueError("set BUTTON_PIN to a reviewed pin identifier")
    if pull not in ("up", "down", "none"):
        raise ValueError('set BUTTON_PULL to "up", "down", or "none"')
    if type(pressed_level) is not int or pressed_level not in (0, 1):
        raise ValueError("set PRESSED_LEVEL to 0 or 1 for the reviewed circuit")
    if pull == "up" and pressed_level != 0:
        raise ValueError("pull-up wiring requires PRESSED_LEVEL = 0")
    if pull == "down" and pressed_level != 1:
        raise ValueError("pull-down wiring requires PRESSED_LEVEL = 1")
    if type(OBSERVATION_MS) is not int or not 1_000 <= OBSERVATION_MS <= 10_000:
        raise ValueError("OBSERVATION_MS must be 1000..10000")
    if type(POLL_MS) is not int or not 20 <= POLL_MS <= 100:
        raise ValueError("POLL_MS must be 20..100")
    if type(DEBOUNCE_MS) is not int or not POLL_MS <= DEBOUNCE_MS <= 500:
        raise ValueError("DEBOUNCE_MS must be between POLL_MS and 500")
    if MAX_REPORTED_PRESSES != 12:
        raise ValueError("MAX_REPORTED_PRESSES is a fixed output cap of 12")
    return pin_id, pull, pressed_level


def debounce_step(sample, last_sample, stable_sample, run_length, needed):
    """Accept a new button state only after it stays steady long enough."""
    if type(sample) is not int or sample not in (0, 1):
        raise ValueError("button samples must be 0 or 1")
    if sample == last_sample:
        run_length = min(run_length + 1, needed)
    else:
        last_sample = sample
        run_length = 1

    changed = run_length >= needed and sample != stable_sample
    if changed:
        stable_sample = sample
    return last_sample, stable_sample, run_length, changed


def press_report(press_count):
    """Return one capped progress message, or ``None`` after suppression."""
    if type(press_count) is not int or press_count < 1:
        raise ValueError("press_count must be a positive integer")
    if press_count <= MAX_REPORTED_PRESSES:
        return "Press {}".format(press_count)
    if press_count == MAX_REPORTED_PRESSES + 1:
        return "Further presses are counted without per-press output."
    return None


def _pin_pull(Pin, pull):
    """Turn the simple setting word into a MicroPython pull choice."""
    if pull == "up":
        return Pin.PULL_UP
    if pull == "down":
        return Pin.PULL_DOWN
    # None here means "do not turn on a built-in pull resistor".
    return None


def _release_input(button, Pin):
    """Release a button only when one was created during setup."""
    if button is not None:
        # pull=None removes the built-in pull resistor during cleanup.
        button.init(mode=Pin.IN, pull=None)


def main():
    """Count stable pressed transitions and stop after the fixed observation."""
    pin_id, pull, pressed_level = validate_configuration(
        BUTTON_PIN, BUTTON_PULL, PRESSED_LEVEL
    )
    needed = (DEBOUNCE_MS + POLL_MS - 1) // POLL_MS

    from machine import Pin
    from time import sleep_ms, ticks_diff, ticks_ms

    # None means "no button object yet" and keeps early-error cleanup safe.
    button = None
    try:
        button = Pin(pin_id, Pin.IN, _pin_pull(Pin, pull))
        last_sample = button.value()
        stable_sample = last_sample
        run_length = needed
        press_count = 0
        seconds = OBSERVATION_MS // 1_000
        print("Counting debounced presses for {} seconds.".format(seconds))
        started_ms = ticks_ms()

        while ticks_diff(ticks_ms(), started_ms) < OBSERVATION_MS:
            sleep_ms(POLL_MS)
            sample = button.value()
            last_sample, stable_sample, run_length, changed = debounce_step(
                sample, last_sample, stable_sample, run_length, needed
            )
            if changed and stable_sample == pressed_level:
                press_count += 1
                message = press_report(press_count)
                if message is not None:
                    print(message)

        print("Finished with {} debounced presses.".format(press_count))
    finally:
        _release_input(button, Pin)


if __name__ == "__main__":
    main()
