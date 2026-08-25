# SPDX-License-Identifier: MIT
"""Show a short list of names from one folder on the board.

Purpose:
    Read only the direct names in one folder without changing them.
Prerequisites:
    PyBLE board software v0.6.0 and its ``gc`` and ``os`` tools.
Settings:
    ``DIRECTORY = "/"`` means the board's top folder. You may use
    ``DIRECTORY = "/examples"`` after making that folder in Files.
Before you run:
    Check that ``DIRECTORY`` starts with ``/`` and that the folder exists.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson only reads names. It does not save, delete, or change files.
Expected:
    One Console line shows up to 20 short names from the chosen folder. It says
    when more names exist.
Try this:
    Run once with ``/``. If ``/examples`` exists, change the setting and compare.
Stop and cleanup:
    Stop may end the list early. Cleanup closes the folder reader.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    The limits below keep names short and Console output small. The full path is
    important because Run may use a different current folder than PyBLE Files.
"""

import gc
import os


# SETTING TO TRY
DIRECTORY = "/"

# SAFETY LIMITS - leave these values unchanged.
MAXIMUM_NAMES = 20
MAXIMUM_NAME_CHARS = 16


def validate_directory(directory):
    """Allow only the two short folders explained in Settings."""
    if directory not in ("/", "/examples"):
        raise ValueError('DIRECTORY must be "/" or "/examples"')
    return directory


def short_name(name, maximum_chars=MAXIMUM_NAME_CHARS):
    """Make one folder name short and safe to show in the Console."""
    if type(maximum_chars) is not int or not 1 <= maximum_chars <= 16:
        raise ValueError("maximum_chars must be an integer from 1 to 16")
    text = str(name)
    characters = []
    for character in text[:maximum_chars]:
        character_number = ord(character)
        characters.append(character if 32 <= character_number <= 126 else "?")
    safe = "".join(characters)
    return safe + "..." if len(text) > maximum_chars else safe


def choose_names(names, maximum_names=MAXIMUM_NAMES):
    """Choose a limited number of names and say whether more exist."""
    if type(maximum_names) is not int or not 1 <= maximum_names <= 20:
        raise ValueError("maximum_names must be an integer from 1 to 20")
    shown = []
    for name in names:
        if len(shown) == maximum_names:
            return shown, True
        shown.append(short_name(name))
    return shown, False


def read_folder_names(os_module, path):
    """Read each direct name with the board's small-memory folder tool."""
    return (entry[0] for entry in os_module.ilistdir(path))


def folder_message(directory, shown, more_exist):
    """Build one short physical Console line for the chosen folder."""
    parts = ["Folder: {}".format(directory)]
    if shown:
        parts.extend("- {}".format(name) for name in shown)
    else:
        parts.append("(empty)")
    if more_exist:
        parts.append("... more name(s) not shown")
    return " | ".join(parts)


def close_names(names):
    """Close the folder-name reader when it provides a close action."""
    if hasattr(names, "close"):
        names.close()


def main():
    """Read and print only direct names from the reviewed absolute path."""
    directory = validate_directory(DIRECTORY)
    names = read_folder_names(os, directory)
    try:
        shown, more_exist = choose_names(names)
    finally:
        try:
            close_names(names)
        finally:
            # None drops our last link to the reader so gc can finish closing it.
            names = None
            gc.collect()
    print(folder_message(directory, shown, more_exist))


if __name__ == "__main__":
    main()
