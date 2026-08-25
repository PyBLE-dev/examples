# SPDX-License-Identifier: MIT
"""Show a dim sequence on the LCD-1.47B onboard WS2812 pixel.

Purpose:
    Show dim red, green, and blue on the tiny light built into the exact board.
Prerequisites:
    The exact B-version board and matching PyBLE board software named
    ``waveshare-esp32-s3-lcd-147b``. Read the board label, then set
    ``CONFIRM_EXACT_BOARD`` to ``True``.
Wiring:
    No extra wires are needed. The built-in color light uses GPIO38. Seeing
    ``esp32-s3`` in the console does not prove that this is the correct board.
Settings:
    First confirm the board. Each color is ``(red, green, blue)`` and each
    number stays from 0 to 16 for low brightness. ``(0, 0, 0)`` means off.
Before you run:
    Read the physical board label. Continue only if it says
    ESP32-S3-LCD-1.47B and it is the B-version with matching board software.
Try this:
    After that exact-board check, try only blue with
    ``DIM_COLORS = ((0, 0, 8),)``. The final comma is needed.
Persistent effects:
    No files or settings are saved. The color light finishes off.
Expected:
    The onboard pixel shows three dim colors once, then turns off.
Stop and cleanup:
    The program sends the off color and leaves GPIO38 low when it finishes,
    meets an error, or you tap PyBLE Stop.

Validation:
    The software check and your confirmation both happen before GPIO38 is used.
    Physical tests are not recorded yet.
"""

# SETUP GUIDE
# STOP: first read the board label and check the installed PyBLE board software.
# Ask a teacher or another adult to check both with you before you continue.
# False means "do not use GPIO38" and makes the program stop safely.
# Only for the exact ESP32-S3-LCD-1.47B B-version, change False to True:
# CONFIRM_EXACT_BOARD = True
# PIXEL_HOLD_MS is time per color; 1_000 milliseconds (ms) is 1 second.
# Keep each RGB number from 0 to 16 and all colors within 2 seconds.
CONFIRM_EXACT_BOARD = False
PIXEL_HOLD_MS = 500
DIM_COLORS = ((8, 0, 0), (0, 8, 0), (0, 0, 8))
# END OF SETUP GUIDE


def _require_exact_board_confirmation():
    """Check both the board software and the reader's board-label promise."""
    try:
        import pyble_waveshare_lcd147b
    except ImportError:
        raise RuntimeError(
            "This example requires waveshare-esp32-s3-lcd-147b board software"
        )

    if CONFIRM_EXACT_BOARD is not True:
        raise RuntimeError(
            "Verify the LCD-1.47B B-version board, then set "
            "CONFIRM_EXACT_BOARD = True"
        )


def validate_colors(colors, hold_ms):
    """Return a small immutable sequence without touching hardware."""
    if type(hold_ms) is not int or not 50 <= hold_ms <= 2_000:
        raise ValueError("PIXEL_HOLD_MS must be 50..2000")
    if not isinstance(colors, (tuple, list)) or not 1 <= len(colors) <= 8:
        raise ValueError("DIM_COLORS must contain 1..8 colors")

    checked = []
    for color in colors:
        if not isinstance(color, (tuple, list)) or len(color) != 3:
            raise ValueError("each color must have three channels")
        channels = []
        for value in color:
            if type(value) is not int or not 0 <= value <= 16:
                raise ValueError("pixel channels must be integers from 0 to 16")
            channels.append(value)
        checked.append(tuple(channels))
    if len(checked) * hold_ms > 2_000:
        raise ValueError("paced pixel work must remain within 2 seconds")
    return tuple(checked)


def main():
    """Play the confirmed exact-board sequence and always turn the pixel off."""
    colors = validate_colors(DIM_COLORS, PIXEL_HOLD_MS)
    _require_exact_board_confirmation()

    from machine import Pin
    from neopixel import NeoPixel
    from time import sleep_ms

    data_pin = Pin(38, Pin.OUT, value=0)
    # None means "the pixel helper was not made yet" for safe cleanup.
    pixels = None
    try:
        pixels = NeoPixel(data_pin, 1)
        print("Playing a dim sequence on the confirmed LCD-1.47B pixel.")
        for color in colors:
            pixels[0] = color
            pixels.write()
            sleep_ms(PIXEL_HOLD_MS)
    finally:
        try:
            if pixels is not None:
                pixels[0] = (0, 0, 0)
                pixels.write()
        finally:
            data_pin.value(0)


if __name__ == "__main__":
    main()
