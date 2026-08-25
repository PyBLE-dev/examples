# SPDX-License-Identifier: MIT
"""Verify an explicitly configured software SPI loopback.

Purpose:
    Send a few letters out and read them back through one jumper wire. SCK is
    the clock, MOSI sends, and MISO receives.
Settings:
    Choose three different GPIO numbers (numbered board connections) and a slow
    test speed. The five test letters are ready for a first run.
Before you run:
    Ask a teacher or adult to check the pin map for your exact board. Turn board
    power off before adding or removing the jumper. Disconnect other SPI parts
    from these test wires.
Prerequisites:
    Use three numeric GPIOs that the board guide marks safe for software SPI.
    Check their logic voltage and whether the board needs them while starting.
Wiring:
    With power off, connect MOSI directly to MISO with one jumper. SCK stays on
    its own checked GPIO. The board supplies all three signals for this test.
Try this:
    After one PASS, change LOOPBACK_PAYLOAD to b"HELLO" and run again. Keep the
    small b; it tells Python to send the letters as bytes through the wire.
Persistent effects:
    No files or settings are left behind.
Expected:
    The five received letters match the five sent letters, so Console says PASS.
Stop and cleanup:
    Stop may interrupt the transfer; cleanup leaves all three pins as inputs
    that do not send power. The final pin step performs the needed cleanup.
"""

# SETUP GUIDE
# None means "not chosen yet." The program stops safely while a required
# setting is None. Ask a teacher or adult to check your exact board guide.
# Never guess GPIO numbers or copy them from a different board.
#
# Complete example only if the guide approves GPIOs 7, 8, and 9 for this test:
# SCK_PIN = 7
# MOSI_PIN = 8
# MISO_PIN = 9
# SPI_BAUDRATE_HZ = 100_000
# Do not copy these values unless the exact board guide approves them.
# All three GPIO numbers must be different.
SCK_PIN = None  # Replace with the checked numeric clock GPIO.
MOSI_PIN = None  # Replace with the checked numeric send GPIO.
MISO_PIN = None  # Replace with the checked numeric receive GPIO.
SPI_BAUDRATE_HZ = None

# These five letters are sent and read back. Leave them for the first run.
LOOPBACK_PAYLOAD = b"PyBLE"
# END OF SETUP GUIDE
# Later uses of None are safety bookkeeping or mean "no internal pull."
# They are not setup choices. Do not edit the program below.


def validate_pin(name, value):
    """Return a structurally valid, explicitly supplied Pin identifier."""
    if value is None:
        raise ValueError(
            "%s is still None; use the numeric GPIO chosen from your board guide"
            % name
        )
    if isinstance(value, bool):
        raise ValueError("%s must not be a boolean" % name)
    if isinstance(value, int):
        if value < 0 or value > 255:
            raise ValueError("%s must be between 0 and 255" % name)
        return value
    if isinstance(value, str):
        if not value or value != value.strip() or len(value) > 32:
            raise ValueError("%s must be a short, nonblank Pin name" % name)
        return value
    raise ValueError("%s must be an integer or Pin name" % name)


def validate_baudrate(value):
    """Return a deliberately bounded, explicitly supplied SPI baud rate."""
    if value is None:
        raise ValueError(
            "SPI_BAUDRATE_HZ is still None; use 100_000 for this wire-only test"
        )
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 10000 <= value <= 1000000
    ):
        raise ValueError("Set SPI_BAUDRATE_HZ from 10000 to 1000000")
    return value


def validate_payload(payload):
    """Return a small immutable loopback payload."""
    if not isinstance(payload, bytes) or not 1 <= len(payload) <= 32:
        raise ValueError("LOOPBACK_PAYLOAD must contain 1 to 32 bytes")
    return payload


def validate_config(sck_pin, mosi_pin, miso_pin, baudrate_hz, payload):
    """Validate every setting before callers import or construct hardware."""
    sck_pin = validate_pin("SCK_PIN", sck_pin)
    mosi_pin = validate_pin("MOSI_PIN", mosi_pin)
    miso_pin = validate_pin("MISO_PIN", miso_pin)
    if not all(type(pin) is int for pin in (sck_pin, mosi_pin, miso_pin)):
        raise ValueError("multi-pin examples require numeric GPIO identifiers")
    if len({sck_pin, mosi_pin, miso_pin}) != 3:
        raise ValueError("SCK_PIN, MOSI_PIN, and MISO_PIN must be distinct")
    return (
        sck_pin,
        mosi_pin,
        miso_pin,
        validate_baudrate(baudrate_hz),
        validate_payload(payload),
    )


def perform_loopback(bus, payload):
    """Transfer one payload through a SoftSPI-like object."""
    received = bytearray(len(payload))
    bus.write_readinto(payload, received)
    return bytes(received)


def loopback_matches(payload, received):
    """Compare two bounded byte sequences without hardware dependencies."""
    return bytes(payload) == bytes(received)


def release_pins(pins, pin_class):
    """Leave each bus pin as an input that does not send power."""
    first_error = None
    for pin in pins:
        if pin is None:
            continue
        try:
            pin.init(pin_class.IN, None)
        except BaseException as error:
            if first_error is None:
                first_error = error
    if first_error is not None:
        raise first_error


def main():
    """Validate configuration, transfer once, and release bus resources."""
    config = validate_config(
        SCK_PIN,
        MOSI_PIN,
        MISO_PIN,
        SPI_BAUDRATE_HZ,
        LOOPBACK_PAYLOAD,
    )

    from machine import Pin, SoftSPI

    sck_id, mosi_id, miso_id, baudrate_hz, payload = config
    sck = None
    mosi = None
    miso = None
    try:
        sck = Pin(sck_id)
        mosi = Pin(mosi_id)
        miso = Pin(miso_id)
        bus = SoftSPI(
            baudrate=baudrate_hz,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=SoftSPI.MSB,
            sck=sck,
            mosi=mosi,
            miso=miso,
        )
        received = perform_loopback(bus, payload)
        print("Sent: %s" % list(payload))
        print("Received: %s" % list(received))
        if not loopback_matches(payload, received):
            raise RuntimeError("SPI loopback FAIL: check the MOSI/MISO jumper")
        print("SPI loopback PASS.")
    finally:
        # Pinned SoftSPI.deinit() is a no-op; explicit Pin.init() is the cleanup.
        release_pins((sck, mosi, miso), Pin)


if __name__ == "__main__":
    main()
