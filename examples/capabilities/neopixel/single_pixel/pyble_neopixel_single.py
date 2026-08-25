# SPDX-License-Identifier: MIT
"""Show a short, dim color sequence on one external addressable pixel.

Purpose:
    Show three dim colors on one addressable pixel, then turn it off.
Settings:
    Choose the GPIO connected to the pixel's data-in pin. This lesson always
    uses exactly one pixel; its dim colors and wait time are ready to use.
Before you run:
    Ask a teacher or adult to check the exact board guide, pixel guide, power
    supply, protection, and data voltage. Turn all power off before changing
    wires. Never power the pixel from a GPIO.
Prerequisites:
    Use PyBLE ESP board software with the NeoPixel tool and a GPIO that the
    board guide marks safe for data output. Check the one-pixel power need.
Wiring:
    Connect the checked GPIO to data-in, not data-out. Use a suitable pixel power
    supply and shared GND (ground). Follow the pixel guide for protection and
    any needed data-voltage converter (level shifter).
Try this:
    After one safe run, use DIM_COLORS = ((8, 0, 8),) to show dim purple.
Persistent effects:
    No files or settings are left behind, and cleanup sends the off color.
Expected:
    The one pixel displays dim red, green, and blue, then turns off.
Stop and cleanup:
    Stop may interrupt the sequence; cleanup writes black and leaves the data
    pin as an input that does not send power.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while PIXEL_PIN is
# None. Ask a teacher or adult to check your exact board and pixel guides.
# Never guess a GPIO number or copy one from a different board.
#
# Complete example only if the guide says GPIO 7 is safe for pixel data:
# PIXEL_PIN = 7
# Do not copy 7 unless your exact board guide says to use it.
PIXEL_PIN = None  # Replace with the checked data-output GPIO number.
PIXEL_COUNT = 1  # This lesson controls exactly one physical pixel.

# Each tuple is (red, green, blue): 0 is off and 8 is deliberately dim.
DIM_COLORS = ((8, 0, 0), (0, 8, 0), (0, 0, 8))
COLOR_DELAY_MS = 300  # Show each color for about one third-second.
# END OF SETUP GUIDE
# Later uses of None are safety bookkeeping or mean "no internal pull."
# They are not setup choices. Do not edit the program below.


def validate_pin(name, value):
    """Return a structurally valid, explicitly supplied Pin identifier."""
    if value is None:
        raise ValueError(
            "%s is still None; use the data GPIO chosen from your board guide"
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


def validate_int(name, value, minimum, maximum):
    """Return a bounded integer without accepting bool."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not minimum <= value <= maximum
    ):
        raise ValueError("%s must be from %d to %d" % (name, minimum, maximum))
    return value


def validate_color(color):
    """Return one deliberately dim RGB tuple."""
    if not isinstance(color, tuple) or len(color) != 3:
        raise ValueError("each DIM_COLORS entry must be an RGB tuple")
    return tuple(validate_int("RGB channel", channel, 0, 16) for channel in color)


def validate_config(pin_id, pixel_count, colors, delay_ms):
    """Validate every setting before callers import or construct hardware."""
    pin_id = validate_pin("PIXEL_PIN", pin_id)
    pixel_count = validate_int("PIXEL_COUNT", pixel_count, 1, 1)
    if not isinstance(colors, tuple) or not 1 <= len(colors) <= 8:
        raise ValueError("DIM_COLORS must contain 1 to 8 colors")
    colors = tuple(validate_color(color) for color in colors)
    delay_ms = validate_int("COLOR_DELAY_MS", delay_ms, 20, 2000)
    if len(colors) * delay_ms > 4_000:
        raise ValueError("the paced color work must remain within 4 seconds")
    return pin_id, pixel_count, colors, delay_ms


def show_colors(pixels, colors, delay_ms, sleep_ms):
    """Write a bounded color sequence to a NeoPixel-like object."""
    for color in colors:
        pixels[0] = color
        pixels.write()
        sleep_ms(delay_ms)


def turn_pixels_off(pixels):
    """Fill a NeoPixel-like object with black and transmit it."""
    pixels.fill((0, 0, 0))
    pixels.write()


def main():
    """Validate configuration, show colors, and leave the pixel off."""
    config = validate_config(
        PIXEL_PIN,
        PIXEL_COUNT,
        DIM_COLORS,
        COLOR_DELAY_MS,
    )

    from machine import Pin
    from neopixel import NeoPixel
    from time import sleep_ms

    pin_id, pixel_count, colors, delay_ms = config
    pin = None
    pixels = None
    try:
        pin = Pin(pin_id, Pin.OUT, value=0)
        pixels = NeoPixel(pin, pixel_count)
        print("Showing %d dim colors on one pixel." % len(colors))
        show_colors(pixels, colors, delay_ms, sleep_ms)
        print("Single-pixel sequence complete.")
    finally:
        try:
            if pixels is not None:
                turn_pixels_off(pixels)
        finally:
            if pin is not None:
                pin.init(Pin.IN, None)


if __name__ == "__main__":
    main()
