<!-- SPDX-License-Identifier: MIT -->

# Example Authoring Contract

## Leaf and source layout

Put each example in one cataloged leaf below `examples/`. A leaf normally has
one regular, non-executable UTF-8 file with LF endings. Entrypoints match
`^[a-z][a-z0-9_]*\.py$`, use a globally unique `pyble_*.py` basename, and are
at most 48 UTF-8 bytes. Never use `boot.py`, `main.py`, symlinks, Git LFS,
compiled `.mpy`, or binary assets.

Keep source below 32 KiB and the leaf batch below 128 KiB. Users import into a
bounded category directory below board `/examples` because the firmware rejects
top-level names beginning with `pyble` or `pble`. Remove the example leaf from
the remote parent when deriving the board destination; for example,
`examples/capabilities/gpio/blink_external_led/` maps to
`/examples/capabilities/gpio/`.

Do not flatten the collection. PBLE/1 has one 480-byte, non-paginated directory
listing, and the app refuses import when conflict discovery is truncated. The
repository validator keeps each prescribed category below half that encoded
budget, leaving operational margin for directory metadata or a few user files.

## Required source shape

Start with `# SPDX-License-Identifier: MIT`, followed by a module docstring with
these labels:

```text
Purpose:
Prerequisites:
Wiring:
Settings:
Before you run:
Try this:
Persistent effects:
Expected:
Stop and cleanup:
```

Write the first part for a child who is new to programming. Use short, complete
sentences. Explain a technical word the first time it appears, including units
such as `ms` (milliseconds) and names such as ADC, PWM, RGB, byte, or JSON. Tell
the learner exactly what to look at, what to change, and what a successful run
looks like. Keep protocol, validation, and HIL details after those instructions.
Every labeled section must contain an explanation. Do not use `None` as a
complete wiring or effects explanation.

Define a small `main()` and call it only through:

```python
if __name__ == "__main__":
    main()
```

PyBLE RUN file execution sets `__name__` to `"__main__"`; ordinary imports
therefore remain inert. Keep reusable validation and transformation logic pure
enough for host tests.

## Hardware configuration

Generic examples publish physical pin, bus, and count constants as obvious
unset values. Validate every value—including type, range, distinctness, and
caps—before importing or constructing hardware. Never infer a generic board's
LED, button, pixel, bus, or safe GPIO.

Put a `# SETUP GUIDE` immediately above every block containing an unset
learner-editable constant. It must:

- say that Python `None` means “not chosen yet” and makes the lesson stop safely;
- name every value the learner must change and explain its allowed values and
  units;
- show one complete, comment-only example that is conditional on the exact
  board guide, or name the board or carrier it was checked for;
- say that the recipe is an example, not a profile-wide default, and ask a
  teacher or another adult to check the exact board guide and circuit; and
- end with `# END OF SETUP GUIDE` before ordinary program code.

Write each sample value on its own parseable line, such as
`# BUTTON_PIN = 15`; do not use `YOUR_PIN`, ellipses, or `None` as the sample.
All assignments in one recipe must work together and pass the example's normal
validation function. Repository tests read the comment literals and check that
complete group, so prose-only or internally inconsistent recipes fail CI.

Keep the published pins at `None`; do not turn example fixture pins into
defaults. An exact-board safety confirmation stays `False` until the physical
board and firmware profile are checked, and its guide must explain what changing
it to `True` promises. Distinguish Python `None` from the quoted string
`"none"`: the latter deliberately disables a built-in pull resistor and needs a
reviewed external resistor. Explain later internal uses of `None` as “not
created yet” cleanup bookkeeping when a beginner could mistake them for more
settings.

When one example uses multiple pins, require numeric GPIO identifiers. Named
aliases are not portable and two different spellings can resolve to the same
physical pin, defeating a raw distinctness check.

Fixed wiring is allowed only for the named Waveshare ESP32-S3-LCD-1.47B and
Raspberry Pi Pico 2 W profiles. The Waveshare GPIO38 pixel example must import
the exact-image marker and require explicit confirmation before constructing
the pin. Runtime chip text such as `esp32-s3` is not a profile check.

## Work, effects, and cleanup

Prefer finite, paced work under 30 seconds, 4 KiB console output, and 32 KiB
additional live heap. Stop lessons still need a hard upper bound. Validate
wiring before access; use low brightness and conservative rates; restore
outputs and deinitialize resources in `finally` where supported.

Treat catalog `runtime_seconds_max` and `output_bytes_max` as hard contracts for
source-controlled work under an active PBLE session with a responsive console,
not descriptions of defaults. Budget the 40 ms interval between every physical
console write; `print(text)` sends the body and newline separately. Every value
accepted by a source validator must also leave room for peripheral setup,
cleanup, and final status output. PyBLE v0.6.0 can additionally wait up to
250 ms for each backpressured console-notification attempt. That transport
contingency is not source-controlled and is outside the catalog maximum, so HIL
must record observed wall time and must not turn the maximum into a stalled-link
guarantee. Interactive input may instead use an explicit operator Stop bound
recorded in both source and catalog.

Filesystem examples use reviewed absolute paths below `/examples`, where the
app can manage them, refuse overwrite, and remove only files they created. An
intentionally retained file must be cataloged and clearly announced. Never
read or print unique IDs, MAC addresses, credentials, tokens, labels, or user
secrets. Remember that `input()` visibly echoes typed characters. Make
deliberate errors unmistakable before raising the documented exception.
