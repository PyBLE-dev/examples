# SPDX-License-Identifier: MIT
"""Read an externally wired push button for a short, fixed time.

Purpose:
    Tell you when an external push button is pressed or released.
Settings:
    Choose the button's GPIO number (a numbered board connection), pull
    direction, and pressed level. The readings and wait are ready for a run.
Before you run:
    Ask a teacher or adult to check the pin map and button circuit for your
    exact board. Turn board power off before changing wires. Use only the
    board's safe logic voltage, never a guessed supply voltage.
Prerequisites:
    Use a GPIO that the board guide marks safe as an input. Check its startup
    jobs and whether it supports the pull direction used by the circuit.
Wiring:
    The beginner recipe connects the button between GPIO and GND, uses the
    board's internal pull-up, and reads 0 when pressed. An adult must check a
    pull-down or external-resistor circuit. All parts must share GND (ground).
Try this:
    Press and release the button slowly. Watch the words change in the console.
Persistent effects:
    No files or settings are left behind.
Expected:
    The console reports the initial state and subsequent transitions for about
    four seconds.
Stop and cleanup:
    Stop may interrupt the readings; cleanup disables the internal pull and
    leaves the pin as an input that does not send power to the circuit.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while a required
# setting is None. Ask a teacher or adult to check your exact board guide.
# Never guess a GPIO number or copy one from a different board.
#
# Complete example only if the guide approves GPIO 7 for a button to GND:
# BUTTON_PIN = 7
# BUTTON_PULL = "up"
# PRESSED_LEVEL = 0
# Do not copy 7 unless your exact board guide says to use it.
BUTTON_PIN = None  # Replace with the checked input GPIO number.
BUTTON_PULL = None  # Choose "up", "down", or "none" to match the circuit.
PRESSED_LEVEL = None  # Choose 0 or 1 to mean "pressed."
# The quoted word "none" disables the built-in pull and needs an external
# resistor. It is different from Python's unquoted None above.

# These lesson settings are ready for the first run.
SAMPLE_COUNT = 16  # Look at the button 16 times.
SAMPLE_INTERVAL_MS = 200  # Wait one fifth-second between looks.
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
            "%s is still None; use 0 or 1 to match the button wiring" % name
        )
    if isinstance(value, bool) or value not in (0, 1):
        raise ValueError("Set %s to 0 or 1 for the reviewed circuit" % name)
    return value


def validate_config(pin_id, pull, pressed_level, count, interval_ms):
    """Validate every setting before callers import or construct hardware."""
    pin_id = validate_pin("BUTTON_PIN", pin_id)
    if pull is None:
        raise ValueError(
            'BUTTON_PULL is still None; use "up" for the GPIO-to-GND recipe'
        )
    if pull not in ("up", "down", "none"):
        raise ValueError('Set BUTTON_PULL to "up", "down", or "none"')
    pressed_level = validate_level("PRESSED_LEVEL", pressed_level)
    if pull == "up" and pressed_level != 0:
        raise ValueError("pull-up wiring requires PRESSED_LEVEL = 0")
    if pull == "down" and pressed_level != 1:
        raise ValueError("pull-down wiring requires PRESSED_LEVEL = 1")
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 100:
        raise ValueError("SAMPLE_COUNT must be an integer from 1 to 100")
    if (
        isinstance(interval_ms, bool)
        or not isinstance(interval_ms, int)
        or not 20 <= interval_ms <= 2000
    ):
        raise ValueError("SAMPLE_INTERVAL_MS must be from 20 to 2000")
    # PyBLE receives a print body and its newline as two physical writes. Count
    # the worst case: every sample transitions, plus the start and final lines.
    console_writes = 2 * (count + 2)
    paced_ms = (count - 1) * interval_ms + (console_writes - 1) * 40
    if paced_ms > 5_000:
        raise ValueError("paced button output must remain within 5 seconds")
    return pin_id, pull, pressed_level, count, interval_ms


def is_pressed(raw_level, pressed_level):
    """Convert a raw binary reading into a logical button state."""
    raw_level = validate_level("raw_level", raw_level)
    pressed_level = validate_level("pressed_level", pressed_level)
    return raw_level == pressed_level


def observe_button(button, pressed_level, count, interval_ms, sleep_ms, emit):
    """Sample a Pin-like input and emit only state transitions."""
    previous = None
    for index in range(count):
        current = is_pressed(button.value(), pressed_level)
        if current != previous:
            emit("Button pressed." if current else "Button released.")
            previous = current
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
    """Validate configuration, then observe and safely release the input."""
    config = validate_config(
        BUTTON_PIN,
        BUTTON_PULL,
        PRESSED_LEVEL,
        SAMPLE_COUNT,
        SAMPLE_INTERVAL_MS,
    )

    from machine import Pin
    from time import sleep_ms

    pin_id, pull, pressed_level, count, interval_ms = config
    button = None
    try:
        button = Pin(pin_id, Pin.IN, machine_pull(Pin, pull))
        print("Watching the button for a short, fixed time.")
        observe_button(
            button,
            pressed_level,
            count,
            interval_ms,
            sleep_ms,
            print,
        )
        print("Button observation complete.")
    finally:
        if button is not None:
            button.init(Pin.IN, None)


if __name__ == "__main__":
    main()
