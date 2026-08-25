<!-- SPDX-License-Identifier: MIT -->

# PyBLE examples repository and complete catalog plan

- Status: **Implemented; HIL validation and release pending**
- Plan revision: 1.1
- Prepared: 2026-08-25
- Approved: 2026-08-25 by explicit maintainer implementation instruction
- Implementation reconciled: 2026-08-25
- Target repository: `https://github.com/PyBLE-dev/examples`
- Local working copy: `/Users/vyv/Working/SciLabPro/PyBLE-Examples`

> Implementation record: the maintainer explicitly instructed implementation
> of the complete plan on 2026-08-25. All 32 source examples, the development
> catalog/schema, repository validator, host suite, evidence schema, and CI now
> exist. Local host, catalog, and pinned `mpy-cross` gates pass. Every catalog
> validation status remains `planned`; HIL, live app import, and release gates
> remain open.

## 1. Decision recorded

This document is the approved initial scope and architecture for the official
PyBLE example collection. The approval covers:

1. the 32-example catalog and its release grouping;
2. the distinction between portable, capability-based, and exact-hardware
   examples;
3. the rule that a design target is not a validation claim;
4. the safe hardware-configuration and cleanup rules;
5. the repository/catalog layout required by the current GitHub importer; and
6. the deferred and excluded topics.

Approval authorized the completed source implementation. It does not approve
every future example that might be imagined; additions or scope changes update
this plan or a successor roadmap first.

## 2. Goal

Create a clean-room, MIT-licensed, readable MicroPython example collection that
works naturally with PyBLE's GitHub connection and covers all five qualified
firmware profiles without pretending that they share one physical pinout.

The collection should:

- give a new user a short path from GitHub import to Run, Console, and Stop;
- teach portable MicroPython before introducing external wiring;
- expose capabilities only where the shipped firmware actually provides them;
- provide exact examples for the two profiles that name exact physical boards;
- keep every example small enough for BLE transfer and low-memory boards;
- make prerequisites, physical effects, cleanup, and validation status visible;
- remain useful as a manual library even before richer catalog UI exists; and
- provide reproducible evidence for every published compatibility claim.

### Non-goals

This repository will not become a firmware mirror, driver dump, general board
support package, copied vendor tutorial collection, or substitute for PyBLE's
protocol and firmware specifications. It will not make USB serial or Wi-Fi the
primary workflow.

## 3. Qualified baseline

The initial plan is pinned to the qualified PyBLE v0.6.0 release:

- PyBLE agent: `0.6.0`
- protocol: `PBLE/1`
- MicroPython: `1.28.0`
- source commit: `0c7230d6708797c241160ba71fbd37e6b22f180a`
- release tag: `firmware-v0.6.0`
- release descriptor SHA-256:
  `c2940281a14feddb55c48de15ac18087e9317d1b7130e514fab5a209b046a1e6`

The five release profile IDs are:

| Profile ID | Kind | Designed example surface |
| --- | --- | --- |
| `esp32-4mb` | Generic firmware profile | Portable examples and explicitly configured generic hardware examples; frozen `neopixel` |
| `esp32-s3-n16r8` | Generic firmware profile | Portable examples and explicitly configured generic hardware examples; frozen `neopixel` |
| `waveshare-esp32-s3-lcd-147b` | Exact Waveshare ESP32-S3-LCD-1.47B profile | Portable/generic examples, frozen `neopixel`, exact LCD and onboard-pixel examples |
| `esp32-c3-4mb` | Generic firmware profile | Portable examples and explicitly configured generic hardware examples; frozen `neopixel` |
| `rpi-pico2-w` | Exact Raspberry Pi Pico 2 W profile | Portable/generic examples and exact named onboard-LED examples |

These are firmware profiles, not five interchangeable carrier-board pin maps.
The three generic profiles must never acquire an implied onboard LED, button,
pixel, bus, or safe GPIO from this repository. A qualification carrier's wiring
is test-fixture evidence, not a public profile promise.

Both S3 images report the runtime chip as `esp32-s3`, although only the exact
Waveshare image includes its board-specific display support. Therefore neither
the current app nor example code may infer the exact profile from the chip name.

### Capability groups used below

| Code | Designed compatibility |
| --- | --- |
| `A5` | All five profiles |
| `E4` | The four ESP profiles: `esp32-4mb`, `esp32-s3-n16r8`, `waveshare-esp32-s3-lcd-147b`, and `esp32-c3-4mb` |
| `W1` | `waveshare-esp32-s3-lcd-147b` only |
| `P1` | `rpi-pico2-w` only |

`A5`, `E4`, `W1`, and `P1` express intended compatibility. Catalog records
separately list profiles on which the exact source revision has passed
hardware-in-the-loop (HIL) validation. Those lists are currently empty; no row
below is a completed validation claim.

The current common runtime surface is sufficient for the implemented portable
set, including `machine`, `asyncio`, `array`, `binascii`, `collections`,
`framebuf`, `gc`, `hashlib`, `io`, `json`, `math`, `os`, `random`, `re`,
`struct`, `sys`, and `time`. The ESP profiles additionally provide `esp`,
`esp32`, and `neopixel`. Pico provides `rp2`, but PIO remains deferred until
its lifecycle and Stop behavior are specified. Examples must not silently
bundle around a missing firmware module.

## 4. Design principles

1. **Capability before chip family.** Reuse one source file when the APIs and
   safety contract are genuinely the same. Do not copy an example into five
   nearly identical board folders.
2. **Exact hardware only when exact hardware is named.** Fixed board pins are
   allowed for the Waveshare and Pico 2 W exact profiles only.
3. **Configured generic hardware.** Generic GPIO, PWM, ADC, I2C, and SPI
   examples ship with visibly unset configuration values and refuse to touch
   hardware until the user supplies and reviews them.
4. **Safe by default.** Work and console output are bounded; output devices are
   returned to an inactive state; resources are deinitialized where the port
   supports it; files are never silently overwritten.
5. **Readable source.** Only source `.py` examples are shipped. Each is small,
   starts with child-facing settings and run instructions, explains new words,
   and is useful without generated assets or compiled `.mpy` files.
6. **The constrained profiles define portability.** Common examples are checked
   on classic ESP32, ESP32-C3, and Pico 2 W, not just an S3 with PSRAM.
7. **Evidence, not implication.** `designed_profiles` and `validated_profiles`
   remain separate throughout the catalog, documentation, UI, and releases.
8. **Clean-room authorship.** Examples, explanations, identifiers, pin policies,
   and tests are authored fresh from PyBLE's public contracts. Unknown-licensed
   or proprietary examples are not adapted.

## 5. Repository layout

The implementation uses this shape:

```text
.
├── .github/
│   └── workflows/
├── catalog/
│   ├── examples.json
│   └── examples.schema.json
├── docs/
│   ├── authoring.md
│   ├── compatibility.md
│   ├── release-policy.md
│   ├── validation.md
│   └── planning/
│       └── examples-catalog-plan.md
├── examples/
│   ├── portable/
│   │   ├── basics/<example>/
│   │   ├── data/<example>/
│   │   └── workflow/<example>/
│   ├── capabilities/
│   │   ├── gpio/<example>/
│   │   ├── buses/<example>/
│   │   └── neopixel/<example>/
│   ├── exact_hardware/
│   │   ├── waveshare_esp32_s3_lcd_147b/<example>/
│   │   └── rpi_pico2_w/<example>/
│   └── projects/<example>/
├── tests/
├── tools/
├── validation/
├── AGENTS.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
└── SECURITY.md
```

Each `<example>` is a leaf directory containing one runnable `.py` file; all 32
implemented examples are single-file.
Explanatory information required at import time lives in the module docstring
and catalog, because the current app does not preview a leaf README. A
multi-file local-module lesson is deferred until the runner defines a reliable
script-directory import contract.

No submodule links the examples repository to the app/firmware repository. The
repositories have different release cadences and are connected by immutable
catalog metadata instead.

## 6. Current PyBLE GitHub-import contract

The catalog and file layout must work with the app that exists now, not depend
on a future catalog feature:

- the user connects a public canonical GitHub repository root URL;
- an optional Git ref can be resolved and pinned to a commit;
- navigation is lazy and folder-based;
- only direct, regular, lowercase `.py` blobs in the open folder are importable;
- selected files are flattened by basename into the board's current working
  directory; remote subdirectories are not recreated;
- PBLE returns one non-paginated directory listing capped at 480 response
  bytes, and the importer refuses conflict checks against a truncated listing;
- one file must be no larger than 256 KiB, the selected batch no larger than
  1 MiB, and a target path no longer than 128 UTF-8 bytes;
- source must be valid UTF-8 and contain no NUL byte;
- all selected files are fetched before writes begin, but board writes are
  sequential rather than transactionally atomic;
- the app does not automatically open or run an imported file; and
- the app does not yet persist complete source provenance on the board.

The repository deliberately uses narrower limits:

| Item | Repository limit |
| --- | --- |
| Example filename | `^[a-z][a-z0-9_]*\.py$`, globally unique, at most 48 UTF-8 bytes |
| Typical source file | At most 32 KiB; a larger exception needs review and an explicit catalog limit |
| Importable leaf batch | At most 128 KiB |
| Entry point | A uniquely named `pyble_*.py`; never `boot.py` or `main.py` |
| Git object | Regular non-executable mode `100644`; no symlink, submodule, or Git LFS pointer |
| Encoding | UTF-8, LF line endings, no NUL byte |

Global filename uniqueness prevents two examples imported at different times
from unexpectedly overwriting one another. Implemented `pyble_*.py` entrypoints
cannot be written at board root because PyBLE reserves top-level `pyble` and
`pble` prefixes. The 32 basenames also cannot safely share one `/examples`
directory: their encoded FILE_LIST payload needs 1,018 bytes and would be
truncated, blocking later imports.

Documentation therefore requires bounded board category directories derived
by removing the example leaf from its remote parent. For example,
`examples/portable/basics/hello_console/` maps to
`/examples/portable/basics/`. This produces nine import destinations; the
largest complete catalog listing needs 186 payload bytes, below the enforced
240-byte repository budget and leaving margin within PBLE's response. Users
create each directory level through Files because import does not call
`mkdir`. Source must not assume that the runner changes
the MicroPython VM's working directory to the Files UI/import destination or
adds the executed file's parent to `sys.path`. Filesystem examples therefore
use reviewed absolute paths, and the initial roadmap does not rely on sibling
module imports.

## 7. Complete implemented example catalog

All 32 entries below have source files and development catalog records. They
remain grouped into the first three planned releases: `v0.1` establishes the
portable, capability, and exact-hardware paths; `v0.2` adds the language, data,
workflow, and configured-hardware library; and `v0.3` adds composed projects
and deeper exact-hardware coverage. No release tag or HIL claim exists yet.

The approved stable IDs and basenames below must not be casually renamed.

### 7.1 v0.1 — first usable collection (8 examples)

| Stable ID | Entrypoint | Purpose | Group | Requirements and safety |
| --- | --- | --- | --- | --- |
| `portable-hello-console` | `pyble_hello_console.py` | First import, Run, and console output | `A5` | Core Python; one bounded message; no hardware or files |
| `portable-paced-counter` | `pyble_paced_counter.py` | Variables, a finite loop, and pacing | `A5` | `time.sleep_ms`; finite duration and small output |
| `portable-runtime-info` | `pyble_runtime_info.py` | Show implementation, platform, and free heap | `A5` | `sys`, `os`, `gc`; never prints MAC address, `machine.unique_id()`, label, or another identifier |
| `portable-file-round-trip` | `pyble_file_round_trip.py` | Create, verify, and remove a tiny text file safely | `A5` | Uses `/examples/pyble_example_round_trip.txt`, which remains visible through the app's filesystem jail; refuses overwrite; requires no concurrent Files mutation; removes the verified path and explains possible residue |
| `gpio-blink-external-led` | `pyble_gpio_blink.py` | Configurable digital output with an external LED | `A5` | Unset pin; external LED/resistor; finite toggles; inactive in `finally` |
| `neopixel-single-pixel` | `pyble_neopixel_single.py` | Construct and update one addressable pixel | `E4` | Unset data pin; fixed count of one; dim finite colors; pixel off in `finally` |
| `pico2w-onboard-led` | `pyble_pico2w_onboard_led.py` | Use the Pico 2 W's named onboard LED | `P1` | `machine.Pin("LED")`; finite blink; LED off in `finally` |
| `waveshare-lcd147b-hello` | `pyble_waveshare_lcd147b_hello.py` | Show a bounded hello frame on the exact B-version LCD | `W1` | Qualified display helper/wiring only; bounded display time; backlight off and display deinitialized in `finally` |

Release intent: a new user can verify the app workflow without wiring, while
maintainers can prove portable, configured-capability, and exact-board catalog
paths before scaling the collection.

### 7.2 v0.2 — portable language, workflow, and data (10 examples)

| Stable ID | Entrypoint | Purpose | Group | Requirements and safety |
| --- | --- | --- | --- | --- |
| `portable-data-decisions` | `pyble_data_decisions.py` | Values, strings, collections, and branching in one coherent example | `A5` | Core Python; bounded console output |
| `portable-reusable-functions` | `pyble_reusable_functions.py` | Parameters, return values, and reuse | `A5` | Core Python; deterministic bounded output |
| `portable-error-handling` | `pyble_error_handling.py` | Validate data and handle one deliberate exception | `A5` | Catches only the expected error; no persistent effect |
| `portable-console-input` | `pyble_console_input.py` | One prompt/response through the PyBLE console | `A5` | `input()` echoes and transiently retains the line before source validation; operator enters at most four printable ASCII, non-secret characters to fit the Pico console budget and uses Stop within 120 seconds if unanswered; publish only after five-profile Run/Stop HIL |
| `portable-json-data` | `pyble_json_data.py` | Encode and decode a small in-memory object | `A5` | `json`; no filesystem write; bounded output |
| `portable-async-cooperation` | `pyble_async_cooperation.py` | Run two finite, paced cooperative tasks | `A5` | `asyncio`; finite tasks; runner and Stop interaction require five-profile HIL |
| `portable-binary-data` | `pyble_binary_data.py` | Pack, inspect, and unpack one small binary record | `A5` | `struct` and `binascii`; in-memory only; fixed-size data and bounded hexadecimal output |
| `workflow-stop-a-program` | `pyble_stop_a_program.py` | Practice stopping a visibly active but bounded program | `A5` | Paced counter with a hard maximum duration; cleanup remains safe if Stop interrupts it |
| `workflow-expected-error` | `pyble_expected_error.py` | Recognize an intentional runner traceback | `A5` | Prints intent, then raises one documented `ValueError`; filename and docstring make the failure unmistakable |
| `filesystem-list-directory` | `pyble_list_directory.py` | List one explicit board directory without modifying it | `A5` | `gc`, `os`; reviewed absolute path (default `/`); never assumes the VM working directory matches the Files UI; non-recursive, scans at most 21 entries, renders at most 20 sanitized names on one bounded physical line, then releases and collects the iterator |

### 7.3 v0.2 — configured hardware capabilities (7 examples)

Every pin or bus value in this section is unset in implemented source. The code
validates configuration before constructing a peripheral. HIL uses
operator-supplied fixture values without turning those values into defaults.
Each source puts a complete comment-only setup recipe beside those values. The
recipe is labeled as one board example and requires an adult check; it is not a
portable pin-map claim.

| Stable ID | Entrypoint | Purpose | Group | Requirements and safety |
| --- | --- | --- | --- | --- |
| `gpio-read-external-button` | `pyble_gpio_button.py` | Read a pulled digital input for a bounded period | `A5` | Explicit pin and documented low-voltage button circuit; finite, paced output |
| `gpio-button-controls-led` | `pyble_gpio_button_led.py` | Combine input, branching, and output | `A5` | Two distinct pins; button plus external LED/resistor; LED inactive in `finally` |
| `gpio-pwm-fade` | `pyble_gpio_pwm_fade.py` | Change PWM duty gradually | `A5` | Explicit PWM-capable pin; bounded frequency/duty; output off and PWM deinitialized |
| `gpio-adc-sampling` | `pyble_gpio_adc_sampling.py` | Take raw and 0-to-1 scaled ADC readings | `A5` | Explicit ADC-capable pin; external voltage must remain within the board/pin limit; read only |
| `bus-i2c-scan` | `pyble_i2c_scan.py` | Discover addresses on an explicitly wired bus | `A5` | `machine.SoftI2C`; explicit SDA/SCL and pull-ups; reviewed low-voltage bus; one bounded scan |
| `bus-spi-loopback` | `pyble_spi_loopback.py` | Verify SCK/MOSI/MISO using a loopback jumper | `A5` | `machine.SoftSPI`; distinct explicit pins; finite payload; deinitialize where supported |
| `neopixel-strip-chase` | `pyble_neopixel_chase.py` | Index pixels in a finite moving pattern | `E4` | Explicit pin/count; capped count and iterations; low brightness; entire strip off in `finally` |

`A5` here means the code is designed for the common MicroPython API on all five
profiles when the user supplies suitable external hardware and pins. It does
not promise that an arbitrary carrier board exposes every capability.

### 7.4 v0.3 — exact hardware and composed projects (7 examples)

| Stable ID | Entrypoint | Purpose | Group | Requirements and safety |
| --- | --- | --- | --- | --- |
| `pico2w-onboard-led-patterns` | `pyble_pico2w_led_patterns.py` | Compose reusable functions into finite patterns on the named LED | `P1` | Uses only `Pin("LED")`; bounded patterns; LED off in `finally` |
| `waveshare-lcd147b-shapes` | `pyble_waveshare_lcd147b_shapes.py` | Demonstrate fill, pixel, line, rectangle, text, and show operations | `W1` | Exact display contract; bounded frame; backlight off and display deinitialized |
| `waveshare-lcd147b-onboard-pixel` | `pyble_waveshare_lcd147b_pixel.py` | Use the exact board's WS2812 on GPIO38 | `W1` | Requires an inert `pyble_waveshare_lcd147b` marker import and explicit exact-board confirmation before constructing GPIO38; dim finite sequence; pixel off |
| `project-button-press-counter` | `pyble_project_button_counter.py` | Debounce and count button presses for a finite interval | `A5` | Explicit input pin; bounded observation and paced console output |
| `project-adc-data-logger` | `pyble_project_adc_logger.py` | Combine ADC sampling with a small CSV-style log | `A5` | Explicit ADC configuration; fixed sample/byte caps; refuses to overwrite `/examples/pyble_adc_log.csv`, which remains visible through the app's filesystem jail; intentionally retains it for inspection |
| `project-button-neopixel` | `pyble_project_button_neopixel.py` | Combine button input and pixel feedback | `E4` | Explicit distinct pins/count; finite, dim output; strip off in `finally` |
| `project-waveshare-lcd147b-dashboard` | `pyble_waveshare_lcd147b_dashboard.py` | Refresh time and free-memory data in a few display frames | `W1` | No unqualified sensor assumption; paced bounded refresh; display cleanup |

### 7.5 Coverage summary

| Profile | Unchanged portable examples | Configured generic examples | Profile-specific examples |
| --- | ---: | ---: | ---: |
| `esp32-4mb` | 14 | 9 GPIO/bus/project + 3 NeoPixel | 0; it is a generic profile |
| `esp32-s3-n16r8` | 14 | 9 GPIO/bus/project + 3 NeoPixel | 0; it is a generic profile |
| `waveshare-esp32-s3-lcd-147b` | 14 | 9 GPIO/bus/project + 3 NeoPixel | 4 exact LCD/onboard-pixel examples |
| `esp32-c3-4mb` | 14 | 9 GPIO/bus/project + 3 NeoPixel | 0; it is a generic profile |
| `rpi-pico2-w` | 14 | 9 GPIO/bus/project | 2 exact onboard-LED examples |

The counts overlap where a composed project uses a capability. They describe
implemented design coverage, not passed HIL validation.

## 8. Exact-hardware contracts

### Waveshare ESP32-S3-LCD-1.47B

Only `waveshare-esp32-s3-lcd-147b` examples may assume this qualified wiring:

- ST7789V3, 172 × 320 pixels, X offset 34;
- `SPI(1)`, 40 MHz, mode 0;
- MOSI GPIO45, SCLK GPIO40, CS GPIO42, D/C GPIO41;
- reset GPIO39 and active-high backlight GPIO46;
- BGR color order and display inversion enabled; and
- onboard WS2812 data on GPIO38.

Examples must not use `SPI(2)`, which reset the qualified runtime. GPIO45 and
GPIO46 are strapping pins, so module import must be electrically inert and all
configuration happens inside the explicit run path. The current scope does not
claim touch, SD, IMU, battery, display rotation, or PWM backlight support.
The GPIO38 pixel example must first import the exact-image-only
`pyble_waveshare_lcd147b` marker and require an explicit user confirmation; its
folder name and the ambiguous `esp32-s3` runtime chip value are not safety
guards.

### Raspberry Pi Pico 2 W

The exact onboard LED is addressed as `machine.Pin("LED")`; it is not assigned a
made-up numeric RP2350 GPIO. Pico NeoPixel examples are withheld because the
v0.6.0 Pico manifest does not freeze or claim the `neopixel` module.

## 9. Catalog contract

`catalog/examples.json` is the machine-readable source of truth and
`catalog/examples.schema.json` is its strict schema. Each record includes:

| Field | Meaning |
| --- | --- |
| `id`, `title`, `summary` | Stable identity and human-readable discovery text |
| `path`, `entrypoint`, `files` | Repository location and complete import set |
| `category`, `level`, `concepts` | Navigation and teaching progression |
| `classification` | `portable`, `capability`, `exact-hardware`, or `project` |
| `designed_profiles` | Profiles intended by design; never synthesized from runtime `chip` |
| `validated_profiles` | Profiles with passing evidence for this exact example revision |
| `known_incompatible` | Explicit profile/reason pairs |
| `requires` | Modules, capabilities, external components, wiring/configuration, and app behavior |
| `effects` | Pins driven, files created, output produced, expected duration, and cleanup |
| `minimum_firmware`, `protocol` | Compatibility floor, initially v0.6.0 and PBLE/1 |
| `limits` | Source bytes, expected heap/output/runtime, and hardware-specific caps |
| `validation` | Status plus links/IDs for host and HIL evidence |
| `license` | `MIT` and source SPDX conformance |

The JSON Schema rejects unknown fields (`additionalProperties: false`) and
enumerates all profile IDs and controlled capability terms. Validation states
are `planned`, `host_passed`, `hil_passed`, `not_applicable`, or
`known_incompatible`. An example cannot list a profile in
`validated_profiles` without matching immutable evidence.

The catalog has development status, all 32 records have validation status
`planned`, every `validated_profiles` list is empty, and
`validation/index.json` contains no evidence records. Passing local host gates
does not change those evidence-backed fields automatically.

Catalog runtime and output maxima are hard source-work contracts over every
configuration accepted by the validators, under an active PBLE session with a
responsive console. Aggregate checks reserve the 40 ms interval between every
physical console write—including separate `print()` body and newline
writes—plus setup, cleanup, and final status output; they do not merely describe
the published defaults. PyBLE v0.6.0 may additionally spend up to 250 ms on each
backpressured console-notification attempt. That transport contingency is
outside source control and the catalog maximum is therefore not a universal
stalled-link wall-clock guarantee; HIL records observed wall time. The
console-input lesson is the explicit interactive exception and records its
operator-enforced Stop and transmit-budget bounds.

The app may later consume a versioned catalog to provide filtering or prefill a
repository URL/ref. That is a separate PyBLE app specification change. This
repository will not silently auto-select an exact profile from the current
runtime chip string.

## 10. Example source contract

Every implemented runnable example is required to:

- carry `SPDX-License-Identifier: MIT`;
- begin with a concise docstring containing purpose, prerequisites, wiring,
  settings, pre-run steps, one safe change to try, persistent effects, expected
  observation, and Stop/cleanup behavior;
- write the opening instructions for a child, using complete sentences and
  explaining each new technical word or unit before relying on it;
- define a small `main()` behind the verified
  `if __name__ == "__main__":` runner guard and remain inert on import;
- validate all user configuration before opening a peripheral or driving a pin;
- prefer finite work; a Stop lesson must also have a hard time/iteration bound;
- pace console and peripheral updates;
- cap allocations and work comfortably on the binding low-memory profiles;
- close/deinitialize resources and restore inactive outputs in `finally` where
  the runtime permits it;
- avoid hardware access in callbacks unless separately reviewed;
- avoid unique IDs, MAC addresses, credentials, tokens, or user-entered secrets;
- use reviewed absolute filesystem paths below `/examples` so the files remain
  manageable through the app, refuse to overwrite an existing file, and delete
  only a file it created; and
- make expected failures unmistakable in its filename, docstring, and output.

Every learner-editable `None` or `False` hardware value must have a nearby
`SETUP GUIDE`. The guide explains why the lesson stops safely, names all values
and allowed ranges, shows one internally consistent comment-only recipe that is
conditional on the exact board guide or names its checked carrier, requires a
teacher or adult to check it, and marks its end before program logic. Generic
pins remain unset in published source. A quoted `"none"` pull setting is
explained separately from Python `None`.
Each sample uses one parseable `# CONSTANT = literal` line per setting. Host
tests read every complete recipe and pass the values through the source's own
configuration validator.

Portable examples should normally remain below 32 KiB of additional live heap.
Any example that needs more must state and validate a profile-specific budget.
Console output should normally remain below 4 KiB and execution below 30
seconds. Explicit interactive/Stop examples may use a documented larger runtime
but must remain paced and bounded.

Hardware documentation must tell the user to confirm voltage, current limit,
pin capability, boot/strapping conflicts, and a shared ground. LEDs need a
resistor. I2C needs suitable pull-ups. No example assumes that the app can
protect a user from unsafe physical wiring.

## 11. Validation and evidence plan

### Pull-request gates

The repository validator and host suite verify:

1. the catalog JSON against a strict schema;
2. every tracked `.py` is cataloged and every catalog file exists;
3. stable IDs, paths, and case-folded basenames are unique;
4. filename, file-mode, path-length, encoding, NUL, size, batch, and bounded
   board-category FILE_LIST limits;
5. no symlink, submodule, executable source, LFS pointer, generated `.mpy`, or
   firmware binary appears in the importable tree;
6. SPDX, unique-identifier, and credential-like constant gates;
7. compilation with the matching pinned `mpy-cross`, with all output kept in a
   temporary untracked directory;
8. bounded host tests for portable logic and faked hardware behavior, including
   completion, Stop, and cleanup paths;
9. declared imports and capabilities against the pinned profile module matrix;
10. source-level checks for forbidden names/modules, hardware-import inertia,
    constant-true loops, and absolute declared filesystem effects; and
11. catalog/source agreement for inventory, modules, runtime caps, nonempty
    child-facing docstring sections, and parseable setup recipes that pass each
    example's configuration validator.

Run the implemented gates with:

```sh
make test
make validate-host
make validate-mpy MPY_CROSS=/absolute/path/to/pinned/mpy-cross
```

At this implementation revision, the standard-library host suite passes, the
repository validator accepts all 32 examples, and all 32 compile with
`mpy-cross` from pinned MicroPython 1.28.0. These results cover repository
contracts, portable behavior, and fake-hardware behavior; they do not execute
physical hardware or establish a catalog `host_passed`/`hil_passed` evidence
record.

Source audit also identified two v0.6.0 runtime gates that this repository
cannot close by inspection: the ESP native runner reuses its globals across
sequential RUN operations, and console input may be queued outside a run and
persist until VM reset. Five-profile conformance must cover fresh `__main__`
state, sequential-run heap/behavior, stale input, echo/history, overflow,
prompt Stop recovery, and continued PBLE responsiveness. Until an upstream
fix or equivalent evidence exists, development evaluation uses a fresh soft
reboot and sends console input only after the prompt.

### Hardware-in-the-loop gates

For a profile to enter `validated_profiles`, evidence must bind:

- example repository commit and validator-verified canonical source SHA-256
  values;
- the executed board-source SHA-256 values, exact approved constant edits, and
  an archived configured-source asset whenever execution differs from the
  imported canonical source;
- firmware release/tag, source commit, and release descriptor SHA-256;
- exact firmware `profile_id` and, for generic profiles, the named test carrier;
- wiring, external components, and fixture/harness revision;
- PyBLE app version, host platform/device, and GitHub import URL plus resolved
  commit;
- expected and observed console, file, pin, pixel, or display behavior;
- the expected terminal runner state: completion, Stop, or the one documented
  intentional error; cleanup/final state and BLE reconnection/continued
  usability;
- validator version, operator, UTC timestamp, and result.

Every configurable example record must include all published unset constants
(and exact-board confirmation where applicable) in `configuration_edits`.
Wiring is never an empty evidence field: portable records explicitly state that
no external wiring was used. UTC timestamps use RFC 3339 `Z` form.

The first portable release must be run from identical source on all five
profiles. Generic hardware examples need HIL on every profile they claim, using
declared fixture pins. Exact examples need their exact named board. Each release
also gets at least one live GitHub-import path test on the supported iPad and
Android app surfaces; importing files by another mechanism is not sufficient
evidence for the end-to-end path.

## 12. Delivery sequence

The explicit instruction to implement the complete catalog allowed source work
for all three slices in one topic branch. It did not collapse their evidence or
release gates.

| Milestone | Status | Outcome or remaining gate |
| --- | --- | --- |
| M0 — governance | Implemented | Plan approval, contributor/security guidance, authoring/validation contracts, schema, and release policy exist |
| M1/M2 — catalog and validator | Implemented outcome | Strict schema, 32-record catalog, evidence schema, tests, and validator exist and pass local gates; CI is configured; separate red/green commit history is not claimed by this working tree |
| M3 — v0.1 sources | Source implemented | All eight sources pass repository and compilation gates; HIL and live-import evidence remain open |
| M4 — v0.1 release | Not started | Licensing/release audit, complete HIL matrix, live iPad/Android import, frozen evidence, signed tag, and release changelog are required |
| M5 — v0.2 sources | Source implemented | All 17 sources exist; repository/compilation gates pass, while hardware and live-import evidence remain open |
| M6 — v0.3 sources | Source implemented | All seven sources exist; repository/compilation gates pass, while hardware and live-import evidence remain open |

Commits are DCO-signed (`git commit -s`) and use the PyBLE prefixes `[red]`,
`[green]`, `[refactor]`, `[docs]`, `[build]`, or `[chore]`.

## 13. Versioning and cross-repository policy

- `main` represents the newest reviewed source, not necessarily a released
  compatibility promise.
- Stable releases use annotated, signed tags such as `examples-v0.1.0`.
- Each release records the compatible immutable PyBLE firmware descriptor; it
  does not infer compatibility from changing prose or scrape another repo at
  runtime.
- User-facing instructions recommend a release tag or resolved commit for a
  reproducible import. The mutable default branch is for evaluating current
  work.
- A new firmware profile, MicroPython version, module set, runner behavior, or
  importer contract triggers compatibility review and targeted revalidation.
- App integration remains opt-in and specification-driven. The examples repo
  can work through today's generic GitHub navigator without a coordinated app
  release.

## 14. Deferred and excluded scope

The following are intentionally not in the 32-example implementation roadmap:

| Topic | Decision and reason |
| --- | --- |
| Raw BLE/GATT | Excluded: the PyBLE agent owns the BLE peripheral workflow |
| Wi-Fi, HTTP, MQTT, cloud, credentials | Deferred until BLE coexistence, lean-module availability, secret handling, and licensing are designed |
| Generic onboard LED/button/default pin | Excluded: generic profiles do not define carrier routing |
| Pico NeoPixel | Deferred until the Pico module/capability claim is closed with runtime and HIL evidence |
| Waveshare QMI8658, touch, SD, battery, rotation, PWM brightness | Deferred: not part of the current qualified display surface |
| Sibling-module/multi-file lesson | Deferred until RUN defines or supplies a reliable script-directory import path; the Files UI directory is not the VM working directory |
| UART, hard IRQ/timer callbacks, `_thread`, PIO | Deferred pending runner, Stop, callback-allocation, and cross-port safety contracts |
| Watchdog, deep sleep, reset, CPU-frequency changes | Excluded from the initial roadmap because they disrupt the agent or connection lifecycle |
| `boot.py`, `main.py`, autorun | Excluded: imports must not silently change board boot behavior |
| Raw flash, NVS, partitions, bootloader, destructive filesystem operations | Excluded for safety and recovery reasons |
| Motors, relays, servos, heaters, mains, high-power loads | Deferred to a separately reviewed electrical-safety scope |
| Unbounded loops/output or high-brightness pixel demos | Excluded by source and safety contracts |
| Copied vendor examples/drivers or unknown-licensed pedagogy | Excluded by clean-room and MIT licensing rules |
| Compiled `.mpy`, firmware binaries, binary example assets | Excluded; examples remain readable source |

Moving a deferred topic into scope requires a contract update, risk review,
catalog addition, automated tests, and appropriate HIL evidence. An excluded
topic requires an explicit maintainer decision to change policy.

## 15. Definition of done

Source presence and passing host gates are implementation milestones, not this
definition of completion. No example or release currently satisfies the HIL,
live-import, and immutable-evidence requirements below.

An individual example is complete only when:

- its planned contract and catalog record are reviewed;
- tests were introduced red and pass after implementation;
- all repository/importer/source/safety gates pass;
- documentation gives child-facing settings and run steps, then states
  prerequisites, effects, observation, and cleanup;
- every `validated_profiles` entry has immutable matching evidence;
- the exact source imports through the live PyBLE GitHub path;
- the expected terminal state—completion, the documented intentional error, or
  Stop—passes, along with cleanup and continued PBLE usability;
- no firmware binary, generated file, credential, or undocumented dependency is
  committed; and
- the changelog records the user-visible addition.

A release is complete only when every catalog claim is internally consistent,
the eight v0.1 examples satisfy their required profile matrix, release evidence
is archived, and an annotated signed tag is published.

## 16. Decision and evidence checklist

- [x] Repository name `PyBLE-dev/examples` and local sibling layout
- [x] The 32 stable example concepts and the 8-example v0.1 slice
- [x] Folder taxonomy and globally unique `pyble_*.py` basenames
- [x] `designed_profiles` separated from evidence-backed
  `validated_profiles`
- [x] Unset edit-before-run configuration for generic physical pins
- [x] Child-facing setup guides and example recipes for every unset setting
- [x] Exact Waveshare and Pico design assumptions
- [x] Narrower source, batch, heap, output, and runtime limits
- [ ] Required HIL matrix for designed release profiles, plus live iPad and
  Android import checks
- [x] Deferred/excluded topics and the process for admitting them later
- [x] Independent release policy bound to immutable firmware metadata

Two governance questions are resolved for this implementation:

1. Generic pin configuration uses obvious unset constants edited and reviewed
   in source. A future app form would be a separate product specification.
2. Small evidence metadata uses the strict checked-in
   `validation/index.json`; bulky immutable evidence belongs in signed release
   assets referenced by that index.

Catalog discovery, compatibility filters, and a prefilled official URL in the
app remain deferred. Any such work needs its own PyBLE app specification and is
not required for the first examples release.

## 17. Upstream sources for this plan

The baseline and constraints are derived from the PyBLE repository at the
pinned v0.6.0 source commit, especially:

- `README.md` and `CHANGELOG.md` for the qualified five-profile release;
- `firmware/versions.lock` and the release descriptor for pinned versions;
- `docs/specifications/hardware.md` for generic versus exact-board contracts;
- `docs/specifications/firmware.md` and the per-port specifications;
- firmware board overlays/manifests for the shipped module surfaces; and
- the app GitHub-source specification and implementation for current navigation,
  transfer, naming, size, and path behavior.

When older frozen specifications still describe a profile as pending, the
current release README, changelog, release decision, and immutable descriptor
control release status; the frozen documents continue to supply their technical
constraints. The implemented catalog and `docs/compatibility.md` preserve this
distinction explicitly.
