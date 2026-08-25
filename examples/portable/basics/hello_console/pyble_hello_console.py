# SPDX-License-Identifier: MIT
"""Print your first message in the PyBLE Console.

Purpose:
    Show how ``print()`` puts words in the Console.
Prerequisites:
    PyBLE board software v0.6.0. You do not need any extra parts.
Settings:
    ``MESSAGE`` holds the words to print. Keep it on one line and use 1 to 40
    characters. Example: ``MESSAGE = "Hello, Sam!"``
Before you run:
    Open this file in PyBLE, read ``MESSAGE``, and tap Run.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    The Console shows "Hello from PyBLE!" and the program finishes.
Try this:
    Change only the words inside ``MESSAGE`` quotes, then run it again.
Stop and cleanup:
    Stop may end the print early. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.
"""


# SETTINGS TO TRY
MESSAGE = "Hello from PyBLE!"

# SAFETY LIMIT - leave this value unchanged.
MAXIMUM_MESSAGE_CHARS = 40


def validate_message(message):
    """Return a short one-line message, or explain what must be fixed."""
    if type(message) is not str:
        raise ValueError("MESSAGE must be words inside quotes")
    if not 1 <= len(message) <= MAXIMUM_MESSAGE_CHARS:
        raise ValueError("MESSAGE must have 1 to 40 characters")
    if "\n" in message or "\r" in message:
        raise ValueError("MESSAGE must stay on one line")
    return message


def hello_message():
    """Check and return the greeting without printing it yet."""
    return validate_message(MESSAGE)


def main():
    """Write one greeting and finish."""
    print(hello_message())


if __name__ == "__main__":
    main()
