# SPDX-License-Identifier: MIT
"""Record twelve ADC readings without overwriting an existing file.

Purpose:
    Measure a small changing voltage twelve times and save the numbers in a
    board file that can be opened in PyBLE Files.
Prerequisites:
    Ask a teacher or another adult to check that the chosen pin can measure an
    analog voltage (ADC), stays inside the board's limits, and is not a pin
    that the board needs in order to start.
Wiring:
    Connect a low-voltage analog signal to the selected ADC pin and share
    ground. Never exceed the board or pin limit. The program does not change
    the ADC input range, so an adult must check it.
Settings:
    ``ADC_PIN`` is the GPIO/GP label for a pin that can measure voltage. It is
    not the metal header-pin position. The other values set file name, count,
    and timing; the ``MAX_`` values are safety limits.
Before you run:
    In Files, create ``/examples`` and remove or rename an older
    ``pyble_adc_log.csv``. Turn power off before changing wires, then check the
    voltage limit and shared ground before filling ``ADC_PIN``.
Try this:
    SETUP GUIDE shows a Raspberry Pi Pico 2 W GP26/ADC0 example using only
    voltages from 0 to 3.3 V. Use it only with that named and checked board.
Persistent effects:
    Creates and intentionally retains ``/examples/pyble_adc_log.csv`` for
    inspection. The required ``/examples`` directory must already exist. It
    refuses to overwrite an existing path. Delete or rename that file manually
    before another run. A partial file can remain after interruption.
Expected:
    Twelve samples are written with elapsed time, a raw ADC reading from 0 to
    65,535, and the same reading scaled from 0 to 1,000. The console reports
    the byte count.
Stop and cleanup:
    Sample count and file size are limited. The program closes but keeps the
    log after completion, error, or PyBLE Stop. It releases the ADC and pin.

Validation:
    Written for all five PyBLE board-software types with checked wiring.
    Physical tests are not recorded yet.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops before touching a pin.
# Use the GPIO/GP label from the board guide, not the header-pin position.
# Complete example only for a Raspberry Pi Pico 2 W:
# ADC_PIN = 26
# GP26 is ADC0. A teacher can check a 10 kOhm knob (potentiometer) wired with
# its middle leg to GP26 and its two outer legs to 3V3(OUT) and GND.
# Never put 5 V on GP26; this example must stay between 0 V and 3.3 V.
ADC_PIN = None

# The file is kept so you can open it later in PyBLE Files.
LOG_PATH = "/examples/pyble_adc_log.csv"
SAMPLE_COUNT = 12
SAMPLE_INTERVAL_MS = 250
# These two MAX_ values are fixed safety limits. Do not increase them.
MAX_SAMPLE_COUNT = 32
MAX_LOG_BYTES = 1_024
# END OF SETUP GUIDE


def _valid_pin_id(value):
    return (
        type(value) is int
        and 0 <= value <= 255
        or type(value) is str
        and 0 < len(value) <= 32
        and value.strip() == value
    )


def validate_configuration(pin_id):
    """Validate all configuration and caps before constructing the ADC."""
    if not _valid_pin_id(pin_id):
        raise ValueError("set ADC_PIN to a reviewed ADC-capable pin identifier")
    if LOG_PATH != "/examples/pyble_adc_log.csv":
        raise ValueError("LOG_PATH must remain the reviewed absolute path")
    if MAX_SAMPLE_COUNT != 32:
        raise ValueError("MAX_SAMPLE_COUNT is a fixed safety cap of 32")
    if type(SAMPLE_COUNT) is not int or not 1 <= SAMPLE_COUNT <= MAX_SAMPLE_COUNT:
        raise ValueError("SAMPLE_COUNT exceeds its fixed cap")
    if type(SAMPLE_INTERVAL_MS) is not int or not 50 <= SAMPLE_INTERVAL_MS <= 2_000:
        raise ValueError("SAMPLE_INTERVAL_MS must be 50..2000")
    if MAX_LOG_BYTES != 1_024:
        raise ValueError("MAX_LOG_BYTES is a fixed safety cap of 1024")
    runtime_ms = max(0, SAMPLE_COUNT - 1) * SAMPLE_INTERVAL_MS
    if runtime_ms > 3_000:
        raise ValueError("paced ADC logging must remain within 3 seconds")
    return pin_id


def require_absent(path, stat):
    """Refuse an existing path and propagate errors other than not-found."""
    try:
        stat(path)
    except OSError as error:
        # None here means the error did not include a number we can inspect.
        code = error.args[0] if error.args else None
        if code in (2, -2):
            return
        raise
    raise RuntimeError("Refusing to overwrite {}".format(path))


def csv_sample_line(index, elapsed_ms, raw_adc):
    """Make one row with the raw reading and a simpler 0-to-1,000 scale."""
    if type(index) is not int or index < 0:
        raise ValueError("sample index must be a non-negative integer")
    if type(elapsed_ms) is not int or elapsed_ms < 0:
        raise ValueError("elapsed time must be a non-negative integer")
    if type(raw_adc) is not int or not 0 <= raw_adc <= 65_535:
        raise ValueError("ADC value must be an integer from 0 to 65535")
    scaled_0_to_1000 = raw_adc * 1_000 // 65_535
    return "{},{},{},{}\n".format(
        index, elapsed_ms, raw_adc, scaled_0_to_1000
    )


def write_bounded(stream, text, byte_count, maximum):
    """Write one row within the cap; some ports return None after writing."""
    encoded_size = len(text.encode("utf-8"))
    next_count = byte_count + encoded_size
    if next_count > maximum:
        raise RuntimeError("ADC log byte cap would be exceeded")
    written = stream.write(text)
    if written is not None and written != len(text):
        raise OSError("short ADC log write")
    return next_count


def main():
    """Create one exclusive log, sample finitely, close it, and retain it."""
    pin_id = validate_configuration(ADC_PIN)

    import os

    require_absent(LOG_PATH, os.stat)

    from machine import ADC, Pin
    from time import sleep_ms, ticks_diff, ticks_ms

    # None means "not created yet" so cleanup knows which objects exist.
    pin = None
    adc = None
    stream = None
    byte_count = 0
    try:
        pin = Pin(pin_id, Pin.IN)
        adc = ADC(pin)
        try:
            # Mode "x" creates a file but refuses to replace an existing one.
            stream = open(LOG_PATH, "x")
        except OSError:
            raise RuntimeError(
                "Log path is unavailable or now exists; nothing was overwritten"
            )

        byte_count = write_bounded(
            stream,
            "sample,elapsed_ms,raw_0_to_65535,scaled_0_to_1000\n",
            byte_count,
            MAX_LOG_BYTES,
        )
        started_ms = ticks_ms()
        for index in range(SAMPLE_COUNT):
            elapsed_ms = ticks_diff(ticks_ms(), started_ms)
            line = csv_sample_line(index, elapsed_ms, adc.read_u16())
            byte_count = write_bounded(stream, line, byte_count, MAX_LOG_BYTES)
            stream.flush()
            if index + 1 < SAMPLE_COUNT:
                sleep_ms(SAMPLE_INTERVAL_MS)
    finally:
        try:
            if stream is not None:
                stream.close()
        finally:
            try:
                if adc is not None:
                    # Some MicroPython ADC objects have no deinit method.
                    deinit = getattr(adc, "deinit", None)
                    if deinit is not None:
                        deinit()
            finally:
                if pin is not None:
                    # The second None removes any built-in pull resistor.
                    pin.init(Pin.IN, None)

    print("Retained {} bytes at {}.".format(byte_count, LOG_PATH))


if __name__ == "__main__":
    main()
