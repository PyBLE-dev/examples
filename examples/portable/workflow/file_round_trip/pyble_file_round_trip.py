# SPDX-License-Identifier: MIT
"""Make one tiny file, check it, and delete it safely.

Purpose:
    Show the three steps of writing, reading, and deleting a text file.
Prerequisites:
    PyBLE board software v0.6.0 and a writable ``/examples`` folder.
Settings:
    Do not change ``FILE_PATH``. It is the one safe path reviewed for this lesson.
Before you run:
    In Files, make the ``/examples`` folder if needed. Check that
    ``pyble_example_round_trip.txt`` is not there. Leave Files alone during Run.
Wiring:
    You do not need any wires.
Persistent effects:
    A normal run deletes the file it made. Stop or lost power can leave
    ``/examples/pyble_example_round_trip.txt`` behind; read it before deleting it.
Expected:
    The Console says it checked 23 characters and removed the small file.
Try this:
    After a normal run, open Files and confirm that the temporary file is gone.
Stop and cleanup:
    The program tries to close and remove only the file it made. If it cannot
    prove the file is still its own, it leaves the file for you to inspect.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    Exclusive mode ``x`` refuses to replace an existing file. The nested
    ``finally`` blocks still try safe cleanup when writing, reading, or closing
    raises an error. Do not rename, replace, or delete the file during Run.
"""

import os


# REVIEWED PATH AND LESSON TEXT - leave both unchanged.
FILE_PATH = "/examples/pyble_example_round_trip.txt"
FILE_CONTENT = "PyBLE file round trip.\n"


def validate_example_path(path):
    """Keep the runnable lesson on its one reviewed app-visible path."""
    if path != "/examples/pyble_example_round_trip.txt":
        raise ValueError("FILE_PATH must remain the reviewed /examples path")
    return path


def round_trip(path, content, open_fn=open, remove_fn=os.remove):
    """Write, verify, and remove one file, returning its character count."""
    if not path.startswith("/"):
        raise ValueError("file path must be absolute")

    # None means this program has not opened a file yet.
    handle = None
    created = False
    safe_to_remove = False
    try:
        try:
            handle = open_fn(path, "x")
        except OSError:
            message = "Refusing to overwrite or create: {}".format(path)
            raise RuntimeError(message)
        created = True
        safe_to_remove = True
        handle.write(content)
        handle.close()
        handle = None  # The write handle is now closed.

        # Once another open begins, do not remove the path unless its contents
        # have been re-verified as the file this run created.
        safe_to_remove = False
        handle = open_fn(path, "r")
        actual = handle.read()
        handle.close()
        handle = None  # The read handle is now closed.
        if actual != content:
            raise RuntimeError("file verification failed")
        safe_to_remove = True
        return len(actual)
    finally:
        try:
            if handle is not None:
                handle.close()
        finally:
            if created and safe_to_remove:
                remove_fn(path)


def main():
    """Run the round trip at the one documented absolute path."""
    path = validate_example_path(FILE_PATH)
    character_count = round_trip(path, FILE_CONTENT)
    print(
        "Verified {} characters; removed {}".format(
            character_count, path
        )
    )


if __name__ == "__main__":
    main()
