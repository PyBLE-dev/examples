# SPDX-License-Identifier: MIT
"""Turn a small collection into JSON text and back again.

Purpose:
    Show how JSON can carry named pieces of data as text.
Prerequisites:
    PyBLE board software v0.6.0 and its ``json`` tool.
Settings:
    In ``RECORD``, you may change "bird" to "cat", 2 to 4, and ``True`` to
    ``False``. Keep the three names on the left unchanged.
Before you run:
    Read the three name-and-value pairs in ``RECORD``, then tap Run.
Wiring:
    You do not need any wires. The record is teaching data.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    The Console shows JSON text and then the three values recovered from it.
Try this:
    Make the record describe a cat, run it, and find your changes in both lines.
Stop and cleanup:
    Stop may end the report early. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    Encoding turns the collection into JSON text. Decoding turns that text back
    into a Python collection. Both versions stay only in the board's memory.
"""

import json


# SETTINGS TO TRY
RECORD = {
    "animal": "bird",
    "legs": 2,
    "can_fly": True,
}


def validate_record(record):
    """Check the small animal record before turning it into JSON."""
    required_names = ("animal", "legs", "can_fly")
    if (
        type(record) is not dict
        or len(record) != len(required_names)
        or any(name not in record for name in required_names)
    ):
        raise ValueError("RECORD must keep animal, legs, and can_fly")
    animal = record["animal"]
    legs = record["legs"]
    can_fly = record["can_fly"]
    if type(animal) is not str or not 1 <= len(animal) <= 12:
        raise ValueError("animal must be 1 to 12 characters inside quotes")
    if "\n" in animal or "\r" in animal:
        raise ValueError("animal must stay on one line")
    if type(legs) is not int or not 0 <= legs <= 100:
        raise ValueError("legs must be a whole number from 0 to 100")
    if type(can_fly) is not bool:
        raise ValueError("can_fly must be True or False")


def json_round_trip(record, json_module=json):
    """Make JSON text, then turn the text back into a collection."""
    encoded = json_module.dumps(record)
    return encoded, json_module.loads(encoded)


def main():
    """Turn the animal record into JSON, back again, and print both."""
    validate_record(RECORD)
    encoded, decoded = json_round_trip(RECORD)
    print("JSON: {}".format(encoded))
    print(
        "Decoded: animal={}, legs={}, can_fly={}".format(
            decoded["animal"], decoded["legs"], decoded["can_fly"]
        )
    )


if __name__ == "__main__":
    main()
