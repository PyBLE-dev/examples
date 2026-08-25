<!-- SPDX-License-Identifier: MIT -->

# Changelog

Notable user-facing and repository-governance changes to PyBLE Examples are
recorded here. Examples are versioned independently from the PyBLE app and
firmware. Stable releases will use annotated, signed tags such as
`examples-v0.1.0`; `main` and the Unreleased section are not compatibility
promises.

## Unreleased

No examples release has been published. All 32 source files are implemented in
the development catalog, but every record remains `planned`. The evidence index
and `validated_profiles` are empty; no HIL or live GitHub-import result is
claimed.

### Added

- Established the standalone, MIT-licensed repository for PyBLE's official
  user-facing MicroPython examples.
- Implemented all 32 approved single-file examples: 14 portable, 9 capability,
  6 exact-hardware, and 3 composed project sources.
- Added a strict development catalog and schema with the planned 8/17/7 release
  slices, explicit designed compatibility, and no inferred validation claims.
- Added authoring, compatibility, validation, release, contribution, and
  security guidance, plus a strict initially empty evidence index.
- Added standard-library host tests, a repository validator, a pinned
  `mpy-cross` gate, a Makefile interface, and pull-request CI. The host suite
  exercises portable behavior, repository contracts, and fake-hardware cleanup
  paths; it does not replace hardware validation.
- Added this changelog to record future repository and examples releases.

### Changed

- Reworked all 32 example introductions for young first-time learners with
  explicit `Settings`, `Before you run`, and `Try this` instructions, complete
  sentences for wiring and saved-file effects, and plain explanations of new
  technical words.
- Added nearby, comment-only setup recipes for every deliberately unset
  hardware value. Generic pin choices remain fail-closed at `None`, exact-board
  confirmation remains `False`, and the single-pixel lesson now fixes its
  lesson count at one so learners only choose the reviewed data pin.
- Made recipe examples executable documentation: CI parses every concrete
  comment literal, rejects placeholders and empty child-facing sections, and
  passes each complete settings group through the lesson's own validator.
- Expanded the README to define the repository's ownership boundary,
  implemented development catalog, qualified firmware baseline, safety and
  evidence requirements, validation commands, and contribution workflow.
- Documented the current SHA-pinned GitHub-import constraints and made the
  required non-root destination explicit for implemented `pyble_*.py` files.
  Board imports now use bounded category directories below `/examples` so the
  complete collection cannot overflow PBLE's non-paginated listing response.
- Approved the catalog plan for implementation and recorded which design
  decisions are resolved while keeping HIL, live-import, and release gates
  open.
- Corrected filesystem effects to live below `/examples`, avoiding the
  firmware's reserved top-level `pyble`/`pble` namespace, and documented the
  console's normal visible `input()` echo, four-character Pico transmit-budget
  cap, and operator-enforced Stop bound.
- Extended HIL evidence metadata to distinguish the canonical imported source
  from configured source actually executed on a fixture, including exact
  constant edits, hashes, and an archived executed-source asset.
- Recorded v0.6.0 ESP reused-run-globals and stale-console-input behavior as
  explicit runtime conformance gates; neither host fakes nor compilation is
  presented as closing those app/firmware issues.
- Tightened aggregate runtime and console-output caps, limited press reporting,
  made directory listing token-budget-safe with prompt iterator finalization,
  and preannounced the exact intentional error before its traceback.
- Counted separate console body/newline writes in timing guards, capped each
  SoftI2C clock-stretch wait at one millisecond, documented transport
  backpressure outside source-work timing, and made SoftSPI pin cleanup match
  the pinned runtime's no-op deinit hook.
- Hardened evidence validation so required configuration edits and explicit
  wiring cannot be omitted, JSON booleans cannot satisfy numeric constants, and
  evidence timestamps use strict RFC 3339 UTC.
