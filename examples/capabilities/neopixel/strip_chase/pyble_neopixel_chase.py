# SPDX-License-Identifier: MIT
"""Run a short, dim chase on an explicitly configured addressable strip.

Purpose:
    Move one dim amber light along a short addressable-pixel strip, then turn
    every pixel off.
Settings:
    Choose the data GPIO and enter the real number of pixels, from 1 to 32. The
    dim color, two trips, and step time are ready for a first run.
Before you run:
    Ask a teacher or adult to check the exact board guide, strip guide, power
    supply, protection, and data voltage. Turn all power off before changing
    wires. Never power a strip from a GPIO.
Prerequisites:
    Use PyBLE ESP board software with the NeoPixel tool and a GPIO that the
    board guide marks safe for data output. Count pixels and check full power.
Wiring:
    Connect the checked GPIO to the strip's data-in end. Use a suitably rated
    external supply and shared GND (ground). Follow the strip guide for
    protection and any needed data-voltage converter (level shifter).
Try this:
    After one safe run, set CHASE_CYCLES to 1 and watch one trip along the strip.
Persistent effects:
    No files or settings are left behind, and cleanup sends the off color to
    every configured pixel.
Expected:
    One dim amber pixel moves across at most 32 pixels for two cycles.
Stop and cleanup:
    Stop may interrupt the chase; cleanup writes black to the whole strip and
    leaves the data pin as an input that does not send power.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while a required
# setting is None. Ask a teacher or adult to check your exact board and strip
# guides. Never guess a GPIO number or copy one from a different board.
#
# Complete 8-pixel example only if the guide approves GPIO 7 for pixel data:
# PIXEL_PIN = 7
# PIXEL_COUNT = 8
# Do not copy 7 unless your exact board guide says to use it.
PIXEL_PIN = None  # Replace with the checked data-output GPIO number.
# Count the physical pixels and enter the real number.
PIXEL_COUNT = None  # Replace with the real count, from 1 to 32.

# The tuple is (red, green, blue): 0 is off and these values are very dim.
CHASE_COLOR = (8, 2, 0)  # Dim amber.
CHASE_CYCLES = 2  # Move across the strip twice.
STEP_DELAY_MS = 80  # Hold each step for 80 thousandths of a second.
MAX_PIXEL_COUNT = 32  # Fixed safety cap; do not change it.
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
    """Return a deliberately dim RGB tuple."""
    if not isinstance(color, tuple) or len(color) != 3:
        raise ValueError("CHASE_COLOR must be an RGB tuple")
    return tuple(validate_int("RGB channel", channel, 0, 16) for channel in color)


def validate_config(
    pin_id,
    pixel_count,
    color,
    cycles,
    delay_ms,
    max_pixel_count,
):
    """Validate every setting before callers import or construct hardware."""
    pin_id = validate_pin("PIXEL_PIN", pin_id)
    if type(max_pixel_count) is not int or max_pixel_count != 32:
        raise ValueError("MAX_PIXEL_COUNT is a fixed safety cap of 32")
    if pixel_count is None:
        raise ValueError(
            "PIXEL_COUNT is still None; enter the real pixel count from 1 to 32"
        )
    pixel_count = validate_int("PIXEL_COUNT", pixel_count, 1, max_pixel_count)
    color = validate_color(color)
    cycles = validate_int("CHASE_CYCLES", cycles, 1, 5)
    delay_ms = validate_int("STEP_DELAY_MS", delay_ms, 20, 1000)
    if pixel_count * cycles * delay_ms > 6_000:
        raise ValueError("the paced NeoPixel work must remain within 6 seconds")
    return pin_id, pixel_count, color, cycles, delay_ms


def chase_indices(pixel_count, cycles):
    """Return the exact bounded pixel-index sequence for a chase."""
    return tuple(index for _ in range(cycles) for index in range(pixel_count))


def run_chase(pixels, pixel_count, color, cycles, delay_ms, sleep_ms):
    """Run a finite chase against a NeoPixel-like object."""
    for index in chase_indices(pixel_count, cycles):
        pixels.fill((0, 0, 0))
        pixels[index] = color
        pixels.write()
        sleep_ms(delay_ms)


def turn_pixels_off(pixels):
    """Fill a NeoPixel-like object with black and transmit it."""
    pixels.fill((0, 0, 0))
    pixels.write()


def main():
    """Validate configuration, run the chase, and leave every pixel off."""
    config = validate_config(
        PIXEL_PIN,
        PIXEL_COUNT,
        CHASE_COLOR,
        CHASE_CYCLES,
        STEP_DELAY_MS,
        MAX_PIXEL_COUNT,
    )

    from machine import Pin
    from neopixel import NeoPixel
    from time import sleep_ms

    pin_id, pixel_count, color, cycles, delay_ms = config
    pin = None
    pixels = None
    try:
        pin = Pin(pin_id, Pin.OUT, value=0)
        pixels = NeoPixel(pin, pixel_count)
        print("Running a dim chase on %d pixels." % pixel_count)
        run_chase(
            pixels,
            pixel_count,
            color,
            cycles,
            delay_ms,
            sleep_ms,
        )
        print("NeoPixel chase complete.")
    finally:
        try:
            if pixels is not None:
                turn_pixels_off(pixels)
        finally:
            if pin is not None:
                pin.init(Pin.IN, None)


if __name__ == "__main__":
    main()
