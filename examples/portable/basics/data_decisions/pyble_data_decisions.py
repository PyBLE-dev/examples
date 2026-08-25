# SPDX-License-Identifier: MIT
"""Use a small group of numbers to make a decision.

Purpose:
    Find the average temperature and choose a word that describes it.
Prerequisites:
    PyBLE board software v0.6.0; only basic Python tools are used.
Settings:
    In ``SAMPLE``, the name may have 1 to 20 characters and ``values_c`` may
    hold 1 to 5 numbers from -50 to 50. The letter C means degrees Celsius.
Before you run:
    Read the three temperatures in ``SAMPLE``, guess their average, then tap Run.
Wiring:
    You do not need wires. The numbers below do not come from a real sensor.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    The console shows the sample name, values, average, and result.
Try this:
    Change 18 to 30, guess the new result, and run the lesson again.
Stop and cleanup:
    Stop may end the report early. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    An average below 18 is cool. From 18 to below 25 is comfortable. An average
    of 25 or more is warm.
"""


# SETTINGS TO TRY
SAMPLE = {
    "name": "workbench",
    "values_c": (18, 23, 27),
}

# SAFETY LIMITS - leave these values unchanged.
MAXIMUM_NAME_CHARS = 20
MAXIMUM_VALUES = 5

# DESCRIPTION RULES - leave these values unchanged in this lesson.
COOL_BELOW_C = 18
WARM_FROM_C = 25


def validate_sample(sample):
    """Check that the name and temperature list stay small and readable."""
    if type(sample) is not dict:
        raise ValueError("SAMPLE must stay a collection with name and values_c")
    name = sample.get("name")
    values = sample.get("values_c")
    if type(name) is not str or not 1 <= len(name) <= MAXIMUM_NAME_CHARS:
        raise ValueError("the sample name must have 1 to 20 characters")
    if "\n" in name or "\r" in name:
        raise ValueError("the sample name must stay on one line")
    if type(values) not in (tuple, list) or not 1 <= len(values) <= MAXIMUM_VALUES:
        raise ValueError("values_c must hold 1 to 5 temperatures")
    for value in values:
        if type(value) not in (int, float) or not -50 <= value <= 50:
            raise ValueError("each temperature must be a number from -50 to 50")
    return name, values


def classify_temperature(value_c):
    """Choose cool, comfortable, or warm for one Celsius value."""
    if value_c < COOL_BELOW_C:
        return "cool"
    if value_c < WARM_FROM_C:
        return "comfortable"
    return "warm"


def summarize_sample(sample):
    """Check the sample, find its average, and choose a description."""
    name, values = validate_sample(sample)
    average = sum(values) / len(values)
    return name, values, average, classify_temperature(average)


def main():
    """Print the sample data and the resulting branch decision."""
    name, values, average, decision = summarize_sample(SAMPLE)
    print("Sample: {}".format(name))
    print("Values (C): {}".format(values))
    print("Average: {:.1f} C -> {}".format(average, decision))


if __name__ == "__main__":
    main()
