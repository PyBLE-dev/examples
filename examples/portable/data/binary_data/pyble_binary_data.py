# SPDX-License-Identifier: MIT
"""Pack two numbers into three bytes and unpack them again.

Purpose:
    Show how a program can store small numbers in a compact form.
Prerequisites:
    PyBLE board software v0.6.0 and its ``binascii`` and ``struct`` tools.
Settings:
    ``SAMPLE_NUMBER`` may be 0 to 65,535. ``STATUS_CODE`` may be 0 to 255.
    Both must be whole numbers. Do not change ``RECORD_FORMAT`` yet.
Before you run:
    Find the two setting numbers, then tap Run.
Wiring:
    You do not need any wires. The numbers are teaching data.
Persistent effects:
    This lesson does not save or change any files.
Expected:
    The Console shows hex text ``020107`` and gets back 513 and 7.
Try this:
    Set ``STATUS_CODE = 8``, run again, and compare the last two hex digits.
Stop and cleanup:
    Stop may end the report early. There is nothing to switch off or close.
Validation:
    Built for all five v0.6.0 board types. Physical tests are not recorded yet.

Technical note:
    A byte holds 8 binary digits. Hex is a short way to write those digits.
    In ``>HB``, ``>`` sets the byte order, ``H`` holds two bytes, and ``B``
    holds one byte.
"""

import binascii
import struct


# SETTINGS TO TRY
SAMPLE_NUMBER = 513
STATUS_CODE = 7

# PACKING RULE - leave this text unchanged for this lesson.
RECORD_FORMAT = ">HB"


def validate_values(sample_number, status_code):
    """Check that both numbers fit in the spaces made for them."""
    if type(sample_number) is not int or not 0 <= sample_number <= 65535:
        raise ValueError("SAMPLE_NUMBER must be an integer from 0 to 65535")
    if type(status_code) is not int or not 0 <= status_code <= 255:
        raise ValueError("STATUS_CODE must be an integer from 0 to 255")


def pack_record(sample_number, status_code, struct_module=struct):
    """Check and pack one two-byte number and one one-byte number."""
    validate_values(sample_number, status_code)
    return struct_module.pack(RECORD_FORMAT, sample_number, status_code)


def unpack_record(packed_bytes, struct_module=struct):
    """Get both numbers back using the same packing rule."""
    return struct_module.unpack(RECORD_FORMAT, packed_bytes)


def bytes_as_hex(packed_bytes, binascii_module=binascii):
    """Return lowercase hex text that is easy to print."""
    return binascii_module.hexlify(packed_bytes).decode("ascii")


def main():
    """Pack the record, display it, and unpack it again."""
    packed_bytes = pack_record(SAMPLE_NUMBER, STATUS_CODE)
    sample_number, status_code = unpack_record(packed_bytes)
    print("Packed bytes (hex): {}".format(bytes_as_hex(packed_bytes)))
    print(
        "Unpacked: sample={}, status={}".format(sample_number, status_code)
    )


if __name__ == "__main__":
    main()
