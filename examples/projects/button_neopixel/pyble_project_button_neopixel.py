# SPDX-License-Identifier: MIT
"""Use a configured external button to control a dim NeoPixel strip.

Purpose:
    Make a short strip of color lights glow dim green while a button is held.
Prerequisites:
    PyBLE ESP board software that includes ``neopixel``. Ask a teacher or
    another adult to check the exact board, button, pixel strip, power supply,
    and all five settings before you run the program.
Wiring:
    Use distinct suitable pins, a low-voltage button circuit, shared ground,
    and a correctly powered WS2812-compatible strip. Choose ``"up"``,
    ``"down"``, or ``"none"`` to match the reviewed button circuit. Confirm
    voltage, current, data-signal level, pin ability, and whether either pin
    helps the board start. Never power the strip from a GPIO pin.
Settings:
    The button needs a GPIO number, pull choice, and pressed signal. The strip
    needs a different GPIO number and its real pixel count. RGB means red,
    green, blue; ``(0, 8, 0)`` is a very dim green.
Before you run:
    Turn off all power before changing wires. Check the strip's separate power
    rating, data-signal level, shared ground, and direction arrow. Fill all five
    ``None`` settings; never guess a pin or the number of pixels.
Try this:
    SETUP GUIDE gives one complete, conditional ESP32-DevKitC V4 example. Use
    it only when that exact carrier's guide and the complete circuit agree.
Persistent effects:
    No files or settings are saved. Every pixel finishes off.
Expected:
    The configured strip glows dim green while the button is pressed and is
    otherwise off for an eight-second observation.
Stop and cleanup:
    The program sends the off color, leaves the data pin low, and leaves the
    button as an input when it finishes or when you tap PyBLE Stop.

Validation:
    Written for the four PyBLE ESP board-software types with checked wiring.
    Physical tests are not recorded yet. The Pico board software does not
    include the ``neopixel`` tool.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops before touching a pin.
# Ask a teacher or another adult to check the exact board and circuit.
# Python None has no quote marks. The text "none" has quotes and means that a
# checked external resistor, not the board, holds the button signal steady.
# Use GPIO labels, not header positions. The two GPIO numbers must differ.
# Complete example only for an ESP32-DevKitC V4 with an ESP32-WROOM module,
# after its guide and the pixel power/data circuit have been checked:
# BUTTON_PIN = 25       # Button joins GPIO25 to GND.
# BUTTON_PULL = "up"
# PRESSED_LEVEL = 0
# PIXEL_PIN = 27        # GPIO27 goes to the checked pixel data-input circuit.
# PIXEL_COUNT = 1
# Use a rated strip supply, shared ground, and a level shifter when required.
BUTTON_PIN = None
BUTTON_PULL = None
PRESSED_LEVEL = None
PIXEL_PIN = None
PIXEL_COUNT = None

OBSERVATION_MS = 8_000
POLL_MS = 50
# This fixed cap limits power and memory. Do not increase it.
MAX_PIXELS = 16
# RGB means (red, green, blue); keep every number from 0 to 16.
DIM_ACTIVE_COLOR = (0, 8, 0)
# END OF SETUP GUIDE


def _valid_pin_id(value):
    return (
        type(value) is int
        and 0 <= value <= 255
        or type(value) is str
        and 0 < len(value) <= 32
        and value.strip() == value
    )


def validate_configuration(button_pin, pull, pressed_level, pixel_pin, count):
    """Reject every unset or unsafe configuration before hardware access."""
    if not _valid_pin_id(button_pin):
        raise ValueError("set BUTTON_PIN to a reviewed pin identifier")
    if not _valid_pin_id(pixel_pin):
        raise ValueError("set PIXEL_PIN to a reviewed pin identifier")
    if type(button_pin) is not int or type(pixel_pin) is not int:
        raise ValueError("multi-pin examples require numeric GPIO identifiers")
    if button_pin == pixel_pin:
        raise ValueError("BUTTON_PIN and PIXEL_PIN must be distinct")
    if pull not in ("up", "down", "none"):
        raise ValueError('set BUTTON_PULL to "up", "down", or "none"')
    if type(pressed_level) is not int or pressed_level not in (0, 1):
        raise ValueError("set PRESSED_LEVEL to 0 or 1 for the reviewed circuit")
    if pull == "up" and pressed_level != 0:
        raise ValueError("pull-up wiring requires PRESSED_LEVEL = 0")
    if pull == "down" and pressed_level != 1:
        raise ValueError("pull-down wiring requires PRESSED_LEVEL = 1")
    if type(MAX_PIXELS) is not int or MAX_PIXELS != 16:
        raise ValueError("MAX_PIXELS is a fixed safety cap of 16")
    if type(count) is not int or not 1 <= count <= MAX_PIXELS:
        raise ValueError(
            "set PIXEL_COUNT to an integer from 1 to {}".format(MAX_PIXELS)
        )
    if type(OBSERVATION_MS) is not int or not 1_000 <= OBSERVATION_MS <= 8_000:
        raise ValueError("OBSERVATION_MS must be 1000..8000")
    if type(POLL_MS) is not int or not 20 <= POLL_MS <= 200:
        raise ValueError("POLL_MS must be 20..200")
    validate_dim_color(DIM_ACTIVE_COLOR)
    return button_pin, pull, pressed_level, pixel_pin, count


def validate_dim_color(color):
    """Return one validated, deliberately low-brightness RGB tuple."""
    if type(color) is not tuple or len(color) != 3:
        raise ValueError("DIM_ACTIVE_COLOR must be an RGB tuple")
    for channel in color:
        if type(channel) is not int or not 0 <= channel <= 16:
            raise ValueError("DIM_ACTIVE_COLOR channels must be from 0 to 16")
    return color


def color_for_level(level, pressed_level):
    """Map a digital input level to one low-brightness RGB tuple."""
    if type(level) is not int or level not in (0, 1):
        raise ValueError("button level must be 0 or 1")
    return DIM_ACTIVE_COLOR if level == pressed_level else (0, 0, 0)


def fill_pixels(pixels, count, color):
    """Set and transmit one already-validated color across the strip."""
    for index in range(count):
        pixels[index] = color
    pixels.write()


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
    """Mirror the button on the strip briefly, then force every output off."""
    button_pin, pull, pressed_level, pixel_pin, count = validate_configuration(
        BUTTON_PIN,
        BUTTON_PULL,
        PRESSED_LEVEL,
        PIXEL_PIN,
        PIXEL_COUNT,
    )
    iterations = OBSERVATION_MS // POLL_MS

    from machine import Pin
    from neopixel import NeoPixel
    from time import sleep_ms

    # None means "not created yet" so cleanup knows which objects exist.
    button = None
    data_pin = None
    pixels = None
    try:
        button = Pin(button_pin, Pin.IN, _pin_pull(Pin, pull))
        data_pin = Pin(pixel_pin, Pin.OUT, value=0)
        pixels = NeoPixel(data_pin, count)

        # None here means no color has been sent to the strip yet.
        previous_color = None
        print("Button-to-pixel feedback active for {} ms.".format(OBSERVATION_MS))
        for _ in range(iterations):
            color = color_for_level(button.value(), pressed_level)
            if color != previous_color:
                fill_pixels(pixels, count, color)
                previous_color = color
            sleep_ms(POLL_MS)
        print("Observation complete; strip is off.")
    finally:
        try:
            if pixels is not None:
                fill_pixels(pixels, count, (0, 0, 0))
        finally:
            try:
                if data_pin is not None:
                    data_pin.value(0)
            finally:
                _release_input(button, Pin)


if __name__ == "__main__":
    main()
