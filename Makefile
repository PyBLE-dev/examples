# SPDX-License-Identifier: MIT

PYTHON ?= python3
MPY_CROSS ?= mpy-cross
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: test validate validate-host validate-mpy

test:
	$(PYTHON) -m unittest discover -s tests -v

validate-host:
	$(PYTHON) tools/validate_catalog.py

validate-mpy:
	$(PYTHON) tools/validate_catalog.py --mpy-cross "$(MPY_CROSS)"

validate: test validate-host
