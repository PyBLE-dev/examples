<!-- SPDX-License-Identifier: MIT -->

# Compatibility Model

## Qualified firmware baseline

The initial catalog is designed against PyBLE agent `0.6.0`, PBLE/1,
MicroPython `1.28.0`, firmware source
`0c7230d6708797c241160ba71fbd37e6b22f180a`, tag `firmware-v0.6.0`, and release
descriptor SHA-256
`c2940281a14feddb55c48de15ac18087e9317d1b7130e514fab5a209b046a1e6`.

| Profile | Contract |
| --- | --- |
| `esp32-4mb` | Generic ESP32; no carrier pinout; frozen `neopixel` |
| `esp32-s3-n16r8` | Generic lean ESP32-S3; no carrier pinout or display claim; frozen `neopixel` |
| `waveshare-esp32-s3-lcd-147b` | Exact B-version board; frozen `neopixel`, `pyble_st7789`, and `pyble_waveshare_lcd147b` |
| `esp32-c3-4mb` | Generic ESP32-C3; no carrier pinout; frozen `neopixel` |
| `rpi-pico2-w` | Exact Pico 2 W; onboard LED is `Pin("LED")`; no `neopixel` claim |

All five profiles provide the common MicroPython surface used by portable and
explicitly configured generic examples. The profiles do not share a physical
pin map. Both ESP32-S3 images report `chip=esp32-s3`; code and catalog tooling
must not infer the exact Waveshare image from that value.

## Designed versus validated

`designed_profiles` records reviewed API and safety intent.
`validated_profiles` records only profiles with passing evidence for the exact
example source and firmware identities. The two fields must remain separate in
source review, catalog UI, documentation, and releases.

The initial implementation intentionally leaves `validated_profiles` empty.
Host compilation and fake-hardware tests can establish `host_passed`, but only
the HIL process in [validation.md](validation.md) may establish `hil_passed`.
Known incompatibilities are explicit; absence from `validated_profiles` is not
silently converted into incompatibility or support.
