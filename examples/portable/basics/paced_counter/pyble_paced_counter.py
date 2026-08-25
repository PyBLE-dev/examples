# SPDX-License-Identifier: MIT
"""Count slowly so you can watch a loop work.

Purpose:
    Use variables, a loop, and a short wait between numbers.
Prerequisites:
    PyBLE board software v0.6.0. Try Hello Console first if you are new.
Settings:
    ``TOTAL_COUNTS`` may be 1 to 5. ``DELAY_MS`` may be 100 to 500.
    There are 1,000 milliseconds (ms) in one second.
Before you run:
    Check that the two settings are inside those ranges, then tap Run.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    The Console shows Count 1/5 through Count 5/5, half a second apart.
Try this:
    Set ``TOTAL_COUNTS = 3`` and ``DELAY_MS = 250``, then run it again.
Stop and cleanup:
    Stop may end the count early. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.
"""

import time


# SETTINGS TO TRY
TOTAL_COUNTS = 5       # How many numbers to show: 1 to 5.
DELAY_MS = 500         # Wait time: 100 to 500 ms.


def validate_settings(total, delay_ms):
    """Check the two settings before counting."""
    if type(total) is not int or not 1 <= total <= 5:
        raise ValueError("TOTAL_COUNTS must be an integer from 1 to 5")
    if type(delay_ms) is not int or not 100 <= delay_ms <= 500:
        raise ValueError("DELAY_MS must be an integer from 100 to 500")


def count_message(current, total):
    """Build one counter line without sleeping or printing."""
    return "Count {}/{}".format(current, total)


def run_counter(total, delay_ms, sleep_ms, emit=print):
    """Show each number and use the supplied wait function between numbers."""
    for current in range(1, total + 1):
        emit(count_message(current, total))
        if current != total:
            sleep_ms(delay_ms)


def main():
    """Check the settings and run the paced counter."""
    validate_settings(TOTAL_COUNTS, DELAY_MS)
    run_counter(TOTAL_COUNTS, DELAY_MS, time.sleep_ms)


if __name__ == "__main__":
    main()
