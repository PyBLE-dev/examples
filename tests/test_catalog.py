# SPDX-License-Identifier: MIT
"""Catalog, schema, evidence, and repository-contract tests."""

from copy import deepcopy
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.validate_catalog import (  # noqa: E402
    BOARD_LISTING_REPOSITORY_BUDGET_BYTES,
    CONFIGURABLE_CONSTANTS,
    DEFAULT_CATALOG,
    DEFAULT_EVIDENCE,
    DEFAULT_EVIDENCE_SCHEMA,
    DEFAULT_SCHEMA,
    ContractError,
    Errors,
    SchemaSubsetValidator,
    _board_category_directory,
    _board_listing_payload_bytes,
    _read_json,
    _validate_schema_keywords,
    validate_repository,
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sample_evidence(example_id, filename):
    """Return structurally complete evidence for focused negative tests."""
    return {
        "id": "hil-sample",
        "example_id": example_id,
        "example_commit": "0" * 40,
        "source_sha256": {filename: "0" * 64},
        "executed_source_sha256": {filename: "0" * 64},
        "configuration_edits": [],
        "executed_source_asset": "",
        "firmware": {
            "agent": "0.6.0",
            "tag": "firmware-v0.6.0",
            "source_commit": "0" * 40,
            "descriptor_sha256": "0" * 64,
        },
        "profile_id": "esp32-4mb",
        "carrier": "fixture carrier",
        "fixture": "fixture revision",
        "wiring": ["No external wiring for this portable example"],
        "app": "test app",
        "host": "test host",
        "import": "immutable import description",
        "expected": "expected behavior",
        "observed": "observed behavior",
        "terminal_state": "done",
        "cleanup": "no resources",
        "pble_responsive": True,
        "validator_version": "1",
        "operator": "test operator",
        "timestamp_utc": "2026-08-25T00:00:00Z",
        "result": "passed",
        "assets": [],
    }


class CatalogValidationTest(unittest.TestCase):
    def setUp(self):
        self.catalog = read_json(DEFAULT_CATALOG)
        self.schema = read_json(DEFAULT_SCHEMA)

    def schema_errors(self, value):
        errors = Errors()
        SchemaSubsetValidator(self.schema, errors).validate(value)
        return errors.items

    def validate_changed(self, catalog=None, evidence=None):
        """Validate temporary JSON mutations against the real repository."""
        catalog = self.catalog if catalog is None else catalog
        evidence = read_json(DEFAULT_EVIDENCE) if evidence is None else evidence
        with tempfile.TemporaryDirectory(prefix="pyble-catalog-test-") as directory:
            catalog_path = Path(directory) / "examples.json"
            evidence_path = Path(directory) / "index.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            with self.assertRaises(ContractError) as caught:
                validate_repository(
                    ROOT,
                    catalog_path,
                    DEFAULT_SCHEMA,
                    evidence_path,
                    DEFAULT_EVIDENCE_SCHEMA,
                )
        return str(caught.exception)

    def test_complete_repository_contract_passes(self):
        self.assertEqual(
            validate_repository(
                ROOT,
                DEFAULT_CATALOG,
                DEFAULT_SCHEMA,
                DEFAULT_EVIDENCE,
                DEFAULT_EVIDENCE_SCHEMA,
            ),
            32,
        )

    def test_every_example_starts_with_child_facing_instructions(self):
        required = ("Settings:", "Before you run:", "Try this:")
        for record in self.catalog["examples"]:
            source_path = ROOT / record["path"] / record["entrypoint"]
            source = source_path.read_text(encoding="utf-8")
            docstring = ast.get_docstring(ast.parse(source), clean=False) or ""
            with self.subTest(example=record["id"]):
                for label in required:
                    self.assertIn(label, docstring)
                    lines = docstring.splitlines()
                    indexes = [
                        index
                        for index, line in enumerate(lines)
                        if line.strip() == label
                    ]
                    self.assertEqual(len(indexes), 1)
                    next_heading = next(
                        (
                            index
                            for index in range(indexes[0] + 1, len(lines))
                            if lines[index].strip().endswith(":")
                            and lines[index].strip()[:-1].replace(" ", "").isalpha()
                        ),
                        len(lines),
                    )
                    self.assertTrue(
                        any(
                            line.strip()
                            for line in lines[indexes[0] + 1:next_heading]
                        )
                    )
                self.assertNotRegex(
                    docstring,
                    r"(?mi)^\s*Wiring:\s*None[.;]?\s*$",
                )
                self.assertNotRegex(
                    docstring,
                    r"(?mi)^\s*Persistent effects:\s*None[.;]?\s*$",
                )

    def test_configurable_examples_publish_checked_setup_recipes(self):
        records = {record["id"]: record for record in self.catalog["examples"]}
        self.assertEqual(
            CONFIGURABLE_CONSTANTS["neopixel-single-pixel"],
            {"PIXEL_PIN"},
        )
        for example_id, constants in CONFIGURABLE_CONSTANTS.items():
            record = records[example_id]
            source_path = ROOT / record["path"] / record["entrypoint"]
            source = source_path.read_text(encoding="utf-8")
            configuration = " ".join(record["requires"]["configuration"])
            app_steps = " ".join(record["requires"]["app"])
            guide = source.split("# SETUP GUIDE", 1)[1].split(
                "# END OF SETUP GUIDE", 1
            )[0]
            with self.subTest(example=example_id):
                self.assertIn("# SETUP GUIDE", source)
                self.assertIn("# END OF SETUP GUIDE", source)
                self.assertIn("SETUP GUIDE", app_steps)
                self.assertRegex(guide.lower(), r"\b(?:teacher|adult)\b")
                for constant in constants:
                    self.assertIn(constant, configuration)
                    prefix = "# {} =".format(constant)
                    examples = [
                        line
                        for line in guide.splitlines()
                        if line.startswith(prefix)
                    ]
                    self.assertEqual(len(examples), 1)
                    assignment = ast.parse(examples[0][1:].lstrip()).body[0]
                    value = ast.literal_eval(assignment.value)
                    if constant == "CONFIRM_EXACT_BOARD":
                        self.assertIs(value, True)
                    else:
                        self.assertIsNotNone(value)
                        self.assertNotIsInstance(value, bool)

    def test_button_guides_distinguish_none_from_quoted_none(self):
        button_ids = {
            "gpio-read-external-button",
            "gpio-button-controls-led",
            "project-button-press-counter",
            "project-button-neopixel",
        }
        for record in self.catalog["examples"]:
            if record["id"] not in button_ids:
                continue
            source_path = ROOT / record["path"] / record["entrypoint"]
            source = source_path.read_text(encoding="utf-8")
            guide = source.split("# SETUP GUIDE", 1)[1].split(
                "# END OF SETUP GUIDE", 1
            )[0]
            with self.subTest(example=record["id"]):
                self.assertIn('"none"', guide)
                self.assertIn("quote", guide.lower())

    def test_catalog_has_exact_release_and_classification_counts(self):
        releases = {}
        classifications = {}
        for record in self.catalog["examples"]:
            releases[record["planned_release"]] = (
                releases.get(record["planned_release"], 0) + 1
            )
            classifications[record["classification"]] = (
                classifications.get(record["classification"], 0) + 1
            )
        self.assertEqual(releases, {"0.1.0": 8, "0.2.0": 17, "0.3.0": 7})
        self.assertEqual(
            classifications,
            {"portable": 14, "capability": 9, "exact-hardware": 6, "project": 3},
        )

    def test_board_category_layout_avoids_truncated_conflict_lists(self):
        flattened = {
            record["entrypoint"] for record in self.catalog["examples"]
        }
        self.assertGreater(_board_listing_payload_bytes(flattened), 480)

        categories = {}
        for record in self.catalog["examples"]:
            directory = _board_category_directory(record["path"])
            categories.setdefault(directory, set()).add(record["entrypoint"])
        self.assertEqual(max(map(_board_listing_payload_bytes, categories.values())), 186)
        self.assertLessEqual(
            max(map(_board_listing_payload_bytes, categories.values())),
            BOARD_LISTING_REPOSITORY_BUDGET_BYTES,
        )

    def test_unknown_properties_are_rejected(self):
        changed = deepcopy(self.catalog)
        changed["examples"][0]["unsupported"] = True
        self.assertTrue(
            any("unknown property" in error for error in self.schema_errors(changed))
        )

    def test_invalid_profile_and_filename_are_rejected(self):
        changed = deepcopy(self.catalog)
        changed["examples"][0]["designed_profiles"] = ["imaginary-board"]
        changed["examples"][0]["entrypoint"] = "Main.PY"
        errors = self.schema_errors(changed)
        self.assertTrue(
            any(
                "designed_profiles[0] is not one of" in error
                for error in errors
            )
        )
        self.assertTrue(any("entrypoint" in error for error in errors))

    def test_malformed_catalog_shape_reports_a_controlled_contract_error(self):
        changed = deepcopy(self.catalog)
        changed["examples"][0]["designed_profiles"] = [{}]
        message = self.validate_changed(catalog=changed)
        self.assertIn("is not one of", message)

    def test_schema_subset_rejects_an_unimplemented_keyword(self):
        changed = deepcopy(self.schema)
        changed["examplesOf"] = []
        errors = Errors()
        _validate_schema_keywords(changed, errors)
        self.assertTrue(any("unsupported" in error for error in errors.items))

    def test_json_reader_rejects_duplicate_properties(self):
        with tempfile.TemporaryDirectory(prefix="pyble-json-test-") as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"version": 1, "version": 2}', encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "duplicate JSON"):
                _read_json(path)

    def test_evidence_index_is_strict_and_initially_empty(self):
        evidence = read_json(DEFAULT_EVIDENCE)
        evidence_schema = read_json(DEFAULT_EVIDENCE_SCHEMA)
        self.assertEqual(evidence["records"], [])
        changed = deepcopy(evidence)
        changed["unexpected"] = 1
        errors = Errors()
        SchemaSubsetValidator(evidence_schema, errors).validate(changed)
        self.assertTrue(any("unknown property" in error for error in errors.items))

    def test_schema_uses_json_equality_and_strict_date_times(self):
        errors = Errors()
        SchemaSubsetValidator({"const": 1}, errors).validate(True)
        self.assertTrue(any("must equal" in error for error in errors.items))

        errors = Errors()
        SchemaSubsetValidator({"enum": [True]}, errors).validate(1)
        self.assertTrue(any("not one of" in error for error in errors.items))

        errors = Errors()
        unique_schema = {"type": "array", "uniqueItems": True}
        SchemaSubsetValidator(unique_schema, errors).validate([1, 1.0])
        self.assertTrue(any("items must be unique" in error for error in errors.items))

        errors = Errors()
        SchemaSubsetValidator(unique_schema, errors).validate([True, 1])
        self.assertEqual(errors.items, [])

        errors = Errors()
        date_time_schema = {"type": "string", "format": "date-time"}
        SchemaSubsetValidator(date_time_schema, errors).validate(
            "2026-08-25X00:00:00+07:00"
        )
        self.assertTrue(any("RFC 3339" in error for error in errors.items))

        errors = Errors()
        SchemaSubsetValidator(date_time_schema, errors).validate(
            "2026-08-25T00:00:00.123Z"
        )
        self.assertEqual(errors.items, [])

    def test_hil_schema_requires_explicit_wiring_and_utc(self):
        evidence_schema = read_json(DEFAULT_EVIDENCE_SCHEMA)
        record = sample_evidence(
            "portable-paced-counter", "pyble_paced_counter.py"
        )
        record["wiring"] = []
        record["timestamp_utc"] = "2026-08-25T07:00:00+07:00"
        evidence = {
            "$schema": "./index.schema.json",
            "version": 1,
            "records": [record],
        }
        errors = Errors()
        SchemaSubsetValidator(evidence_schema, errors).validate(evidence)
        self.assertTrue(any("wiring needs at least 1" in error for error in errors.items))
        self.assertTrue(any("timestamp_utc" in error for error in errors.items))

        record["wiring"] = [" "]
        record["timestamp_utc"] = "2026-08-25T00:00:00Z"
        errors = Errors()
        SchemaSubsetValidator(evidence_schema, errors).validate(evidence)
        self.assertTrue(any("wiring[0]" in error for error in errors.items))

    def test_no_hardware_profile_is_claimed_as_validated(self):
        for record in self.catalog["examples"]:
            self.assertEqual(record["validated_profiles"], [], record["id"])
            self.assertNotEqual(record["validation"]["status"], "hil_passed")

    def test_approved_inventory_cannot_be_substituted_at_the_same_count(self):
        changed = deepcopy(self.catalog)
        changed["examples"][0]["id"] = "portable-substitute-console"
        message = self.validate_changed(catalog=changed)
        self.assertIn("approved 32-example inventory", message)

    def test_host_evidence_must_name_an_existing_repository_file(self):
        changed = deepcopy(self.catalog)
        changed["examples"][0]["validation"] = {
            "status": "host_passed",
            "host_evidence": ["tests/does_not_exist.py"],
            "hil_evidence": [],
        }
        message = self.validate_changed(catalog=changed)
        self.assertIn("host evidence must name an existing repository file", message)

    def test_created_files_must_remain_below_the_app_visible_directory(self):
        changed = deepcopy(self.catalog)
        record = next(
            item
            for item in changed["examples"]
            if item["id"] == "portable-file-round-trip"
        )
        record["effects"]["files_created"] = ["/pyble_hidden.txt"]
        message = self.validate_changed(catalog=changed)
        self.assertIn("app-manageable below /examples", message)

    def test_hil_evidence_cannot_be_attached_to_a_different_example(self):
        changed = deepcopy(self.catalog)
        hello = changed["examples"][0]
        hello["validated_profiles"] = ["esp32-4mb"]
        hello["validation"] = {
            "status": "hil_passed",
            "host_evidence": ["tests/test_catalog.py"],
            "hil_evidence": ["hil-paced-esp32"],
        }
        evidence = {
            "$schema": "./index.schema.json",
            "version": 1,
            "records": [
                sample_evidence(
                    "portable-paced-counter", "pyble_paced_counter.py"
                )
            ],
        }
        evidence["records"][0]["id"] = "hil-paced-esp32"
        message = self.validate_changed(catalog=changed, evidence=evidence)
        self.assertIn("evidence for a different example", message)

    def test_configurable_hil_requires_every_published_unset_constant(self):
        evidence = {
            "$schema": "./index.schema.json",
            "version": 1,
            "records": [
                sample_evidence(
                    "gpio-blink-external-led", "pyble_gpio_blink.py"
                )
            ],
        }
        message = self.validate_changed(evidence=evidence)
        self.assertIn(
            "must configure exactly these constants: LED_ACTIVE_LEVEL, LED_PIN",
            message,
        )

        evidence["records"][0]["configuration_edits"] = [
            {
                "file": "pyble_gpio_blink.py",
                "constant": "LED_PIN",
                "value": "1",
            },
            {
                "file": "pyble_gpio_blink.py",
                "constant": "LED_ACTIVE_LEVEL",
                "value": "1",
            },
        ]
        message = self.validate_changed(evidence=evidence)
        self.assertNotIn("must configure exactly these constants", message)


if __name__ == "__main__":
    unittest.main()
