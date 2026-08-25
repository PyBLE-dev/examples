# SPDX-License-Identifier: MIT
"""Check a value and catch one planned mistake.

Purpose:
    Show how a program can catch and explain one planned mistake.
Prerequisites:
    PyBLE board software v0.6.0; only basic Python tools are used.
Settings:
    ``TOO_HIGH_PERCENTAGE`` may be a whole number from 101 to 200. Example:
    ``TOO_HIGH_PERCENTAGE = 101``. It must stay too high for this lesson.
Before you run:
    Remember that a percentage must be from 0 to 100, then tap Run.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    The Console shows one allowed value and says it caught the planned mistake.
Try this:
    After running, change ``TOO_HIGH_PERCENTAGE`` from 120 to 101. It is still
    too high, so the program catches it in the same way.
Stop and cleanup:
    Stop may end the report early. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    ``ValueError`` means a value is not allowed. ``except`` catches that error
    so this program can explain it and finish normally.
"""


# SETTING TO TRY
TOO_HIGH_PERCENTAGE = 120

# LESSON VALUE - leave this allowed percentage unchanged.
GOOD_PERCENTAGE = 75


def validate_lesson_setting(value):
    """Check that the planned mistake stays a small, too-high percentage."""
    if type(value) is not int or not 101 <= value <= 200:
        raise ValueError("TOO_HIGH_PERCENTAGE must be an integer from 101 to 200")


def validate_percentage(value):
    """Return a whole-number percentage from 0 to 100."""
    if type(value) is not int or value < 0 or value > 100:
        raise ValueError("a percentage must be a whole number from 0 to 100")
    return value


def main():
    """Handle only the expected error from one deliberately invalid value."""
    validate_lesson_setting(TOO_HIGH_PERCENTAGE)
    valid_value = validate_percentage(GOOD_PERCENTAGE)
    print("{} is an allowed percentage.".format(valid_value))
    try:
        validate_percentage(TOO_HIGH_PERCENTAGE)
    except ValueError as error:
        print("We caught the planned mistake: {}".format(error))


if __name__ == "__main__":
    main()
