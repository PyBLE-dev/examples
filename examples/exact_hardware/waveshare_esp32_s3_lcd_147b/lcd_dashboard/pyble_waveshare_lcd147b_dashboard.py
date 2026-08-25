# SPDX-License-Identifier: MIT
"""Refresh a small runtime dashboard on the ESP32-S3-LCD-1.47B.

Purpose:
    Show elapsed time, unused working memory, and progress on the built-in
    screen. No sensor is needed.
Prerequisites:
    The exact Waveshare ESP32-S3-LCD-1.47B and matching PyBLE board software
    named ``waveshare-esp32-s3-lcd-147b``.
Wiring:
    No extra wires are needed. The built-in screen uses SCLK GPIO40, MOSI
    GPIO45, CS GPIO42, D/C GPIO41, reset GPIO39, and backlight GPIO46. Some of
    these pins help the board start, so never run this on a different board.
Settings:
    ``FRAME_COUNT`` is the number of pictures. ``FRAME_INTERVAL_MS`` is the
    wait between pictures. ``1_000`` milliseconds (ms) equals one second.
Before you run:
    Read the board label. Run this only on the exact
    ESP32-S3-LCD-1.47B B-version with its matching PyBLE board software.
Try this:
    On that exact board, try three pictures with a one-second wait by using
    ``FRAME_COUNT = 3`` and ``FRAME_INTERVAL_MS = 1_000``.
Persistent effects:
    No files or settings are saved. The screen finishes dark.
Expected:
    Five pictures show run time, unused working memory, and a progress bar.
Stop and cleanup:
    The program shows a fixed number of pictures, then turns the screen light
    off and releases the screen. The same cleanup runs when you tap Stop.

Validation:
    Built only for the exact LCD-1.47B B-version. Physical tests are not
    recorded yet.
"""

# SETUP GUIDE
# These settings are only for the exact ESP32-S3-LCD-1.47B B-version.
# FRAME_COUNT is the number of pictures; FRAME_INTERVAL_MS is the wait.
# Example for this exact board: 3 pictures, each followed by a 1-second wait.
# FRAME_COUNT = 3
# FRAME_INTERVAL_MS = 1_000
# Keep 1 to 10 pictures and waits from 100 to 2_000 ms.
# Together, all waits must add up to 4_000 ms or less.
FRAME_COUNT = 5
FRAME_INTERVAL_MS = 800
# END OF SETUP GUIDE


# FIXED SCREEN SETUP
# The helper code below matches the wires built into the exact board.
# Beginners can leave it unchanged and continue at dashboard_values().


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


def dashboard_values(frame_number, elapsed_ms, free_bytes):
    """Make three short lines; free bytes are unused working-memory bytes."""
    for name, value in (
        ("frame_number", frame_number),
        ("elapsed_ms", elapsed_ms),
        ("free_bytes", free_bytes),
    ):
        if type(value) is not int or value < 0:
            raise ValueError("{} must be a non-negative integer".format(name))
    return (
        "Frame {}/{}".format(frame_number, FRAME_COUNT),
        "Elapsed: {} ms".format(elapsed_ms),
        "Free: {} B".format(free_bytes),
    )


def draw_dashboard(display, rgb565, lines, progress_width):
    """Draw one picture; x goes across and y goes down from the top left."""
    navy = rgb565(8, 18, 40)
    white = rgb565(255, 255, 255)
    blue = rgb565(45, 91, 255)
    green = rgb565(34, 197, 94)
    muted = rgb565(148, 163, 184)

    display.fill(navy)
    display.fill_rect(0, 0, 172, 44, blue)
    display.text("PyBLE DASHBOARD", 24, 18, white)
    display.text(lines[0], 18, 92, white)
    display.text(lines[1], 18, 126, muted)
    display.text(lines[2], 18, 160, muted)
    display.rect(10, 250, 152, 24, white)
    display.fill_rect(11, 251, progress_width, 22, green)
    display.text("runtime data only", 20, 292, muted)


def _close_display(display):
    """Turn off and release a display only when setup created one."""
    if display is not None:
        try:
            display.backlight(False)
        finally:
            display.deinit()


def main():
    """Show five paced runtime frames, then release all display resources."""
    if type(FRAME_COUNT) is not int or not 1 <= FRAME_COUNT <= 10:
        raise ValueError("FRAME_COUNT must be 1..10")
    if type(FRAME_INTERVAL_MS) is not int or not 100 <= FRAME_INTERVAL_MS <= 2_000:
        raise ValueError("FRAME_INTERVAL_MS must be 100..2000")
    if FRAME_COUNT * FRAME_INTERVAL_MS > 4_000:
        raise ValueError("paced dashboard work must remain within 4 seconds")

    import gc
    from time import sleep_ms, ticks_diff, ticks_ms

    # None means "no display yet" and keeps early-error cleanup safe.
    display = None
    started_ms = ticks_ms()
    try:
        display, rgb565 = _open_display()
        for index in range(FRAME_COUNT):
            gc.collect()
            elapsed_ms = ticks_diff(ticks_ms(), started_ms)
            lines = dashboard_values(index + 1, elapsed_ms, gc.mem_free())
            progress_width = (index + 1) * 150 // FRAME_COUNT
            draw_dashboard(display, rgb565, lines, progress_width)
            display.show()
            if index == 0:
                display.backlight(True)
            sleep_ms(FRAME_INTERVAL_MS)
        print("Dashboard complete after {} frames.".format(FRAME_COUNT))
    finally:
        _close_display(display)


if __name__ == "__main__":
    main()
