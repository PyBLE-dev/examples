# SPDX-License-Identifier: MIT
"""Show a few facts about the software running on your board.

Purpose:
    Show the Python name and version, board software, and free memory.
Prerequisites:
    PyBLE board software v0.6.0 and its ``gc``, ``os``, and ``sys`` tools.
Settings:
    There are no settings to change in this lesson.
Before you run:
    Open the Console, then tap Run.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson does not save files. It may free memory that is no longer used.
Expected:
    Four short lines show Python, its version, board software, and free memory.
Try this:
    Run the same file on another supported board and compare the four lines.
Stop and cleanup:
    Stop may end the report early. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    One byte is a small piece of memory. This lesson never prints a board ID,
    user label, or hostname.
"""

import gc
import os
import sys


def version_text(version):
    """Join the first three version numbers with dots."""
    parts = []
    for value in version[:3]:
        parts.append(str(value))
    return ".".join(parts)


def collect_runtime_info(gc_module=gc, os_module=os, sys_module=sys):
    """Collect only the four safe facts shown by this lesson."""
    gc_module.collect()
    implementation = sys_module.implementation
    uname = os_module.uname()
    if hasattr(gc_module, "mem_free"):
        free_memory = gc_module.mem_free()
    else:
        free_memory = "not reported"
    return (
        ("Python", implementation.name),
        ("Python version", version_text(implementation.version)),
        ("Board software", "{}/{}".format(uname.sysname, sys_module.platform)),
        ("Free memory (bytes)", free_memory),
    )


def main():
    """Print the four-line software and memory report."""
    for label, value in collect_runtime_info():
        print("{}: {}".format(label, value))


if __name__ == "__main__":
    main()
