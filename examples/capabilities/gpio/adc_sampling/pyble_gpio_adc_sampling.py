# SPDX-License-Identifier: MIT
"""Take a small set of ADC readings from a reviewed input pin.

Purpose:
    Read a safe analog voltage as a number. ADC means "analog-to-digital
    converter": it turns a voltage into a number the program can use.
Settings:
    Choose one GPIO (a numbered board connection) that your exact board guide
    marks as an ADC input. The readings and wait are ready for a first run.
Before you run:
    Ask a teacher or adult to check the ADC pin and maximum input voltage for
    your exact board. Turn board power off before changing wires. Never connect
    5 V just because a board or cable makes 5 V available.
Prerequisites:
    Use a GPIO marked ADC or analog input. Check its voltage limit, whether the
    board needs it while starting, and any limits while Wi-Fi is running.
Wiring:
    Connect only a teacher-approved low-voltage signal to the ADC pin and share
    GND. The signal must stay inside the exact board's safe input range.
Try this:
    Move a teacher-approved knob or sensor slowly and watch the numbers change.
Persistent effects:
    No files or settings are left behind; the example only reads the input.
Expected:
    Twelve readings appear over about three seconds. Each shows the board's raw
    number from 0 to 65,535 and the same result scaled from 0.000 to 1.000.
Stop and cleanup:
    Stop may interrupt the readings; cleanup stops the ADC where possible and
    leaves the pin as an input that does not send power to the circuit.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while a required
# setting is None. Ask a teacher or adult to check your exact board guide.
# Never guess a GPIO number or copy one from a different board.
#
# Complete example only if the guide marks GPIO 7 as a safe ADC input:
# ADC_PIN = 7
# Do not copy 7 unless your exact board guide says it can measure voltage.
ADC_PIN = None  # Replace with the checked ADC or analog-input GPIO number.

# These lesson settings are ready for the first run.
SAMPLE_COUNT = 12  # Take twelve readings.
SAMPLE_INTERVAL_MS = 200  # Wait one fifth-second between readings.
# END OF SETUP GUIDE
# Later uses of None are safety bookkeeping or mean "no internal pull."
# They are not setup choices. Do not edit the program below.


def validate_pin(name, value):
    """Return a structurally valid, explicitly supplied Pin identifier."""
    if value is None:
        raise ValueError(
            "%s is still None; choose a GPIO marked ADC in your board guide"
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


def validate_config(pin_id, count, interval_ms):
    """Validate every setting before callers import or construct hardware."""
    pin_id = validate_pin("ADC_PIN", pin_id)
    count = validate_int("SAMPLE_COUNT", count, 1, 100)
    interval_ms = validate_int("SAMPLE_INTERVAL_MS", interval_ms, 20, 2000)
    # PyBLE receives a print body and its newline as two physical writes. Count
    # every sample plus the start and final lines before accepting the budget.
    console_writes = 2 * (count + 2)
    paced_ms = (count - 1) * interval_ms + (console_writes - 1) * 40
    if paced_ms > 3_500:
        raise ValueError("paced ADC output must remain within 3.5 seconds")
    return pin_id, count, interval_ms


def normalize_reading(raw_value):
    """Normalize one unsigned 16-bit ADC reading to the inclusive unit range."""
    raw_value = validate_int("raw ADC value", raw_value, 0, 65535)
    return raw_value / 65535


def sample_adc(adc, count, interval_ms, sleep_ms, emit):
    """Read and report a bounded number of samples from an ADC-like object."""
    for index in range(count):
        raw_value = adc.read_u16()
        normalized = normalize_reading(raw_value)
        emit("%02d: raw=%d scaled_0_to_1=%.3f" % (
            index + 1, raw_value, normalized
        ))
        if index + 1 < count:
            sleep_ms(interval_ms)


def main():
    """Validate configuration, sample ADC, and release available resources."""
    config = validate_config(ADC_PIN, SAMPLE_COUNT, SAMPLE_INTERVAL_MS)

    from machine import ADC, Pin
    from time import sleep_ms

    pin_id, count, interval_ms = config
    pin = None
    adc = None
    try:
        pin = Pin(pin_id)
        adc = ADC(pin)
        print("Taking a fixed number of ADC readings.")
        sample_adc(adc, count, interval_ms, sleep_ms, print)
        print("ADC sampling complete.")
    finally:
        try:
            if adc is not None:
                deinit = getattr(adc, "deinit", None)
                if deinit is not None:
                    deinit()
        finally:
            if pin is not None:
                pin.init(Pin.IN, None)


if __name__ == "__main__":
    main()
