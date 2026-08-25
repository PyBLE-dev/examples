<!-- SPDX-License-Identifier: MIT -->

# Security Policy

## Reporting a vulnerability

Report security or safety problems privately through
[GitHub Security Advisories](https://github.com/PyBLE-dev/examples/security/advisories/new).
Do not disclose an unresolved vulnerability in a public issue. Include the
affected example and commit, PyBLE app and firmware versions, board/profile,
reproduction steps, observed impact, and any safe mitigation. Do not attach
credentials, device identifiers, private repository data, or unrelated logs.

Maintainers will acknowledge the report, assess whether the issue also affects
the PyBLE app or firmware, and coordinate separate fixes when repository
ownership crosses that boundary.

## Safety scope

Example code is executable input and must be reviewed before Run. Confirm board
voltage, current limits, pin capability, boot/strapping conflicts, component
polarity, and shared ground. The app cannot make unsafe wiring safe.

Security-sensitive changes include code that accesses identifiers or secrets,
writes persistent files, changes boot behavior, drives hardware without prior
validation, leaves outputs active after Stop/error, or causes unbounded work or
console output. `boot.py`, `main.py`, raw flash/NVS/partition access, reset and
sleep controls, networking, high-power loads, and destructive filesystem
operations are outside the initial collection's approved scope.

Only evidence-backed tagged releases carry compatibility claims. The mutable
`main` branch and an example's designed profile list are not validation or
safety guarantees.
