# SPDX-License-Identifier: MIT
"""Let two small tasks take turns while they wait.

Purpose:
    Show that another task can work while the first task is waiting.
Prerequisites:
    PyBLE board software v0.6.0 and its ``asyncio`` tool. Try Paced Counter first.
Settings:
    There are no settings to change. The step counts and wait times below are
    safety limits for this lesson. There are 1,000 ms in one second.
Before you run:
    Guess whether Red or Blue will print its next step first, then tap Run.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    Red shows three steps and Blue shows two. Their lines take turns.
Try this:
    Run it twice and check whether each task always reaches its last step.
Stop and cleanup:
    Stop may end either wait. The program resets its task manager before ending.
Validation:
    Run and Stop must still be checked on all five board types before release.

Technical note:
    ``asyncio`` calls this cooperative work: tasks choose to pause at ``await``
    so other tasks can run. The task manager is also called an event loop.
"""

import asyncio


# SAFETY LIMITS - leave these values unchanged.
RED_STEPS = 3
RED_WAIT_MS = 180
BLUE_STEPS = 2
BLUE_WAIT_MS = 260


async def paced_worker(label, count, delay_ms, sleep_ms, emit=print):
    """Show one task's steps, waiting between them so another task can run."""
    for step in range(1, count + 1):
        emit("Task {}: step {}/{}".format(label, step, count))
        if step != count:
            await sleep_ms(delay_ms)


async def cooperative_demo(sleep_ms, emit=print):
    """Start both workers and wait until both are finished."""
    await asyncio.gather(
        paced_worker("Red", RED_STEPS, RED_WAIT_MS, sleep_ms, emit),
        paced_worker("Blue", BLUE_STEPS, BLUE_WAIT_MS, sleep_ms, emit),
    )


def main():
    """Run both tasks once and reset the task manager afterward."""
    try:
        asyncio.run(cooperative_demo(asyncio.sleep_ms))
    finally:
        asyncio.new_event_loop()
    print("Both tasks completed.")


if __name__ == "__main__":
    main()
