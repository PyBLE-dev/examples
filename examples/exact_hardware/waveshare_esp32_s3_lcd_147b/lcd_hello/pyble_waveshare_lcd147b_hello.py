# SPDX-License-Identifier: MIT
"""Show a short hello picture on the Waveshare ESP32-S3-LCD-1.47B.

Purpose:
    Put a small greeting on the board's built-in screen.
Prerequisites:
    The exact Waveshare ESP32-S3-LCD-1.47B and matching PyBLE board software
    named ``waveshare-esp32-s3-lcd-147b``.
Wiring:
    No extra wires are needed. The built-in screen uses SCLK GPIO40, MOSI
    GPIO45, CS GPIO42, D/C GPIO41, reset GPIO39, and backlight GPIO46. Some of
    these pins help the board start, so never run this on a different board.
Settings:
    ``DISPLAY_HOLD_MS`` says how long the greeting stays visible.
    ``1_000`` milliseconds (ms) equals one second. Do not change any GPIO.
Before you run:
    Read the board label. Run this only on the exact
    ESP32-S3-LCD-1.47B B-version with its matching PyBLE board software.
Try this:
    On that exact board, try ``DISPLAY_HOLD_MS = 2_000`` for a two-second
    greeting, or change the words inside ``"Hello!"`` in ``draw_hello``.
Persistent effects:
    No files or settings are saved. The picture disappears after the screen is
    refreshed or powered off.
Expected:
    A PyBLE greeting is visible for three seconds.
Stop and cleanup:
    The light behind the screen stays off until the picture is ready. The
    program turns it off and releases the screen when it finishes, meets an
    error, or you tap PyBLE Stop.

Validation:
    Built only for the exact LCD-1.47B B-version. Physical tests are not
    recorded yet.
"""

# SETUP GUIDE
# This time setting is only for the exact ESP32-S3-LCD-1.47B B-version.
# 1_000 milliseconds (ms) is 1 second.
# Example for this exact board: DISPLAY_HOLD_MS = 2_000 shows 2 seconds.
# Keep it from 50 to 3_000. Do not change the fixed screen GPIO numbers.
DISPLAY_HOLD_MS = 3_000
# END OF SETUP GUIDE


# FIXED SCREEN SETUP
# The helper code below matches the wires built into the exact board.
# Beginners can leave it unchanged and continue reading at draw_hello().


def validate_hold_ms(value):
    """Keep the visible hold within the catalog runtime budget."""
    if type(value) is not int or not 50 <= value <= 3_000:
        raise ValueError("DISPLAY_HOLD_MS must be 50..3000")
    return value


def _require_exact_board_software():
    """Check the exact board-software marker before touching any GPIO."""
    try:
        import pyble_waveshare_lcd147b
    except ImportError:
        raise RuntimeError(
            "This example requires waveshare-esp32-s3-lcd-147b board software"
        )


def _best_effort_level(pin, level):
    """Set a pin only when setup created it; ignore cleanup-only errors."""
    if pin is not None:
        try:
            pin.value(level)
        except BaseException:
            pass


def _open_display():
    """Build the exact display while keeping its light off during setup."""
    _require_exact_board_software()

    from machine import Pin
    from pyble_st7789 import ST7789, rgb565

    # None means "not made yet" so cleanup knows which pins really exist.
    backlight = None
    chip_select = None
    try:
        backlight = Pin(46, Pin.OUT, value=0)
        chip_select = Pin(42, Pin.OUT, value=1)
        display = ST7789(
            1,
            40_000_000,
            0,
            0,
            Pin(40, Pin.OUT),
            Pin(45, Pin.OUT),
            chip_select,
            Pin(41, Pin.OUT),
            Pin(39, Pin.OUT),
            backlight,
            172,
            320,
            34,
            0,
            True,
            True,
        )
        return display, rgb565
    except BaseException:
        _best_effort_level(chip_select, 1)
        _best_effort_level(backlight, 0)
        raise


def draw_hello(display, rgb565):
    """Draw one picture; x goes across and y goes down from the top left."""
    navy = rgb565(8, 18, 40)
    white = rgb565(255, 255, 255)
    blue = rgb565(45, 91, 255)
    muted = rgb565(148, 163, 184)

    display.fill(navy)
    display.fill_rect(12, 18, 148, 50, blue)
    display.text("PyBLE", 64, 35, white)
    display.text("Hello!", 58, 142, white)
    display.text("LCD-1.47B", 46, 164, muted)
    display.rect(10, 10, 152, 300, muted)


def _close_display(display):
    """Turn off and release a display only when setup created one."""
    if display is not None:
        try:
            display.backlight(False)
        finally:
            display.deinit()


def main():
    """Show the greeting briefly, then release the exact display resources."""
    hold_ms = validate_hold_ms(DISPLAY_HOLD_MS)

    from time import sleep_ms

    # None means "no display yet" and keeps early-error cleanup safe.
    display = None
    try:
        display, rgb565 = _open_display()
        draw_hello(display, rgb565)
        display.show()
        display.backlight(True)
        print("Showing the LCD-1.47B hello frame for {} ms.".format(hold_ms))
        sleep_ms(hold_ms)
    finally:
        _close_display(display)


if __name__ == "__main__":
    main()
