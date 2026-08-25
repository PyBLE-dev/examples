# SPDX-License-Identifier: MIT
"""Fade an externally wired LED with PWM, then turn the output off.

Purpose:
    Fade an external LED up and down, then stop by itself. PWM turns the LED on
    and off very quickly so your eyes see a change in brightness.
Settings:
    Choose a PWM-capable GPIO (a numbered board connection) and a safe PWM
    frequency. The dim brightness, fade steps, cycles, and wait are ready.
Before you run:
    Ask a teacher or adult to check the pin map, resistor, and LED for your exact
    board. Turn board power off before changing wires. Never drive a motor,
    speaker, or high-power light directly from a GPIO.
Prerequisites:
    Use a GPIO that the board guide marks safe for PWM output. Check its voltage,
    current limit, whether the board needs it while starting, and whether its
    PWM timing parts are shared with another pin.
Wiring:
    Connect GPIO -> resistor -> LED -> GND (ground). An adult must check the
    resistor.
Try this:
    After one safe run, set FADE_CYCLES to 1 and watch one up-and-down fade.
Persistent effects:
    No files are left behind. PWM timing can be shared with other PWM outputs,
    so this lesson also turns its PWM output off during cleanup.
Expected:
    The LED fades up to about one-quarter brightness and back down twice.
Stop and cleanup:
    Stop may interrupt fading; cleanup turns brightness to zero, stops PWM, and
    leaves the pin as an input that does not send power to the circuit.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while a required
# setting is None. Ask a teacher or adult to check your exact board guide.
# Never guess a GPIO number or copy one from a different board.
#
# Complete example only if the guide approves GPIO 7 for this PWM LED:
# PWM_PIN = 7
# PWM_FREQUENCY_HZ = 1_000
# Do not copy 7 unless your exact board guide says to use it.
PWM_PIN = None  # Replace with the checked PWM-capable GPIO number.
PWM_FREQUENCY_HZ = None

# These lesson settings are ready for the first run.
MAX_DUTY_U16 = 16384  # Limit brightness to about one quarter of full duty.
FADE_STEPS = 8  # Use eight small brightness steps.
FADE_CYCLES = 2  # Fade up and down twice.
STEP_DELAY_MS = 100  # Hold each step for one tenth-second.
# END OF SETUP GUIDE
# Later uses of None are safety bookkeeping or mean "no internal pull."
# They are not setup choices. Do not edit the program below.


def validate_pin(name, value):
    """Return a structurally valid, explicitly supplied Pin identifier."""
    if value is None:
        raise ValueError(
            "%s is still None; use the PWM GPIO chosen from your board guide"
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


def validate_config(pin_id, frequency_hz, max_duty, steps, cycles, delay_ms):
    """Validate every setting before callers import or construct hardware."""
    pin_id = validate_pin("PWM_PIN", pin_id)
    if frequency_hz is None:
        raise ValueError(
            "PWM_FREQUENCY_HZ is still None; after checking PWM support, "
            "use 1_000 for this plain-LED lesson"
        )
    frequency_hz = validate_int("PWM_FREQUENCY_HZ", frequency_hz, 100, 5000)
    max_duty = validate_int("MAX_DUTY_U16", max_duty, 1, 16384)
    steps = validate_int("FADE_STEPS", steps, 2, 32)
    cycles = validate_int("FADE_CYCLES", cycles, 1, 5)
    delay_ms = validate_int("STEP_DELAY_MS", delay_ms, 20, 1000)
    if (2 * steps + 1) * cycles * delay_ms > 5_000:
        raise ValueError("the paced PWM work must remain within 5 seconds")
    return pin_id, frequency_hz, max_duty, steps, cycles, delay_ms


def duty_sequence(max_duty, steps):
    """Return one finite up/down fade as portable integer duties."""
    rising = [(max_duty * index) // steps for index in range(steps + 1)]
    falling = [(max_duty * index) // steps for index in range(steps - 1, -1, -1)]
    return tuple(rising + falling)


def run_fade(pwm, duties, cycles, delay_ms, sleep_ms):
    """Apply a bounded duty sequence to a PWM-like object."""
    for _ in range(cycles):
        for duty in duties:
            pwm.duty_u16(duty)
            sleep_ms(delay_ms)


def main():
    """Validate configuration, run the fade, and release PWM resources."""
    config = validate_config(
        PWM_PIN,
        PWM_FREQUENCY_HZ,
        MAX_DUTY_U16,
        FADE_STEPS,
        FADE_CYCLES,
        STEP_DELAY_MS,
    )

    from machine import PWM, Pin
    from time import sleep_ms

    pin_id, frequency_hz, max_duty, steps, cycles, delay_ms = config
    pin = None
    pwm = None
    try:
        pin = Pin(pin_id, Pin.OUT, value=0)
        pwm = PWM(pin, freq=frequency_hz, duty_u16=0)
        print("Running %d dim PWM fade cycle(s)." % cycles)
        run_fade(
            pwm,
            duty_sequence(max_duty, steps),
            cycles,
            delay_ms,
            sleep_ms,
        )
        print("PWM fade complete.")
    finally:
        try:
            if pwm is not None:
                try:
                    pwm.duty_u16(0)
                finally:
                    pwm.deinit()
        finally:
            if pin is not None:
                pin.init(Pin.IN, None)


if __name__ == "__main__":
    main()
