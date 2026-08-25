# SPDX-License-Identifier: MIT
"""Make one planned error so you can recognize an error report.

Purpose:
    Show what PyBLE does when a program cannot finish normally.
Prerequisites:
    PyBLE board software v0.6.0 and the PyBLE Console.
Settings:
    There are no settings to change. This file must make its planned error.
Before you run:
    Read the Expected section below. Be ready for PyBLE to show an error; that
    result is the lesson, and it does not harm the board.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson does not save files or change hardware.
Expected:
    The Console announces a planned ``ValueError``. PyBLE then shows an error
    report, which programmers call a traceback.
Try this:
    After this lesson, run ``pyble_error_handling.py`` to see an error that the
    program catches and explains instead.
Stop and cleanup:
    Stop may end the run before the error. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    A small Console may miss part of the traceback, so this file prints the
    exact error first. This file fails on purpose.
"""


# PLANNED ERROR - leave this text unchanged.
ERROR_MESSAGE = "This ValueError is part of the lesson."


def raise_expected_error():
    """Make the one error promised by this teaching example."""
    raise ValueError(ERROR_MESSAGE)


def announcement_message():
    """Name the planned error before the traceback begins."""
    return "A planned ValueError comes next: {}".format(ERROR_MESSAGE)


def main():
    """Announce and then raise the documented error."""
    print(announcement_message())
    raise_expected_error()


if __name__ == "__main__":
    main()
