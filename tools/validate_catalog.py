#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the PyBLE example catalog and importable source tree."""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "catalog" / "examples.json"
DEFAULT_SCHEMA = ROOT / "catalog" / "examples.schema.json"
DEFAULT_EVIDENCE = ROOT / "validation" / "index.json"
DEFAULT_EVIDENCE_SCHEMA = ROOT / "validation" / "index.schema.json"
PROFILES = {
    "esp32-4mb",
    "esp32-s3-n16r8",
    "waveshare-esp32-s3-lcd-147b",
    "esp32-c3-4mb",
    "rpi-pico2-w",
}
ALL_PROFILES = frozenset(PROFILES)
ESP_PROFILES = frozenset(PROFILES - {"rpi-pico2-w"})
WAVESHARE_PROFILE = frozenset({"waveshare-esp32-s3-lcd-147b"})
PICO_PROFILE = frozenset({"rpi-pico2-w"})
EXPECTED_RELEASE_COUNTS = {"0.1.0": 8, "0.2.0": 17, "0.3.0": 7}
EXPECTED_CLASS_COUNTS = {
    "portable": 14,
    "capability": 9,
    "exact-hardware": 6,
    "project": 3,
}
BOARD_LISTING_REPOSITORY_BUDGET_BYTES = 240
EXPECTED_INVENTORY = {
    "portable-hello-console": (
        "0.1.0", "portable", "examples/portable/basics/hello_console",
        "pyble_hello_console.py", ALL_PROFILES,
    ),
    "portable-paced-counter": (
        "0.1.0", "portable", "examples/portable/basics/paced_counter",
        "pyble_paced_counter.py", ALL_PROFILES,
    ),
    "portable-runtime-info": (
        "0.1.0", "portable", "examples/portable/basics/runtime_info",
        "pyble_runtime_info.py", ALL_PROFILES,
    ),
    "portable-file-round-trip": (
        "0.1.0", "portable", "examples/portable/workflow/file_round_trip",
        "pyble_file_round_trip.py", ALL_PROFILES,
    ),
    "gpio-blink-external-led": (
        "0.1.0", "capability",
        "examples/capabilities/gpio/blink_external_led",
        "pyble_gpio_blink.py", ALL_PROFILES,
    ),
    "neopixel-single-pixel": (
        "0.1.0", "capability",
        "examples/capabilities/neopixel/single_pixel",
        "pyble_neopixel_single.py", ESP_PROFILES,
    ),
    "pico2w-onboard-led": (
        "0.1.0", "exact-hardware",
        "examples/exact_hardware/rpi_pico2_w/onboard_led",
        "pyble_pico2w_onboard_led.py", PICO_PROFILE,
    ),
    "waveshare-lcd147b-hello": (
        "0.1.0", "exact-hardware",
        "examples/exact_hardware/waveshare_esp32_s3_lcd_147b/lcd_hello",
        "pyble_waveshare_lcd147b_hello.py", WAVESHARE_PROFILE,
    ),
    "portable-data-decisions": (
        "0.2.0", "portable", "examples/portable/basics/data_decisions",
        "pyble_data_decisions.py", ALL_PROFILES,
    ),
    "portable-reusable-functions": (
        "0.2.0", "portable", "examples/portable/basics/reusable_functions",
        "pyble_reusable_functions.py", ALL_PROFILES,
    ),
    "portable-error-handling": (
        "0.2.0", "portable", "examples/portable/basics/error_handling",
        "pyble_error_handling.py", ALL_PROFILES,
    ),
    "portable-console-input": (
        "0.2.0", "portable", "examples/portable/workflow/console_input",
        "pyble_console_input.py", ALL_PROFILES,
    ),
    "portable-json-data": (
        "0.2.0", "portable", "examples/portable/data/json_data",
        "pyble_json_data.py", ALL_PROFILES,
    ),
    "portable-async-cooperation": (
        "0.2.0", "portable", "examples/portable/workflow/async_cooperation",
        "pyble_async_cooperation.py", ALL_PROFILES,
    ),
    "portable-binary-data": (
        "0.2.0", "portable", "examples/portable/data/binary_data",
        "pyble_binary_data.py", ALL_PROFILES,
    ),
    "workflow-stop-a-program": (
        "0.2.0", "portable", "examples/portable/workflow/stop_a_program",
        "pyble_stop_a_program.py", ALL_PROFILES,
    ),
    "workflow-expected-error": (
        "0.2.0", "portable", "examples/portable/workflow/expected_error",
        "pyble_expected_error.py", ALL_PROFILES,
    ),
    "filesystem-list-directory": (
        "0.2.0", "portable", "examples/portable/workflow/list_directory",
        "pyble_list_directory.py", ALL_PROFILES,
    ),
    "gpio-read-external-button": (
        "0.2.0", "capability",
        "examples/capabilities/gpio/read_external_button",
        "pyble_gpio_button.py", ALL_PROFILES,
    ),
    "gpio-button-controls-led": (
        "0.2.0", "capability",
        "examples/capabilities/gpio/button_controls_led",
        "pyble_gpio_button_led.py", ALL_PROFILES,
    ),
    "gpio-pwm-fade": (
        "0.2.0", "capability", "examples/capabilities/gpio/pwm_fade",
        "pyble_gpio_pwm_fade.py", ALL_PROFILES,
    ),
    "gpio-adc-sampling": (
        "0.2.0", "capability", "examples/capabilities/gpio/adc_sampling",
        "pyble_gpio_adc_sampling.py", ALL_PROFILES,
    ),
    "bus-i2c-scan": (
        "0.2.0", "capability", "examples/capabilities/buses/i2c_scan",
        "pyble_i2c_scan.py", ALL_PROFILES,
    ),
    "bus-spi-loopback": (
        "0.2.0", "capability", "examples/capabilities/buses/spi_loopback",
        "pyble_spi_loopback.py", ALL_PROFILES,
    ),
    "neopixel-strip-chase": (
        "0.2.0", "capability",
        "examples/capabilities/neopixel/strip_chase",
        "pyble_neopixel_chase.py", ESP_PROFILES,
    ),
    "pico2w-onboard-led-patterns": (
        "0.3.0", "exact-hardware",
        "examples/exact_hardware/rpi_pico2_w/onboard_led_patterns",
        "pyble_pico2w_led_patterns.py", PICO_PROFILE,
    ),
    "waveshare-lcd147b-shapes": (
        "0.3.0", "exact-hardware",
        "examples/exact_hardware/waveshare_esp32_s3_lcd_147b/lcd_shapes",
        "pyble_waveshare_lcd147b_shapes.py", WAVESHARE_PROFILE,
    ),
    "waveshare-lcd147b-onboard-pixel": (
        "0.3.0", "exact-hardware",
        "examples/exact_hardware/waveshare_esp32_s3_lcd_147b/onboard_pixel",
        "pyble_waveshare_lcd147b_pixel.py", WAVESHARE_PROFILE,
    ),
    "project-button-press-counter": (
        "0.3.0", "project", "examples/projects/button_press_counter",
        "pyble_project_button_counter.py", ALL_PROFILES,
    ),
    "project-adc-data-logger": (
        "0.3.0", "project", "examples/projects/adc_data_logger",
        "pyble_project_adc_logger.py", ALL_PROFILES,
    ),
    "project-button-neopixel": (
        "0.3.0", "project", "examples/projects/button_neopixel",
        "pyble_project_button_neopixel.py", ESP_PROFILES,
    ),
    "project-waveshare-lcd147b-dashboard": (
        "0.3.0", "exact-hardware",
        "examples/exact_hardware/waveshare_esp32_s3_lcd_147b/lcd_dashboard",
        "pyble_waveshare_lcd147b_dashboard.py", WAVESHARE_PROFILE,
    ),
}
COMMON_PROFILE_MODULES = {
    "asyncio", "binascii", "gc", "json", "machine", "os", "struct",
    "sys", "time",
}
PROFILE_MODULES = {
    "esp32-4mb": COMMON_PROFILE_MODULES | {"neopixel"},
    "esp32-s3-n16r8": COMMON_PROFILE_MODULES | {"neopixel"},
    "waveshare-esp32-s3-lcd-147b": COMMON_PROFILE_MODULES
    | {"neopixel", "pyble_st7789", "pyble_waveshare_lcd147b"},
    "esp32-c3-4mb": COMMON_PROFILE_MODULES | {"neopixel"},
    "rpi-pico2-w": COMMON_PROFILE_MODULES,
}
CONFIGURABLE_CONSTANTS = {
    "gpio-blink-external-led": {"LED_PIN", "LED_ACTIVE_LEVEL"},
    "neopixel-single-pixel": {"PIXEL_PIN"},
    "gpio-read-external-button": {
        "BUTTON_PIN", "BUTTON_PULL", "PRESSED_LEVEL",
    },
    "gpio-button-controls-led": {
        "BUTTON_PIN", "BUTTON_PULL", "PRESSED_LEVEL", "LED_PIN",
        "LED_ACTIVE_LEVEL",
    },
    "gpio-pwm-fade": {"PWM_PIN", "PWM_FREQUENCY_HZ"},
    "gpio-adc-sampling": {"ADC_PIN"},
    "bus-i2c-scan": {"SDA_PIN", "SCL_PIN", "I2C_FREQUENCY_HZ"},
    "bus-spi-loopback": {
        "SCK_PIN", "MOSI_PIN", "MISO_PIN", "SPI_BAUDRATE_HZ",
    },
    "neopixel-strip-chase": {"PIXEL_PIN", "PIXEL_COUNT"},
    "waveshare-lcd147b-onboard-pixel": {"CONFIRM_EXACT_BOARD"},
    "project-button-press-counter": {
        "BUTTON_PIN", "BUTTON_PULL", "PRESSED_LEVEL",
    },
    "project-adc-data-logger": {"ADC_PIN"},
    "project-button-neopixel": {
        "BUTTON_PIN", "BUTTON_PULL", "PRESSED_LEVEL", "PIXEL_PIN",
        "PIXEL_COUNT",
    },
}
DOCSTRING_LABELS = (
    "Purpose:",
    "Prerequisites:",
    "Wiring:",
    "Settings:",
    "Before you run:",
    "Try this:",
    "Persistent effects:",
    "Expected:",
    "Stop and cleanup:",
)
HARDWARE_MODULES = {
    "machine",
    "neopixel",
    "pyble_st7789",
    "pyble_waveshare_lcd147b",
}
FORBIDDEN_MODULES = {
    "bluetooth",
    "network",
    "requests",
    "socket",
    "urequests",
    "umqtt",
    "_thread",
    "rp2",
}
FORBIDDEN_SUFFIXES = {
    ".bin",
    ".elf",
    ".hex",
    ".mpy",
    ".pyc",
    ".uf2",
}
SUPPORTED_SCHEMA_KEYWORDS = {
    "$defs",
    "$id",
    "$ref",
    "$schema",
    "additionalProperties",
    "const",
    "enum",
    "format",
    "items",
    "maxItems",
    "maxLength",
    "maxProperties",
    "maximum",
    "minItems",
    "minLength",
    "minProperties",
    "minimum",
    "pattern",
    "properties",
    "required",
    "title",
    "type",
    "uniqueItems",
}


class ContractError(Exception):
    """A deterministic validation failure."""


class Errors:
    """Collect independent errors so one run gives an actionable report."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.add(message)

    def raise_if_any(self) -> None:
        if self.items:
            lines = "\n".join("- " + item for item in self.items)
            raise ContractError(
                "validation failed with {} error(s):\n{}".format(
                    len(self.items), lines
                )
            )


def _json_key(value: Any) -> tuple[Any, ...]:
    """Return one hashable, JSON-semantic value for equality and uniqueness."""
    if value is None:
        return ("null",)
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, (int, float)):
        return ("number", value)
    if isinstance(value, str):
        return ("string", value)
    if isinstance(value, list):
        return ("array", tuple(_json_key(item) for item in value))
    if isinstance(value, dict):
        return (
            "object",
            tuple(sorted((key, _json_key(item)) for key, item in value.items())),
        )
    raise ContractError("schema comparison received a non-JSON value")


def _json_equal(left: Any, right: Any) -> bool:
    """Compare JSON values without Python's bool/int equality shortcut."""
    return _json_key(left) == _json_key(right)


def _type_matches(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "null":
        return instance is None
    return False


class SchemaSubsetValidator:
    """Evaluate the dependency-free JSON Schema subset used by this repo."""

    def __init__(self, root_schema: dict[str, Any], errors: Errors) -> None:
        self.root_schema = root_schema
        self.errors = errors

    def _resolve(self, reference: str) -> dict[str, Any]:
        if not reference.startswith("#/"):
            raise ContractError("unsupported external JSON Schema ref: " + reference)
        node: Any = self.root_schema
        for raw_part in reference[2:].split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")
            if not isinstance(node, dict) or part not in node:
                raise ContractError("unresolved JSON Schema ref: " + reference)
            node = node[part]
        if not isinstance(node, dict):
            raise ContractError("JSON Schema ref is not an object: " + reference)
        return node

    def validate(
        self, instance: Any, schema: dict[str, Any] | None = None, path: str = "$"
    ) -> None:
        schema = self.root_schema if schema is None else schema
        if "$ref" in schema:
            self.validate(instance, self._resolve(schema["$ref"]), path)
            return

        if "const" in schema:
            self.errors.check(
                _json_equal(instance, schema["const"]),
                "{} must equal {!r}".format(path, schema["const"]),
            )
        if "enum" in schema:
            self.errors.check(
                any(_json_equal(instance, item) for item in schema["enum"]),
                "{} is not one of {}".format(path, schema["enum"]),
            )

        expected_type = schema.get("type")
        if expected_type is not None and not _type_matches(instance, expected_type):
            self.errors.add("{} must be {}".format(path, expected_type))
            return

        if isinstance(instance, dict):
            minimum = schema.get("minProperties")
            maximum = schema.get("maxProperties")
            if minimum is not None:
                self.errors.check(
                    len(instance) >= minimum,
                    "{} needs at least {} properties".format(path, minimum),
                )
            if maximum is not None:
                self.errors.check(
                    len(instance) <= maximum,
                    "{} permits at most {} properties".format(path, maximum),
                )
            required = schema.get("required", [])
            for key in required:
                self.errors.check(
                    key in instance,
                    "{} is missing {!r}".format(path, key),
                )
            properties = schema.get("properties", {})
            if schema.get("additionalProperties") is False:
                for key in instance:
                    self.errors.check(
                        key in properties,
                        "{} has unknown property {!r}".format(path, key),
                    )
            elif isinstance(schema.get("additionalProperties"), dict):
                additional_schema = schema["additionalProperties"]
                for key, value in instance.items():
                    if key not in properties:
                        self.validate(
                            value,
                            additional_schema,
                            "{}.{!s}".format(path, key),
                        )
            for key, child_schema in properties.items():
                if key in instance:
                    self.validate(instance[key], child_schema, path + "." + key)

        if isinstance(instance, list):
            minimum = schema.get("minItems")
            maximum = schema.get("maxItems")
            if minimum is not None:
                self.errors.check(
                    len(instance) >= minimum,
                    "{} needs at least {} item(s)".format(path, minimum),
                )
            if maximum is not None:
                self.errors.check(
                    len(instance) <= maximum,
                    "{} permits at most {} item(s)".format(path, maximum),
                )
            if schema.get("uniqueItems"):
                keys = [_json_key(value) for value in instance]
                self.errors.check(
                    len(keys) == len(set(keys)), "{} items must be unique".format(path)
                )
            item_schema = schema.get("items")
            if isinstance(item_schema, dict):
                for index, value in enumerate(instance):
                    self.validate(value, item_schema, "{}[{}]".format(path, index))

        if isinstance(instance, str):
            minimum = schema.get("minLength")
            maximum = schema.get("maxLength")
            if minimum is not None:
                self.errors.check(
                    len(instance) >= minimum,
                    "{} must contain at least {} character(s)".format(path, minimum),
                )
            if maximum is not None:
                self.errors.check(
                    len(instance) <= maximum,
                    "{} must contain at most {} character(s)".format(path, maximum),
                )
            pattern = schema.get("pattern")
            if pattern is not None:
                self.errors.check(
                    re.search(pattern, instance) is not None,
                    "{} does not match {!r}".format(path, pattern),
                )
            if schema.get("format") == "date-time":
                date_time_pattern = (
                    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
                    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?"
                    r"(?:Z|[+-][0-9]{2}:[0-9]{2})$"
                )
                try:
                    parsed = datetime.fromisoformat(
                        instance[:-1] + "+00:00"
                        if instance.endswith("Z")
                        else instance
                    )
                    valid_datetime = (
                        re.fullmatch(date_time_pattern, instance) is not None
                        and parsed.tzinfo is not None
                    )
                except ValueError:
                    valid_datetime = False
                self.errors.check(
                    valid_datetime,
                    "{} must be an RFC 3339 date-time with an offset".format(path),
                )

        if isinstance(instance, int) and not isinstance(instance, bool):
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")
            if minimum is not None:
                self.errors.check(
                    instance >= minimum,
                    "{} must be at least {}".format(path, minimum),
                )
            if maximum is not None:
                self.errors.check(
                    instance <= maximum,
                    "{} must be at most {}".format(path, maximum),
                )


def _guard_calls_main(node: ast.If) -> bool:
    test = node.test
    if not (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "__main__"
    ):
        return False
    return any(
        isinstance(item, ast.Expr)
        and isinstance(item.value, ast.Call)
        and isinstance(item.value.func, ast.Name)
        and item.value.func.id == "main"
        for item in node.body
    )


def _import_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".", 1)[0])
    return names


def _top_level_import_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".", 1)[0])
    return names


def _has_unique_identifier_call(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "unique_id":
            return True
    return False


def _has_unbounded_loop(tree: ast.AST) -> bool:
    return any(
        isinstance(node, ast.While)
        and isinstance(node.test, ast.Constant)
        and bool(node.test.value)
        for node in ast.walk(tree)
    )


def _sensitive_assignment_names(tree: ast.Module) -> set[str]:
    """Return credential-like module constants forbidden in public examples."""
    sensitive = re.compile(
        r"(?:^|_)(?:api_?key|credential|passwd|password|secret|ssid|token)(?:_|$)",
        re.IGNORECASE,
    )
    names: set[str] = set()
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets.extend(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets.append(node.target)
        for target in targets:
            if isinstance(target, ast.Name) and sensitive.search(target.id):
                names.add(target.id)
    return names


def _top_level_literal_assignments(tree: ast.Module) -> dict[str, Any]:
    """Return simple module constants used by published safety gates."""
    values: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                values[target.id] = value
    return values


def _board_category_directory(relative_dir: str) -> str:
    """Derive the bounded board destination from one remote example leaf."""
    return "/" + Path(relative_dir).parent.as_posix()


def _board_listing_payload_bytes(names: set[str]) -> int:
    """Return PBLE FILE_LIST payload bytes after the status byte."""
    return 3 + sum(7 + len(name.encode("utf-8")) for name in names)


def _read_json(path: Path) -> dict[str, Any]:
    duplicate_keys: list[str] = []

    def object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                duplicate_keys.append(key)
            value[key] = item
        return value

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=object_without_duplicate_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError("cannot read {}: {}".format(path, exc)) from exc
    if duplicate_keys:
        raise ContractError(
            "{} contains duplicate JSON properties: {}".format(
                path, sorted(set(duplicate_keys))
            )
        )
    if not isinstance(value, dict):
        raise ContractError("{} must contain a JSON object".format(path))
    return value


def _validate_schema_keywords(
    schema: dict[str, Any], errors: Errors, path: str = "$schema"
) -> None:
    for key in schema:
        errors.check(
            key in SUPPORTED_SCHEMA_KEYWORDS,
            "{} uses unsupported JSON Schema keyword {!r}".format(path, key),
        )
    for container_key in ("properties", "$defs"):
        children = schema.get(container_key, {})
        if isinstance(children, dict):
            for name, child in children.items():
                if isinstance(child, dict):
                    _validate_schema_keywords(
                        child, errors, "{}.{!s}.{}".format(path, container_key, name)
                    )
    for child_key in ("items", "additionalProperties"):
        child = schema.get(child_key)
        if isinstance(child, dict):
            _validate_schema_keywords(child, errors, path + "." + child_key)


def _tracked_modes(root: Path) -> dict[str, str]:
    result = subprocess.run(
        ["git", "ls-files", "-s", "--", "examples"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {}
    modes: dict[str, str] = {}
    for line in result.stdout.splitlines():
        left, _, relative = line.partition("\t")
        fields = left.split()
        if fields and relative:
            modes[relative] = fields[0]
    return modes


def _validate_source(
    root: Path,
    record: dict[str, Any],
    tracked_modes: dict[str, str],
    errors: Errors,
) -> Path | None:
    example_id = record.get("id", "<unknown>")
    relative_dir = record.get("path")
    entrypoint = record.get("entrypoint")
    files = record.get("files")
    if not isinstance(relative_dir, str) or not isinstance(entrypoint, str):
        return None

    errors.check(
        files == [entrypoint],
        "{} files must contain only its entrypoint".format(example_id),
    )
    leaf = root / relative_dir
    source_path = leaf / entrypoint
    errors.check(leaf.is_dir(), "{} leaf directory is missing".format(example_id))
    errors.check(source_path.is_file(), "{} entrypoint is missing".format(example_id))
    if not source_path.is_file():
        return None

    try:
        entries = sorted(item.name for item in leaf.iterdir())
    except OSError as exc:
        errors.add("{} leaf cannot be listed: {}".format(example_id, exc))
        return None
    errors.check(
        entries == [entrypoint],
        "{} leaf must contain exactly {!r}, found {}".format(
            example_id, entrypoint, entries
        ),
    )

    mode = source_path.lstat().st_mode
    errors.check(
        stat.S_ISREG(mode),
        "{} entrypoint must be a regular file".format(example_id),
    )
    errors.check(
        mode & 0o111 == 0, "{} entrypoint must not be executable".format(example_id)
    )
    tracked_mode = tracked_modes.get(source_path.relative_to(root).as_posix())
    if tracked_mode is not None:
        errors.check(
            tracked_mode == "100644",
            "{} tracked Git mode must be 100644, found {}".format(
                example_id, tracked_mode
            ),
        )

    raw = source_path.read_bytes()
    errors.check(
        not raw.startswith(b"version https://git-lfs.github.com/spec/"),
        "{} must not be a Git LFS pointer".format(example_id),
    )
    errors.check(b"\x00" not in raw, "{} contains a NUL byte".format(example_id))
    errors.check(b"\r" not in raw, "{} must use LF line endings".format(example_id))
    source_limit = record.get("limits", {}).get("source_bytes_max", 0)
    if isinstance(source_limit, int):
        errors.check(
            len(raw) <= source_limit,
            "{} exceeds its {}-byte source limit".format(example_id, source_limit),
        )
    batch_limit = record.get("limits", {}).get("import_batch_bytes_max", 0)
    if isinstance(batch_limit, int):
        errors.check(
            len(raw) <= batch_limit,
            "{} exceeds its {}-byte leaf batch limit".format(
                example_id, batch_limit
            ),
        )
    errors.check(
        len(raw) <= 32768,
        "{} exceeds the repository 32 KiB limit".format(example_id),
    )
    board_target = "{}/{}".format(
        _board_category_directory(relative_dir), entrypoint
    )
    errors.check(
        len(board_target.encode("utf-8")) <= 128,
        "{} exceeds the PBLE/1 board target-path limit".format(example_id),
    )
    errors.check(
        len(entrypoint.encode("utf-8")) <= 48,
        "{} entrypoint exceeds 48 UTF-8 bytes".format(example_id),
    )

    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.add("{} is not strict UTF-8: {}".format(example_id, exc))
        return source_path
    errors.check(
        source.startswith("# SPDX-License-Identifier: MIT\n"),
        "{} must start with the MIT SPDX line".format(example_id),
    )
    try:
        tree = ast.parse(source, filename=str(source_path))
        compile(source, str(source_path), "exec")
    except SyntaxError as exc:
        errors.add("{} does not compile: {}".format(example_id, exc))
        return source_path

    docstring = ast.get_docstring(tree, clean=False) or ""
    section_headings = list(
        re.finditer(r"(?m)^\s*[A-Z][A-Za-z ]+:\s*$", docstring)
    )
    for label in DOCSTRING_LABELS:
        label_matches = list(
            re.finditer(
                r"(?m)^\s*{}\s*$".format(re.escape(label)),
                docstring,
            )
        )
        errors.check(
            len(label_matches) == 1,
            "{} docstring must contain exactly one {!r}".format(
                example_id, label
            ),
        )
        if len(label_matches) == 1:
            match = label_matches[0]
            next_heading = next(
                (
                    heading.start()
                    for heading in section_headings
                    if heading.start() > match.start()
                ),
                len(docstring),
            )
            errors.check(
                bool(docstring[match.end():next_heading].strip()),
                "{} docstring section {!r} must explain what to do".format(
                    example_id, label
                ),
            )
    for label in ("Wiring", "Persistent effects"):
        bare_none = re.search(
            r"(?mi)^\s*{}:\s*None[.;]?\s*$".format(re.escape(label)),
            docstring,
        )
        errors.check(
            bare_none is None,
            "{} must explain {!r} in a complete sentence".format(
                example_id, label
            ),
        )
    errors.check(
        any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "main"
            for node in tree.body
        ),
        "{} must define top-level main()".format(example_id),
    )
    errors.check(
        any(isinstance(node, ast.If) and _guard_calls_main(node) for node in tree.body),
        "{} must call main() only through the __main__ guard".format(example_id),
    )
    top_imports = _top_level_import_names(tree)
    errors.check(
        not (top_imports & HARDWARE_MODULES),
        "{} imports hardware at module scope: {}".format(
            example_id, sorted(top_imports & HARDWARE_MODULES)
        ),
    )
    imports = _import_names(tree)
    errors.check(
        not (imports & FORBIDDEN_MODULES),
        "{} imports deferred/excluded modules: {}".format(
            example_id, sorted(imports & FORBIDDEN_MODULES)
        ),
    )
    errors.check(
        not _has_unique_identifier_call(tree),
        "{} must not access a unique device identifier".format(example_id),
    )
    errors.check(
        not _has_unbounded_loop(tree),
        "{} contains an unbounded constant-true while loop".format(example_id),
    )
    sensitive_names = sorted(_sensitive_assignment_names(tree))
    errors.check(
        not sensitive_names,
        "{} defines credential-like constants: {}".format(
            example_id, sensitive_names
        ),
    )
    configurable = CONFIGURABLE_CONSTANTS.get(example_id, set())
    literals = _top_level_literal_assignments(tree)
    published_unset = {
        name for name, value in literals.items() if value is None
    }
    expected_unset = configurable - {"CONFIRM_EXACT_BOARD"}
    errors.check(
        published_unset == expected_unset,
        "{} top-level None settings differ (missing {}, unexpected {})".format(
            example_id,
            sorted(expected_unset - published_unset),
            sorted(published_unset - expected_unset),
        ),
    )
    for constant in sorted(configurable):
        expected = False if constant == "CONFIRM_EXACT_BOARD" else None
        errors.check(
            constant in literals and literals[constant] is expected,
            "{} must publish {} as {!r}".format(
                example_id, constant, expected
            ),
        )
    if configurable:
        guide_start = source.find("# SETUP GUIDE")
        guide_end = source.find("# END OF SETUP GUIDE")
        guide_is_bounded = 0 <= guide_start < guide_end
        errors.check(
            guide_start >= 0,
            "{} must put a SETUP GUIDE above editable settings".format(
                example_id
            ),
        )
        errors.check(
            guide_end >= 0,
            "{} must mark the end of its SETUP GUIDE".format(example_id),
        )
        errors.check(
            guide_is_bounded,
            "{} SETUP GUIDE markers must be in start/end order".format(
                example_id
            ),
        )
        guide = source[guide_start:guide_end] if guide_is_bounded else ""
        explanation = (
            "False means"
            if configurable == {"CONFIRM_EXACT_BOARD"}
            else "None means"
        )
        errors.check(
            explanation in guide,
            "{} SETUP GUIDE must explain {!r}".format(
                example_id, explanation
            ),
        )
        errors.check(
            re.search(r"(?i)\b(?:teacher|adult)\b", guide) is not None,
            "{} SETUP GUIDE must require a teacher or adult check".format(
                example_id
            ),
        )
        for constant in sorted(configurable):
            expected = False if constant == "CONFIRM_EXACT_BOARD" else None
            assignment = re.search(
                r"(?m)^{}\s*=".format(re.escape(constant)), source
            )
            errors.check(
                assignment is not None
                and guide_is_bounded
                and guide_start < assignment.start() < guide_end,
                "{} must place {} inside its SETUP GUIDE".format(
                    example_id, constant
                ),
            )
            commented_examples = [
                line
                for line in guide.splitlines()
                if re.match(
                    r"^#\s*{}\s*=".format(re.escape(constant)), line
                )
            ]
            errors.check(
                len(commented_examples) == 1,
                "{} SETUP GUIDE must show one example assignment for {}".format(
                    example_id, constant
                ),
            )
            if len(commented_examples) == 1:
                example_source = commented_examples[0][1:].lstrip()
                try:
                    example_tree = ast.parse(example_source)
                    example_node = example_tree.body[0]
                    example_value = ast.literal_eval(example_node.value)
                    example_is_assignment = (
                        len(example_tree.body) == 1
                        and isinstance(example_node, ast.Assign)
                        and len(example_node.targets) == 1
                        and isinstance(example_node.targets[0], ast.Name)
                        and example_node.targets[0].id == constant
                    )
                except (
                    AttributeError,
                    IndexError,
                    SyntaxError,
                    TypeError,
                    ValueError,
                ):
                    example_is_assignment = False
                    example_value = expected
                example_is_concrete = (
                    example_value is True
                    if expected is False
                    else example_value is not None
                    and not isinstance(example_value, bool)
                )
                errors.check(
                    example_is_assignment and example_is_concrete,
                    "{} SETUP GUIDE example for {} must be a concrete literal".format(
                        example_id, constant
                    ),
                )
        app_steps = record.get("requires", {}).get("app", [])
        errors.check(
            any(
                isinstance(step, str) and "SETUP GUIDE" in step
                for step in app_steps
            ),
            "{} app requirements must tell learners to follow the SETUP GUIDE".format(
                example_id
            ),
        )
        configuration_text = " ".join(
            item
            for item in record.get("requires", {}).get("configuration", [])
            if isinstance(item, str)
        )
        for constant in sorted(configurable):
            errors.check(
                constant in configuration_text,
                "{} catalog configuration must name {}".format(
                    example_id, constant
                ),
            )

    declared_modules = set(record.get("requires", {}).get("modules", []))
    relevant_imports = imports & {
        "asyncio",
        "binascii",
        "gc",
        "json",
        "machine",
        "neopixel",
        "os",
        "pyble_st7789",
        "pyble_waveshare_lcd147b",
        "struct",
        "sys",
        "time",
    }
    errors.check(
        relevant_imports == declared_modules,
        "{} module declarations differ from imports (missing {}, extra {})".format(
            example_id,
            sorted(relevant_imports - declared_modules),
            sorted(declared_modules - relevant_imports),
        ),
    )

    declared_files = record.get("effects", {}).get("files_created", [])
    for declared in declared_files:
        errors.check(
            isinstance(declared, str) and declared.startswith("/"),
            "{} filesystem effects must use absolute paths".format(example_id),
        )
        if not isinstance(declared, str):
            continue
        errors.check(
            declared.startswith("/examples/")
            and ".." not in Path(declared).parts,
            "{} created files must remain app-manageable below /examples".format(
                example_id
            ),
        )
        errors.check(
            len(declared.encode("utf-8")) <= 128,
            "{} created file path exceeds the PBLE/1 limit".format(example_id),
        )
        errors.check(
            declared in source,
            "{} source does not contain its declared file path {!r}".format(
                example_id, declared
            ),
        )
    return source_path


def _validate_catalog_contract(
    root: Path, catalog: dict[str, Any], errors: Errors
) -> list[Path]:
    examples = catalog.get("examples")
    if not isinstance(examples, list):
        return []

    errors.check(
        set(catalog.get("profiles", [])) == PROFILES,
        "catalog profiles must contain exactly the five qualified profiles",
    )
    ids: list[str] = []
    paths: list[str] = []
    basenames: list[str] = []
    release_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    tracked_modes = _tracked_modes(root)
    source_paths: list[Path] = []
    actual_inventory: dict[str, tuple[Any, ...]] = {}
    board_listing_entries: dict[str, set[str]] = {}

    for record in examples:
        if not isinstance(record, dict):
            continue
        example_id = record.get("id", "<unknown>")
        relative_dir = record.get("path")
        entrypoint = record.get("entrypoint")
        if isinstance(example_id, str):
            ids.append(example_id)
            actual_inventory[example_id] = (
                record.get("planned_release"),
                record.get("classification"),
                relative_dir,
                entrypoint,
                frozenset(record.get("designed_profiles", [])),
            )
        if isinstance(relative_dir, str):
            paths.append(relative_dir)
        if isinstance(entrypoint, str):
            basenames.append(entrypoint.casefold())
        if isinstance(relative_dir, str) and isinstance(entrypoint, str):
            board_directory = _board_category_directory(relative_dir)
            components = Path(board_directory).parts[1:]
            for index in range(1, len(components)):
                parent = "/" + "/".join(components[:index])
                board_listing_entries.setdefault(parent, set()).add(
                    components[index]
                )
            board_listing_entries.setdefault(board_directory, set()).add(
                entrypoint
            )
        for created_path in record.get("effects", {}).get("files_created", []):
            if isinstance(created_path, str) and created_path.startswith("/examples/"):
                created = Path(created_path)
                board_listing_entries.setdefault(created.parent.as_posix(), set()).add(
                    created.name
                )
        release_counts[record.get("planned_release", "<missing>")] += 1
        class_counts[record.get("classification", "<missing>")] += 1

        designed = set(record.get("designed_profiles", []))
        validated = set(record.get("validated_profiles", []))
        incompatible_records = record.get("known_incompatible", [])
        incompatible = {
            item.get("profile")
            for item in incompatible_records
            if isinstance(item, dict) and isinstance(item.get("profile"), str)
        }
        errors.check(
            validated <= designed,
            "{} validated_profiles must be a subset of designed_profiles".format(
                example_id
            ),
        )
        errors.check(
            designed.isdisjoint(incompatible),
            "{} cannot design for and reject the same profile".format(example_id),
        )
        errors.check(
            designed | incompatible == PROFILES,
            "{} must account for every qualified profile".format(example_id),
        )

        validation = record.get("validation", {})
        status_value = validation.get("status")
        host_evidence = validation.get("host_evidence", [])
        hil_evidence = validation.get("hil_evidence", [])
        if status_value in {"host_passed", "hil_passed"}:
            errors.check(
                bool(host_evidence),
                "{} passed validation requires host evidence".format(example_id),
            )
        if status_value == "planned":
            errors.check(
                not host_evidence and not hil_evidence,
                "{} planned validation cannot cite passing evidence".format(
                    example_id
                ),
            )
        for host_path in host_evidence:
            if not isinstance(host_path, str):
                continue
            relative_host_path = Path(host_path)
            valid_host_path = (
                not relative_host_path.is_absolute()
                and ".." not in relative_host_path.parts
                and (root / relative_host_path).is_file()
            )
            errors.check(
                valid_host_path,
                "{} host evidence must name an existing repository file: {!r}".format(
                    example_id, host_path
                ),
            )
        if validated:
            errors.check(
                status_value == "hil_passed" and bool(hil_evidence),
                "{} validated profiles require hil_passed evidence".format(example_id),
            )
        if status_value == "hil_passed":
            errors.check(
                bool(validated) and bool(hil_evidence),
                "{} hil_passed requires profiles and evidence".format(example_id),
            )

        capabilities = set(record.get("requires", {}).get("capabilities", []))
        declared_modules = set(record.get("requires", {}).get("modules", []))
        for profile_id in designed:
            if profile_id not in PROFILE_MODULES:
                continue
            unavailable = declared_modules - PROFILE_MODULES[profile_id]
            errors.check(
                not unavailable,
                "{} requires modules unavailable on {}: {}".format(
                    example_id, profile_id, sorted(unavailable)
                ),
            )
        if "neopixel" in capabilities:
            errors.check(
                "rpi-pico2-w" not in designed,
                "{} must not claim Pico NeoPixel support".format(example_id),
            )
        if capabilities & {"waveshare-lcd147b", "waveshare-marker"}:
            errors.check(
                designed == {"waveshare-esp32-s3-lcd-147b"},
                "{} Waveshare capabilities are exact-profile only".format(example_id),
            )

        classification = record.get("classification")
        if isinstance(relative_dir, str):
            expected_prefix = {
                "portable": "examples/portable/",
                "capability": "examples/capabilities/",
                "exact-hardware": "examples/exact_hardware/",
                "project": "examples/projects/",
            }.get(classification)
            errors.check(
                expected_prefix is not None
                and relative_dir.startswith(expected_prefix),
                "{} path does not match classification".format(example_id),
            )

        effects_duration = record.get("effects", {}).get("duration_seconds_max")
        limits_duration = record.get("limits", {}).get("runtime_seconds_max")
        errors.check(
            effects_duration == limits_duration,
            "{} effect and limit runtime caps must match".format(example_id),
        )

        source_path = _validate_source(root, record, tracked_modes, errors)
        if source_path is not None:
            source_paths.append(source_path)

    errors.check(len(ids) == len(set(ids)), "catalog IDs must be unique")
    errors.check(len(paths) == len(set(paths)), "catalog paths must be unique")
    errors.check(
        len(basenames) == len(set(basenames)),
        "catalog entrypoint basenames must be case-fold unique",
    )
    for board_directory, names in sorted(board_listing_entries.items()):
        payload_bytes = _board_listing_payload_bytes(names)
        errors.check(
            payload_bytes <= BOARD_LISTING_REPOSITORY_BUDGET_BYTES,
            "board directory {} needs {} FILE_LIST payload bytes; budget is {}".format(
                board_directory,
                payload_bytes,
                BOARD_LISTING_REPOSITORY_BUDGET_BYTES,
            ),
        )
    errors.check(
        dict(release_counts) == EXPECTED_RELEASE_COUNTS,
        "planned release counts changed: {}".format(dict(release_counts)),
    )
    errors.check(
        dict(class_counts) == EXPECTED_CLASS_COUNTS,
        "classification counts changed: {}".format(dict(class_counts)),
    )
    errors.check(
        set(actual_inventory) == set(EXPECTED_INVENTORY),
        "catalog IDs differ from the approved 32-example inventory",
    )
    for example_id in sorted(set(actual_inventory) & set(EXPECTED_INVENTORY)):
        errors.check(
            actual_inventory[example_id] == EXPECTED_INVENTORY[example_id],
            "{} release/classification/path/entrypoint/profile contract changed".format(
                example_id
            ),
        )

    examples_root = root / "examples"
    actual_files = {
        path.relative_to(root).as_posix()
        for path in examples_root.rglob("*")
        if path.is_file() or path.is_symlink()
    } if examples_root.is_dir() else set()
    expected_files = {
        path.relative_to(root).as_posix()
        for path in source_paths
    }
    for extra in sorted(actual_files - expected_files):
        errors.add("uncataloged file under examples: {}".format(extra))
    for missing in sorted(expected_files - actual_files):
        errors.add("catalog source is unavailable: {}".format(missing))

    for relative, tracked_mode in sorted(tracked_modes.items()):
        errors.check(
            tracked_mode == "100644" and relative in expected_files,
            "tracked examples entry must be a cataloged 100644 source: {} ({})".format(
                relative, tracked_mode
            ),
        )

    if examples_root.is_dir():
        for path in examples_root.rglob("*"):
            if path.is_symlink():
                errors.add("symlinks are forbidden under examples: {}".format(path))
            if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES:
                errors.add("forbidden generated/binary file: {}".format(path))
    return source_paths


def _compile_with_mpy_cross(
    executable: str, sources: list[Path], errors: Errors
) -> None:
    resolved = Path(executable).expanduser()
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        errors.add("mpy-cross is not an executable file: {}".format(executable))
        return
    with tempfile.TemporaryDirectory(prefix="pyble-examples-mpy-") as temp_dir:
        output_root = Path(temp_dir)
        for source in sources:
            output = output_root / (source.stem + ".mpy")
            result = subprocess.run(
                [str(resolved), "-o", str(output), str(source)],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip()
                errors.add("mpy-cross failed for {}: {}".format(source, detail))


def _git_source_at(
    root: Path,
    commit: str,
    relative_path: str,
    evidence_id: str,
    errors: Errors,
) -> bytes | None:
    """Read one canonical source blob from an evidence-bound Git commit."""
    result = subprocess.run(
        ["git", "show", "{}:{}".format(commit, relative_path)],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        errors.add(
            "evidence {!r} cannot resolve {} at commit {}".format(
                evidence_id, relative_path, commit
            )
        )
        return None
    return result.stdout


def _top_level_assignment_names(source: bytes) -> set[str]:
    """Return names that an HIL configuration edit may explicitly change."""
    try:
        tree = ast.parse(source.decode("utf-8"))
    except (SyntaxError, UnicodeError):
        return set()
    names: set[str] = set()
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets.extend(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets.append(node.target)
        for target in targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
    return names


def validate_repository(
    root: Path,
    catalog_path: Path,
    schema_path: Path,
    evidence_path: Path = DEFAULT_EVIDENCE,
    evidence_schema_path: Path = DEFAULT_EVIDENCE_SCHEMA,
    mpy_cross: str | None = None,
) -> int:
    errors = Errors()
    catalog = _read_json(catalog_path)
    schema = _read_json(schema_path)
    _validate_schema_keywords(schema, errors)
    SchemaSubsetValidator(schema, errors).validate(catalog)
    evidence = _read_json(evidence_path)
    evidence_schema = _read_json(evidence_schema_path)
    _validate_schema_keywords(evidence_schema, errors, "$evidence_schema")
    SchemaSubsetValidator(evidence_schema, errors).validate(evidence, path="$evidence")
    # Semantic checks rely on the strict shapes above. Stop malformed input
    # here so diagnostics remain controlled instead of leaking type errors.
    errors.raise_if_any()
    sources = _validate_catalog_contract(root, catalog, errors)
    catalog_records = {
        record.get("id"): record
        for record in catalog.get("examples", [])
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    evidence_records = [
        record for record in evidence.get("records", []) if isinstance(record, dict)
    ]
    evidence_ids = {record.get("id") for record in evidence_records}
    evidence_by_id = {
        record.get("id"): record
        for record in evidence_records
        if isinstance(record.get("id"), str)
    }
    errors.check(
        len(evidence_ids) == len(evidence_records),
        "HIL evidence IDs must be unique",
    )
    for evidence_record in evidence_records:
        evidence_id = evidence_record.get("id", "<unknown>")
        example_id = evidence_record.get("example_id")
        profile_id = evidence_record.get("profile_id")
        catalog_record = catalog_records.get(example_id)
        errors.check(
            catalog_record is not None,
            "evidence {!r} references unknown example {!r}".format(
                evidence_id, example_id
            ),
        )
        if catalog_record is not None:
            errors.check(
                profile_id in catalog_record.get("designed_profiles", []),
                "evidence {!r} uses undesigned profile {!r}".format(
                    evidence_id, profile_id
                ),
            )
            source_hashes = evidence_record.get("source_sha256", {})
            executed_hashes = evidence_record.get("executed_source_sha256", {})
            catalog_files = set(catalog_record.get("files", []))
            errors.check(
                isinstance(source_hashes, dict)
                and set(source_hashes) == catalog_files,
                "evidence {!r} source hashes must match the catalog file set".format(
                    evidence_id
                ),
            )
            errors.check(
                isinstance(executed_hashes, dict)
                and set(executed_hashes) == catalog_files,
                "evidence {!r} executed hashes must match the catalog file set".format(
                    evidence_id
                ),
            )

            commit = evidence_record.get("example_commit")
            canonical_assignments: dict[str, set[str]] = {}
            if isinstance(commit, str):
                for filename in sorted(catalog_files):
                    relative = "{}/{}".format(catalog_record["path"], filename)
                    source_at_commit = _git_source_at(
                        root, commit, relative, str(evidence_id), errors
                    )
                    if source_at_commit is None:
                        continue
                    canonical_assignments[filename] = (
                        _top_level_assignment_names(source_at_commit)
                    )
                    actual_hash = hashlib.sha256(source_at_commit).hexdigest()
                    errors.check(
                        source_hashes.get(filename) == actual_hash,
                        "evidence {!r} canonical hash differs for {}".format(
                            evidence_id, filename
                        ),
                    )

            edits = evidence_record.get("configuration_edits", [])
            edit_keys = set()
            allowed_constants = CONFIGURABLE_CONSTANTS.get(example_id, set())
            for edit in edits:
                filename = edit.get("file")
                constant = edit.get("constant")
                value = edit.get("value")
                edit_keys.add((filename, constant))
                errors.check(
                    filename in catalog_files,
                    "evidence {!r} config edit uses an unknown file".format(
                        evidence_id
                    ),
                )
                errors.check(
                    constant in allowed_constants,
                    "evidence {!r} config edit is not an approved user constant: {}".format(
                        evidence_id, constant
                    ),
                )
                if filename in canonical_assignments:
                    errors.check(
                        constant in canonical_assignments[filename],
                        "evidence {!r} config edit constant is absent from {}".format(
                            evidence_id, filename
                        ),
                    )
                errors.check(
                    isinstance(value, str)
                    and "\n" not in value
                    and "\r" not in value,
                    "evidence {!r} config values must be one-line literals".format(
                        evidence_id
                    ),
                )
                literal_valid = False
                literal_value = None
                if isinstance(value, str):
                    try:
                        literal_value = ast.literal_eval(value)
                        literal_valid = True
                    except (SyntaxError, ValueError):
                        pass
                errors.check(
                    literal_valid,
                    "evidence {!r} config value is not a Python literal: {}".format(
                        evidence_id, constant
                    ),
                )
                published_value = (
                    False if constant == "CONFIRM_EXACT_BOARD" else None
                )
                if literal_valid:
                    errors.check(
                        literal_value is not published_value,
                        "evidence {!r} config edit leaves {} unpublished".format(
                            evidence_id, constant
                        ),
                    )
                    if constant == "CONFIRM_EXACT_BOARD":
                        errors.check(
                            literal_value is True,
                            "evidence {!r} exact-board confirmation must be True".format(
                                evidence_id
                            ),
                        )
            errors.check(
                len(edit_keys) == len(edits),
                "evidence {!r} configuration constants must be unique".format(
                    evidence_id
                ),
            )
            edited_constants = {
                edit.get("constant") for edit in edits if isinstance(edit, dict)
            }
            errors.check(
                edited_constants == allowed_constants,
                "evidence {!r} must configure exactly these constants: {}".format(
                    evidence_id,
                    ", ".join(sorted(allowed_constants)) or "none",
                ),
            )

            hashes_differ = source_hashes != executed_hashes
            changed_files = {
                filename
                for filename in catalog_files
                if source_hashes.get(filename) != executed_hashes.get(filename)
            }
            edited_files = {
                edit.get("file") for edit in edits if isinstance(edit, dict)
            }
            asset = evidence_record.get("executed_source_asset", "")
            assets = evidence_record.get("assets", [])
            if edits:
                errors.check(
                    hashes_differ,
                    "evidence {!r} configuration edits must change a source hash".format(
                        evidence_id
                    ),
                )
                errors.check(
                    bool(asset) and asset in assets,
                    "evidence {!r} must archive its configured executed source".format(
                        evidence_id
                    ),
                )
                errors.check(
                    changed_files == edited_files,
                    "evidence {!r} changed files must match configuration edits".format(
                        evidence_id
                    ),
                )
            else:
                errors.check(
                    not hashes_differ,
                    "evidence {!r} changed executed source without config edits".format(
                    evidence_id
                ),
            )

        firmware = evidence_record.get("firmware", {})
        baseline = catalog.get("firmware_baseline", {})
        expected_firmware = {
            "agent": baseline.get("agent"),
            "tag": baseline.get("release_tag"),
            "source_commit": baseline.get("source_commit"),
            "descriptor_sha256": baseline.get("release_descriptor_sha256"),
        }
        errors.check(
            firmware == expected_firmware,
            "evidence {!r} firmware identity must match the catalog baseline".format(
                evidence_id
            ),
        )
    for record in catalog.get("examples", []):
        if not isinstance(record, dict):
            continue
        for evidence_id in record.get("validation", {}).get("hil_evidence", []):
            errors.check(
                evidence_id in evidence_ids,
                "{} references unknown HIL evidence {!r}".format(
                    record.get("id", "<unknown>"), evidence_id
                ),
            )
            evidence_record = evidence_by_id.get(evidence_id)
            if evidence_record is not None:
                errors.check(
                    evidence_record.get("example_id") == record.get("id"),
                    "{} references HIL evidence for a different example: {!r}".format(
                        record.get("id", "<unknown>"), evidence_id
                    ),
                )
        evidenced_profiles = {
            item.get("profile_id")
            for item in evidence_records
            if item.get("example_id") == record.get("id")
            and item.get("id")
            in record.get("validation", {}).get("hil_evidence", [])
        }
        errors.check(
            set(record.get("validated_profiles", [])) <= evidenced_profiles,
            "{} has validated profiles without referenced matching evidence".format(
                record.get("id", "<unknown>")
            ),
        )
    if mpy_cross is not None:
        _compile_with_mpy_cross(mpy_cross, sources, errors)
    errors.raise_if_any()
    return len(sources)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument(
        "--evidence-schema", type=Path, default=DEFAULT_EVIDENCE_SCHEMA
    )
    parser.add_argument(
        "--mpy-cross",
        help="compile every entrypoint with this exact mpy-cross executable",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        count = validate_repository(
            args.root.resolve(),
            args.catalog.resolve(),
            args.schema.resolve(),
            args.evidence.resolve(),
            args.evidence_schema.resolve(),
            args.mpy_cross,
        )
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    suffix = " with mpy-cross" if args.mpy_cross else ""
    print("Validated {} PyBLE examples{}".format(count, suffix))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
