# SPDX-License-Identifier: MIT
"""Practice using Stop while a short program is running.

Purpose:
    Give you enough time to press Stop, but still finish by itself if you do not.
Prerequisites:
    PyBLE board software v0.6.0, its ``time`` tool, and PyBLE Run/Stop.
Settings:
    There are no settings to change. The 20 ticks and 500 ms wait are safety
    limits. There are 1,000 ms in one second.
Before you run:
    Find the Run and Stop buttons. Tap Run and watch the tick number grow.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    Stop ends the run early. If you wait, it finishes by itself within 15 seconds.
Try this:
    First press Stop near tick 5. Then tap Run again and let all 20 ticks finish.
Stop and cleanup:
    Stop ends the loop. There is nothing to switch off or close.
Validation:
    Built for all five board types. Physical Run and Stop tests are not recorded.
"""

import time


# SAFETY LIMITS - leave these values unchanged.
MAXIMUM_TICKS = 20
TICK_DELAY_MS = 500


def tick_message(tick, maximum_ticks):
    """Build one short progress line."""
    return "Running: tick {}/{} (press Stop to end early)".format(
        tick, maximum_ticks
    )


def run_ticks(maximum_ticks, delay_ms, sleep_ms, emit=print):
    """Show a limited number of ticks with a wait between them."""
    for tick in range(1, maximum_ticks + 1):
        emit(tick_message(tick, maximum_ticks))
        if tick != maximum_ticks:
            sleep_ms(delay_ms)


def main():
    """Run until Stop or the hard iteration limit."""
    run_ticks(MAXIMUM_TICKS, TICK_DELAY_MS, time.sleep_ms)
    print("Finished by itself. Run again and try Stop.")


if __name__ == "__main__":
    main()
