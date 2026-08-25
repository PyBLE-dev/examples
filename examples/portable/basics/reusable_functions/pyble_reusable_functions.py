# SPDX-License-Identifier: MIT
"""Build small functions and use them more than once.

Purpose:
    Use the same small functions for several temperatures.
Prerequisites:
    PyBLE board software v0.6.0; only basic Python tools are used.
Settings:
    ``TEMPERATURES_C`` may hold 1 to 5 numbers from -50 to 50 degrees Celsius.
Before you run:
    Find ``celsius_to_fahrenheit()`` and notice that it returns an answer.
Wiring:
    You do not need wires. The temperatures do not come from a real sensor.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    Three console lines show converted temperatures and descriptions.
Try this:
    Change 20 to 10 in ``TEMPERATURES_C`` and run the lesson again.
Stop and cleanup:
    Stop may end the report early. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    The formula multiplies by 9, divides by 5, and then adds 32.
"""


# SETTINGS TO TRY
TEMPERATURES_C = (0, 20, 30)

# SAFETY LIMIT - leave this value unchanged.
MAXIMUM_TEMPERATURES = 5


def validate_temperatures(values):
    """Check that the temperature collection stays small and readable."""
    if (
        type(values) not in (tuple, list)
        or not 1 <= len(values) <= MAXIMUM_TEMPERATURES
    ):
        raise ValueError("TEMPERATURES_C must hold 1 to 5 numbers")
    for value in values:
        if type(value) not in (int, float) or not -50 <= value <= 50:
            raise ValueError("each temperature must be a number from -50 to 50")


def celsius_to_fahrenheit(value_c):
    """Convert a Celsius number and return the Fahrenheit value."""
    return value_c * 9 / 5 + 32


def describe_temperature(value_c):
    """Return a short description based on a Celsius value."""
    if value_c < 10:
        return "cold"
    if value_c < 25:
        return "mild"
    return "hot"


def temperature_line(value_c):
    """Use both helper functions to build one line."""
    value_f = celsius_to_fahrenheit(value_c)
    return "{} C = {:.1f} F ({})".format(
        value_c, value_f, describe_temperature(value_c)
    )


def main():
    """Apply the same functions to three inputs."""
    validate_temperatures(TEMPERATURES_C)
    for value_c in TEMPERATURES_C:
        print(temperature_line(value_c))


if __name__ == "__main__":
    main()
