<!-- SPDX-License-Identifier: MIT -->

# Validation and Evidence

## Automated gates

Run the standard-library host suite and repository validator:

```sh
make test
make validate-host
```

Then compile every entrypoint with `mpy-cross` built from the pinned
MicroPython commit `e0e9fbb17ed6fd06bb76e266ae554784c9c80804` (`v1.28.0`):

```sh
make validate-mpy MPY_CROSS=/absolute/path/to/mpy-cross
```

The gates check the strict catalog schema, one-file leaves, unique IDs and
basenames, path/size/encoding/mode limits, SPDX and docstring contracts, inert
imports, forbidden modules and identifiers, bounded loops, declared
capabilities/effects, child-facing source sections, setup-guide markers and
catalog agreement for every unset setting, parseable concrete recipe literals,
and complete recipe groups through the source validators. They also check the
240-byte repository budget for each prescribed board category listing, host
behavior, and MicroPython compilation. The listing budget leaves margin under
PBLE's one-shot 480-byte response. Compiler outputs are created only in a
temporary directory.

## Required runtime conformance probes

PyBLE v0.6.0 has two cross-layer behaviors that host fakes cannot resolve. The
ESP native runner executes in a reused globals dictionary, unlike the Pico
runner's fresh `{"__name__": "__main__"}` globals. Also, the app can send
console input while no program is running, and the firmware input ring is
cleared on VM reset rather than at each RUN boundary.

Before any release or HIL claim, targeted tests must establish on all five
profiles that:

- a clean and sequential run enters the `__main__` guard, stale globals cannot
  change behavior, and repeated examples remain within their heap budgets;
- console input sent only after the prompt reaches that run, idle/stale bytes
  cannot satisfy it, normal echo/history behavior is observed, and Stop recovers
  an unanswered or overflow-affected prompt; and
- source-work runtime limits hold with a responsive console, while observed
  wall time and any v0.6.0 per-notification backpressure waits are recorded
  separately; and
- a terminal run leaves PBLE responsive and every promised cleanup state holds.

Until an upstream app/firmware correction or equivalent conformance evidence
closes these items, use a fresh soft reboot before evaluating each ESP example
and before the console-input lesson, then send only a short non-secret value
after its prompt. Host tests and `mpy-cross` do not close this gate.

## HIL evidence

Never add a profile to `validated_profiles` from inspection, host tests, or a
previous source revision. One passing record binds all of the following:

- example commit plus a validator-verified SHA-256 for every canonical imported
  source file;
- SHA-256 for every source file actually executed, the exact approved constant
  edits, and an archived configured-source asset when those hashes differ;
- firmware agent, tag, source commit, descriptor SHA-256, and exact profile;
- named carrier for a generic profile, fixture/harness revision, wiring, and
  external components;
- PyBLE app version, host platform/device, public repository URL, and resolved
  examples commit;
- expected and observed console/file/pin/pixel/display behavior;
- terminal state, final cleanup state, BLE reconnection/PBLE responsiveness;
- validator version, operator, UTC timestamp, and result.

For every configurable example, `configuration_edits` must name every published
unset constant (and the exact-board confirmation where applicable), not merely
a subset. A fixed teaching value such as the single-pixel lesson's
`PIXEL_COUNT = 1` is not an HIL edit. Follow the source `SETUP GUIDE` and record
the checked carrier and wiring; its comment-only recipe does not replace fixture
review. `wiring` is always nonempty; portable records state explicitly that no
external wiring was required. Store `timestamp_utc` in RFC 3339 `Z` form.

Portable source must pass unchanged on all five profiles before a portable
release claim. Generic hardware examples require every claimed profile and
reviewed fixture pins. Exact examples require the named board. Each release
also requires live GitHub-import coverage on supported iPad and Android
surfaces; another transfer mechanism is not equivalent.

## Evidence storage

Small metadata records, configuration literals, and hashes belong in
`validation/index.json`. Large, immutable logs, photos, captures, and configured
executed-source snapshots belong in signed release assets referenced by that
index. The validator resolves the canonical files from `example_commit`; it
does not treat an edited board copy as the repository source. Public records
must exclude credentials, device identifiers, private paths, and unrelated
logs. Until those records exist, catalog entries remain host-only and no
examples release may be tagged.
