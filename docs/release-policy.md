<!-- SPDX-License-Identifier: MIT -->

# Release Policy

PyBLE Examples versions independently from the PyBLE app and firmware. The
`main` branch is the newest reviewed source and is not a compatibility promise.
Stable releases use annotated, signed tags such as `examples-v0.1.0`.

A release freezes the exact example commit and source hashes, catalog/schema
version, compatible immutable firmware descriptor, automated results, HIL
index, live iPad/Android import evidence, licensing audit, and changelog entry.
Every `validated_profiles` claim must resolve to matching immutable evidence.

The proposed sequence is 8 examples in 0.1.0, 17 additions in 0.2.0, and 7
additions in 0.3.0. Implemented source may coexist on `main`, but no planned tag
exists until every gate for that release slice passes. A changed firmware
profile, MicroPython version, module set, importer contract, or runner behavior
triggers compatibility review and targeted revalidation.

Release instructions use a signed examples tag or resolved commit, never a
moving branch, and bind it to the firmware release descriptor rather than
scraping another repository at runtime.
