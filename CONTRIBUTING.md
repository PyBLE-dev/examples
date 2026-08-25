<!-- SPDX-License-Identifier: MIT -->

# Contributing to PyBLE Examples

Thank you for improving PyBLE's official MicroPython example collection. Read
the [catalog plan](docs/planning/examples-catalog-plan.md) and
[authoring contract](docs/authoring.md) before changing runnable source.

## Branch and commit workflow

The GitHub `main` branch is protected. Update local `main`, create a topic
branch before editing, and merge only through a pull request. The current rule
requires one approval and resolved conversations; new commits dismiss stale
approvals.

DCO-sign every commit with `git commit -s`. Use an imperative subject beginning
with `[red]`, `[green]`, `[refactor]`, `[docs]`, `[build]`, or `[chore]`.
Introduce a failing contract or behavior test before implementation, make the
smallest passing change, and keep refactoring separate while tests remain green.

## Local checks

The validator and host tests use only the Python standard library:

```sh
make test
make validate-host
```

Compile every entrypoint with the `mpy-cross` built from MicroPython 1.28.0:

```sh
make validate-mpy MPY_CROSS=/absolute/path/to/mpy-cross
```

Also run `git diff --check` and inspect `git status --short`. Generated `.mpy`
files belong only in a temporary directory and must never be committed.

## Example changes

Each example lives in one leaf directory and normally contains exactly one
globally unique, lowercase `pyble_*.py` file. Update `catalog/examples.json`
with the source in the same change. Keep imports inert, validate configuration
before hardware construction, bound runtime and output, and guarantee cleanup.

Write the opening instructions for a child who has never used the feature.
Every docstring needs `Settings`, `Before you run`, and `Try this` sections in
addition to the safety contract. Explain jargon and units in plain language.
Every unset hardware value needs an adjacent `SETUP GUIDE` with one complete,
comment-only board recipe, allowed values, and an adult-check reminder. Keep
unsafe generic pins at `None`; an example pin is not a default.

Never infer a pinout for a generic profile. Do not copy vendor tutorials,
drivers, identifiers, text, or tests; author clean-room code from documented
PyBLE and MicroPython contracts. Record every dependency and license.

## Pull requests

Explain the user-visible goal, relevant plan section, safety effects, persistent
files, and checks performed. Catalog, tests, documentation, and source must
agree. A designed profile is not a validation claim: add a profile to
`validated_profiles` only with immutable evidence satisfying
[the validation contract](docs/validation.md). Screenshots or logs complement
that evidence but do not replace its required identity and cleanup fields.
When HIL edits unset constants, record the exact literals, executed hashes, and
configured-source asset; never replace the canonical commit/hash identity with
the edited board copy.
