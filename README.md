<!-- SPDX-License-Identifier: MIT -->

# PyBLE Examples

> **Status: implemented, unreleased, and not HIL-validated.** The development
> catalog contains all 32 approved source examples, plus schema validation,
> host tests, pinned MicroPython compilation, and CI. Every catalog record
> remains `planned`: there is no examples release tag, HIL evidence, or live
> GitHub-import validation yet. Designed compatibility is not a hardware claim.

This is the official public, MIT-licensed collection of user-facing
MicroPython examples for [PyBLE](https://github.com/PyBLE-dev/PyBLE). The
collection is intended for deliberate import through the PyBLE app, transfer
over PBLE/1, and explicit execution on a connected board.

## Purpose and repository boundary

This repository owns the official runnable example source, catalog
metadata and schema, example-specific tests, hardware-in-the-loop (HIL)
evidence, authoring rules, and independently versioned example releases.

The PyBLE product repository continues to own the app and generic GitHub
importer, PBLE/1, firmware profiles and module contracts, product
documentation, and cross-repository compatibility requirements. Its two small
GitHub-import fixtures and eight bundled offline Blocks examples remain
product-owned assets; they are not this catalog.

The repositories have separate histories and release cadences. This collection
is not a submodule, mirror, build input, firmware component, runtime dependency,
or automatic synchronization target. PyBLE treats it as ordinary untrusted
public input: the official URL receives no allowlist, elevated trust, implicit
ref, profile inference, auto-selection, auto-open, or auto-run behavior. See the
accepted
[repository-separation decision](https://github.com/PyBLE-dev/PyBLE/blob/442fa7f4fdd8d9bd0e09288b17c2958241439f1b/docs/decisions/0041-separate-official-examples-repository.md).

## Implemented catalog and release roadmap

The approved catalog implements 32 clean-room examples grouped into three
planned release slices. The sources exist in this development snapshot, but
the tags and compatibility claims do not.

| Proposed tag | Examples | Scope |
| --- | ---: | --- |
| `examples-v0.1.0` | 8 | First import/run workflow, portable basics, configured capabilities, and both exact-board paths |
| `examples-v0.2.0` | 17 | Language, data, workflow, GPIO, buses, ADC, PWM, and NeoPixel |
| `examples-v0.3.0` | 7 | Deeper exact-hardware examples and bounded projects |

The repository uses this layout:

| Path | Contents |
| --- | --- |
| `examples/portable/` | Board-neutral language, data, and workflow lessons |
| `examples/capabilities/` | GPIO, bus, and NeoPixel examples with explicit configuration |
| `examples/exact_hardware/` | Examples for a specifically named qualified board |
| `examples/projects/` | Bounded projects composed from cataloged primitives |
| `catalog/` | Strict machine-readable example metadata and schema |
| `tests/`, `tools/` | Host behavior checks and the repository validator |
| `validation/` | Strict evidence index; initially empty |

Each example is a leaf directory containing one globally unique, lowercase
`pyble_*.py` entrypoint. Its module docstring and catalog record carry the
prerequisites, wiring, effects, expected result, and cleanup instructions
needed at import time. Multi-file lessons remain deferred until the runner
defines a reliable script-directory import contract.

## Importing with the current PyBLE app

No stable examples release exists yet. To evaluate the current development
sources at your own reviewed immutable commit:

1. Install the matching qualified firmware from the
   [PyBLE installer](https://pyble.dev/flash), then connect the app to the
   board.
2. In **Files**, create and enter the bounded category directory that mirrors
   the remote parent, such as `/examples/portable/basics` for a source below
   `examples/portable/basics/<example>/`. Create each directory level first.
3. Open **Import examples** and enter
   `https://github.com/PyBLE-dev/examples`.
4. Resolve a reviewed immutable commit. No `examples-v*` release tag exists
   yet; mutable `main` is not a compatibility promise.
5. Navigate to an example leaf, select its direct `.py` file, and review the
   pinned commit, exact destination, and any overwrite warning.
6. Complete the import, open the file explicitly, read its docstring and source,
   confirm all wiring and configuration, and then choose **Run**. Observe
   **Console** and use **Stop** when instructed.

**Use bounded category directories below `/examples`; do not flatten the
catalog or import entrypoints at board root.** A non-root destination is
mandatory because PyBLE protects top-level names beginning with `pyble` or
`pble`. Map the remote parent with its example leaf removed: for example,
`examples/portable/basics/hello_console/pyble_hello_console.py` goes to
`/examples/portable/basics/pyble_hello_console.py`.

The hierarchy is also operationally required. PBLE/1 returns a directory in
one 480-byte response and provides no listing pagination; the importer refuses
to write when that response is truncated. All 32 basenames need 1,018 encoded
payload bytes if flattened, while the largest prescribed category needs only
186.
Keep unrelated files out of these category directories. The importer does not
create directories for you; use **Files** to create each level before opening
Import examples.

### Reading and setting up a lesson

Every source starts with a child-facing guide. Read `Settings`, `Before you
run`, and `Try this` before pressing **Run**. Lessons without hardware tell you
that no settings or wires are needed. A good first learning order is: Hello
Console, Paced Counter, Stop a Running Program, Data Decisions, Functions,
Console Input, Error Handling, Expected Error, JSON, File Round Trip, List a
Directory, Runtime Information, Binary Data, and Async Tasks.

Hardware lessons place a `SETUP GUIDE` directly above the values to edit. For
example, a reviewed button recipe may show:

```python
# Pico 2 W example: a button joins GP15 to GND.
# BUTTON_PIN = 15
# BUTTON_PULL = "up"
# PRESSED_LEVEL = 0
BUTTON_PIN = None
BUTTON_PULL = None
PRESSED_LEVEL = None
```

The commented values are one complete example, not defaults for every board.
Edit only the value to the right of `=`, keep quote marks where shown, and ask a
teacher or another adult to check the exact board guide and circuit. Python
`None` means “not chosen yet,” so the example stops before touching a pin. Never
guess a GPIO number or copy one from a different board. Repository tests parse
every published recipe and pass the complete group through that lesson's
settings checker.

### Current importer contract

| Concern | Current behavior |
| --- | --- |
| Source identity | Accepts an unauthenticated canonical public `https://github.com/<owner>/<repo>` URL and resolves an optional ref once to a full commit SHA |
| Browsing | Lazy and non-recursive; at most 512 direct entries and a 2 MiB response per folder |
| Eligible files | Direct ordinary Git blobs (`100644` or `100755`) whose names end in lowercase `.py` |
| Destination | Flattens selected basenames into the Files directory captured when import opens; it does not recreate remote folders or call `mkdir` |
| Board listing | One non-paginated 480-byte PBLE response; import stops rather than trusting a truncated conflict listing |
| Limits | 256 KiB per file, 1 MiB per batch, and 128 UTF-8 bytes per target path; source must be strict UTF-8 without NUL |
| Writes | Fetches and validates the complete batch first, then performs sequential, non-atomic board writes with separate overwrite consent |
| After import | Does not persist a complete local project or provenance record and does not automatically open, save, or run a file |

The current app does not render this repository's catalog or preview a
leaf README. Always inspect the imported source before running it. The complete
importer rationale is recorded in
[ADR-0040](https://github.com/PyBLE-dev/PyBLE/blob/442fa7f4fdd8d9bd0e09288b17c2958241439f1b/docs/decisions/0040-sha-pinned-connected-github-import.md).

## Compatibility baseline

The development catalog targets qualified PyBLE firmware v0.6.0: agent `0.6.0`,
PBLE/1, MicroPython `1.28.0`, source commit
`0c7230d6708797c241160ba71fbd37e6b22f180a`, and tag
[`firmware-v0.6.0`](https://github.com/PyBLE-dev/PyBLE/tree/firmware-v0.6.0).
The immutable
[release descriptor](https://pyble.dev/firmware/v0.6.0/release.json) has
SHA-256
`c2940281a14feddb55c48de15ac18087e9317d1b7130e514fab5a209b046a1e6`.

| Profile ID | Kind | Designed surface |
| --- | --- | --- |
| `esp32-4mb` | Generic | Portable and explicitly configured hardware examples; frozen `neopixel` |
| `esp32-s3-n16r8` | Generic | Portable and explicitly configured hardware examples; frozen `neopixel`; no exact-board display claim |
| `waveshare-esp32-s3-lcd-147b` | Exact board | Portable/configured examples, `neopixel`, and qualified Waveshare display helpers |
| `esp32-c3-4mb` | Generic | Portable and explicitly configured hardware examples; frozen `neopixel` |
| `rpi-pico2-w` | Exact board | Portable/configured examples and the named onboard LED via `Pin("LED")`; no `neopixel` claim |

These profiles are not interchangeable pin maps. Generic profiles never imply
an onboard LED, button, pixel, bus, or safe GPIO. Both S3 firmware images report
the runtime chip as `esp32-s3`, so neither the app nor an example can infer that
the exact Waveshare profile is installed.

Designed compatibility and validated compatibility are separate. A profile
may enter an example's `validated_profiles` only when evidence binds the
exact example source and firmware identities to the profile/carrier, wiring,
app and host device, expected and observed behavior, cleanup state, continued
PBLE responsiveness, and a live GitHub-import run.

## Safety and validation

The implemented sources validate user configuration before hardware access,
keep work and console output bounded, avoid credentials and unique device
identifiers, refuse unsafe file overwrites, and restore outputs or deinitialize
resources in `finally`. Generic hardware examples ship with unset pin or bus
values that the user must review. Each unset value has a nearby setup recipe;
it is a deliberate safety stop, not a missing default.

Catalog runtime maxima bound source-controlled work with a responsive connected
console and include v0.6.0's mandatory 40 ms interval between physical console
writes. They are not stalled-link wall-clock guarantees: the firmware may also
spend up to 250 ms on each backpressured notification attempt. HIL evidence must
record observed wall time separately.

MicroPython's `input()` visibly echoes typed characters through the PyBLE
console and can retain the line transiently in VM readline history. The lesson
therefore requires an operator-limited value of at most four printable ASCII,
non-secret characters and tells the operator to use Stop if unanswered. That
cap also keeps the warning, prompt, echo, and result within the Pico console's
initial transmit budget.
Filesystem examples use explicit paths below `/examples`; root names beginning
with `pyble` or `pble` are reserved by the firmware and are not app-manageable.

No initial example may use `boot.py`, `main.py`, autorun, destructive filesystem
or flash operations, unbounded output, or high-power loads. Hardware guidance
must cover voltage, current limits, pin capability, boot/strapping conflicts,
shared ground, and required protection such as LED resistors or I2C pull-ups.
A roadmap entry or passing host test alone is never a HIL validation claim.

### Automated validation

The standard-library host suite checks catalog contracts, all 14 portable
examples, and hardware examples through pure seams and fakes, including
completion, Stop, and cleanup paths. The repository validator checks all 32
sources, metadata, paths, limits, imports, effects, and evidence consistency.
Compile every source with `mpy-cross` built from pinned MicroPython 1.28.0:

```sh
make test
make validate-host
make validate-mpy MPY_CROSS=/absolute/path/to/mpy-cross
```

Passing these gates is host validation only. It does not execute physical
hardware, prove Stop cleanup on a board, validate the live app import path, or
authorize a release. The catalog therefore retains empty `validated_profiles`
and an empty HIL evidence index.

PyBLE v0.6.0 also requires targeted runtime closure before release: its ESP
native runner reuses globals across runs, while console input can be queued
outside a run and retained until VM reset. During development evaluation, use a
fresh soft reboot before each ESP example and before the console-input lesson;
send the short non-secret input only after its prompt. See
[the validation contract](docs/validation.md#required-runtime-conformance-probes).

## Contributing

The GitHub `main` branch is protected. Create or switch to a topic branch before
editing, push that branch, and merge through a pull request. The current policy
requires one approving review and resolved conversations; a new commit dismisses
stale approvals.

Before opening a pull request, also run:

```sh
git diff --check
git status --short
```

Use DCO-signed commits (`git commit -s`) with one of the established prefixes:
`[red]`, `[green]`, `[refactor]`, `[docs]`, `[build]`, or `[chore]`. Pull
requests should cite the relevant plan section, list checks performed, explain
user-visible or safety effects, and attach immutable HIL and live-import
evidence for every compatibility claim.

Read [CONTRIBUTING.md](CONTRIBUTING.md) and the
[authoring](docs/authoring.md), [compatibility](docs/compatibility.md),
[validation](docs/validation.md), and
[release](docs/release-policy.md) contracts before changing an example. The
[approved catalog plan](docs/planning/examples-catalog-plan.md) records scope;
[CHANGELOG.md](CHANGELOG.md) records user-visible changes. This project is
available under the [MIT License](LICENSE).
