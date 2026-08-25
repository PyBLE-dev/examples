# SPDX-License-Identifier: MIT
"""Behavior tests for all fourteen portable/workflow examples."""

import asyncio
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from support import ROOT, load_example


PATHS = {
    "hello": "examples/portable/basics/hello_console/pyble_hello_console.py",
    "paced": "examples/portable/basics/paced_counter/pyble_paced_counter.py",
    "runtime": "examples/portable/basics/runtime_info/pyble_runtime_info.py",
    "decisions": "examples/portable/basics/data_decisions/pyble_data_decisions.py",
    "functions": (
        "examples/portable/basics/reusable_functions/"
        "pyble_reusable_functions.py"
    ),
    "handling": "examples/portable/basics/error_handling/pyble_error_handling.py",
    "json": "examples/portable/data/json_data/pyble_json_data.py",
    "binary": "examples/portable/data/binary_data/pyble_binary_data.py",
    "file": "examples/portable/workflow/file_round_trip/pyble_file_round_trip.py",
    "input": "examples/portable/workflow/console_input/pyble_console_input.py",
    "async": "examples/portable/workflow/async_cooperation/pyble_async_cooperation.py",
    "stop": "examples/portable/workflow/stop_a_program/pyble_stop_a_program.py",
    "error": "examples/portable/workflow/expected_error/pyble_expected_error.py",
    "list": "examples/portable/workflow/list_directory/pyble_list_directory.py",
}


def capture_output(callback):
    """Run one bounded callable and return its console text."""
    output = io.StringIO()
    with redirect_stdout(output):
        callback()
    return output.getvalue()


class PortableExamplesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = {}
        for name, relative in PATHS.items():
            module, stdout, stderr = load_example(relative)
            if stdout or stderr:
                raise AssertionError("{} import produced output".format(relative))
            cls.modules[name] = module

    def test_inventory_matches_fourteen_cataloged_portable_sources(self):
        catalog = json.loads((ROOT / "catalog/examples.json").read_text())
        expected = {
            record["path"] + "/" + record["entrypoint"]
            for record in catalog["examples"]
            if record["classification"] == "portable"
        }
        self.assertEqual(expected, set(PATHS.values()))

    def test_every_portable_lesson_has_child_facing_guidance(self):
        for name, module in self.modules.items():
            with self.subTest(example=name):
                docstring = module.__doc__
                self.assertIn("Settings:", docstring)
                self.assertIn("Before you run:", docstring)
                self.assertIn("Try this:", docstring)
                self.assertIn("Wiring:", docstring)
                self.assertIn("Persistent effects:", docstring)
                self.assertNotRegex(docstring, r"(?m)^\s+None[.;]?")

    def test_hello_console(self):
        self.assertEqual(self.modules["hello"].hello_message(), "Hello from PyBLE!")

    def test_noninteractive_portable_mains_complete(self):
        for name in (
            "hello",
            "runtime",
            "decisions",
            "functions",
            "handling",
            "json",
            "binary",
        ):
            with self.subTest(example=name):
                self.assertTrue(capture_output(self.modules[name].main).strip())

        paced = self.modules["paced"]
        with patch.object(paced.time, "sleep_ms", lambda _delay: None, create=True):
            paced_output = capture_output(paced.main)
        self.assertIn("Count 5/5", paced_output)

        stop = self.modules["stop"]
        with patch.object(stop.time, "sleep_ms", lambda _delay: None, create=True):
            stop_output = capture_output(stop.main)
        self.assertIn("Finished by itself", stop_output)

    def test_clear_console_snapshots(self):
        expected = {
            "hello": "Hello from PyBLE!\n",
            "decisions": (
                "Sample: workbench\n"
                "Values (C): (18, 23, 27)\n"
                "Average: 22.7 C -> comfortable\n"
            ),
            "functions": (
                "0 C = 32.0 F (cold)\n"
                "20 C = 68.0 F (mild)\n"
                "30 C = 86.0 F (hot)\n"
            ),
            "handling": (
                "75 is an allowed percentage.\n"
                "We caught the planned mistake: a percentage must be a whole "
                "number from 0 to 100\n"
            ),
            "json": (
                'JSON: {"animal": "bird", "legs": 2, "can_fly": true}\n'
                "Decoded: animal=bird, legs=2, can_fly=True\n"
            ),
            "binary": (
                "Packed bytes (hex): 020107\n"
                "Unpacked: sample=513, status=7\n"
            ),
        }
        for name, text in expected.items():
            with self.subTest(example=name):
                self.assertEqual(capture_output(self.modules[name].main), text)

    def test_effectful_and_interactive_portable_mains_use_safe_seams(self):
        file_example = self.modules["file"]
        self.assertEqual(
            file_example.FILE_PATH,
            "/examples/pyble_example_round_trip.txt",
        )
        with patch.object(
            file_example,
            "round_trip",
            return_value=len(file_example.FILE_CONTENT),
        ) as round_trip:
            output = capture_output(file_example.main)
        round_trip.assert_called_once_with(
            file_example.FILE_PATH,
            file_example.FILE_CONTENT,
        )
        self.assertIn("removed", output)

        input_example = self.modules["input"]
        response = "blue"
        with patch("builtins.input", return_value=response):
            output = capture_output(input_example.main)
        self.assertIn("appears on screen", output)
        self.assertIn("Recognized", output)

        listing = self.modules["list"]

        class FakeOS:
            @staticmethod
            def ilistdir(_path):
                return iter((("one", 0, 0), ("two", 0, 0)))

        class FakeGC:
            collections = 0

            @classmethod
            def collect(cls):
                cls.collections += 1

        with patch.object(listing, "os", FakeOS), patch.object(
            listing, "gc", FakeGC
        ):
            output = capture_output(listing.main)
        self.assertIn("- one", output)
        self.assertEqual(FakeGC.collections, 1)

        with self.assertRaisesRegex(ValueError, "part of the lesson"):
            capture_output(self.modules["error"].main)

    def test_paced_counter(self):
        output = []
        delays = []
        self.modules["paced"].run_counter(3, 25, delays.append, output.append)
        self.assertEqual(output, ["Count 1/3", "Count 2/3", "Count 3/3"])
        self.assertEqual(delays, [25, 25])
        self.modules["paced"].validate_settings(1, 100)
        with self.assertRaises(ValueError):
            self.modules["paced"].validate_settings(6, 100)
        with self.assertRaises(ValueError):
            self.modules["paced"].validate_settings(2, 99)

    def test_editable_teaching_settings_are_checked(self):
        hello = self.modules["hello"]
        self.assertEqual(hello.validate_message("Hi!"), "Hi!")
        with self.assertRaises(ValueError):
            hello.validate_message("line one\nline two")
        with self.assertRaises(ValueError):
            hello.validate_message("x" * 41)

        decisions = self.modules["decisions"]
        with self.assertRaises(ValueError):
            decisions.validate_sample({"name": "test", "values_c": ()})
        with self.assertRaises(ValueError):
            decisions.validate_sample({"name": "x" * 21, "values_c": (20,)})

        functions = self.modules["functions"]
        with self.assertRaises(ValueError):
            functions.validate_temperatures((0, 1, 2, 3, 4, 5))
        with self.assertRaises(ValueError):
            functions.validate_temperatures((51,))

        json_example = self.modules["json"]
        with self.assertRaises(ValueError):
            json_example.validate_record(
                {"animal": "bird", "legs": 2, "can_fly": "yes"}
            )

        binary = self.modules["binary"]
        with self.assertRaises(ValueError):
            binary.validate_values(65536, 7)
        with self.assertRaises(ValueError):
            binary.validate_values(513, 256)

    def test_runtime_information_is_non_identifying(self):
        runtime = self.modules["runtime"]
        self.assertEqual(runtime.version_text((1, 28, 0, "extra")), "1.28.0")
        source = Path(PATHS["runtime"]).read_text(encoding="utf-8")
        self.assertNotIn("unique_id(", source)

    def test_data_decisions(self):
        decisions = self.modules["decisions"]
        self.assertEqual(decisions.classify_temperature(17), "cool")
        self.assertEqual(decisions.classify_temperature(20), "comfortable")
        self.assertEqual(decisions.classify_temperature(27), "warm")
        self.assertEqual(decisions.summarize_sample(decisions.SAMPLE)[3], "comfortable")

    def test_reusable_functions(self):
        functions = self.modules["functions"]
        self.assertEqual(functions.celsius_to_fahrenheit(0), 32)
        self.assertIn("68.0 F", functions.temperature_line(20))

    def test_error_handling_validator(self):
        handling = self.modules["handling"]
        self.assertEqual(handling.validate_percentage(75), 75)
        handling.validate_lesson_setting(101)
        with self.assertRaises(ValueError):
            handling.validate_percentage(101)
        with self.assertRaises(ValueError):
            handling.validate_percentage(True)
        with self.assertRaises(ValueError):
            handling.validate_lesson_setting(100)

    def test_json_round_trip(self):
        encoded, decoded = self.modules["json"].json_round_trip({"ok": True})
        self.assertEqual(decoded, {"ok": True})
        self.assertEqual(json.loads(encoded), decoded)

    def test_binary_round_trip(self):
        binary = self.modules["binary"]
        payload = binary.pack_record(513, 7)
        self.assertEqual(binary.bytes_as_hex(payload), "020107")
        self.assertEqual(binary.unpack_record(payload), (513, 7))

    def test_file_round_trip_refuses_overwrite_and_cleans_up(self):
        file_example = self.modules["file"]
        with self.assertRaisesRegex(ValueError, "reviewed /examples path"):
            file_example.validate_example_path("/pyble_round_trip.txt")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "round-trip.txt"
            self.assertEqual(file_example.round_trip(str(target), "safe\n"), 5)
            self.assertFalse(target.exists())
            target.write_text("mine", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                file_example.round_trip(str(target), "other")
            self.assertEqual(target.read_text(encoding="utf-8"), "mine")

            class ReplacingWriter:
                def __init__(self, handle):
                    self.handle = handle

                def write(self, text):
                    return self.handle.write(text)

                def close(self):
                    self.handle.close()
                    target.write_text("replacement", encoding="utf-8")

            target.unlink()

            def replacing_open(path, mode):
                handle = open(path, mode)
                return ReplacingWriter(handle) if mode == "x" else handle

            with self.assertRaisesRegex(RuntimeError, "verification failed"):
                file_example.round_trip(
                    str(target),
                    "owned",
                    open_fn=replacing_open,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "replacement")

            target.unlink()

            def failing_read_open(path, mode):
                if mode == "r":
                    raise OSError("read failed")
                return open(path, mode)

            with self.assertRaisesRegex(OSError, "read failed"):
                file_example.round_trip(
                    str(target),
                    "unverified",
                    open_fn=failing_read_open,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "unverified")

        removed = []

        class CloseFailure:
            def write(self, _text):
                return None

            def close(self):
                raise OSError("close failed")

        with self.assertRaises(OSError):
            file_example.round_trip(
                "/examples/test.txt",
                "data",
                open_fn=lambda _path, _mode: CloseFailure(),
                remove_fn=removed.append,
            )
        self.assertEqual(removed, ["/examples/test.txt"])

    def test_console_result_does_not_repeat_the_echoed_response(self):
        input_example = self.modules["input"]
        self.assertTrue(input_example.is_short_printable_text("blue"))
        self.assertFalse(input_example.is_short_printable_text("green"))
        self.assertFalse(input_example.is_short_printable_text("blué"))
        secret = "not-for-output"
        self.assertNotIn(secret, input_example.response_message(secret))
        source = (ROOT / PATHS["input"]).read_text(encoding="utf-8")
        self.assertIn("typed answer appears", source)
        self.assertNotIn("is not echoed", source)

    def test_async_workers_cooperate_finitely(self):
        async_example = self.modules["async"]
        output = []
        delays = []

        async def fake_sleep(delay):
            delays.append(delay)
            await asyncio.sleep(0)

        asyncio.run(async_example.cooperative_demo(fake_sleep, output.append))
        self.assertEqual(len(output), 5)
        self.assertEqual(sorted(delays), [180, 180, 260])
        self.assertTrue(output[0].startswith("Task Red:"))
        self.assertTrue(any(line.startswith("Task Blue:") for line in output))

    def test_stop_lesson_has_hard_bound(self):
        stop = self.modules["stop"]
        output = []
        delays = []
        stop.run_ticks(4, 10, delays.append, output.append)
        self.assertEqual(len(output), 4)
        self.assertEqual(delays, [10, 10, 10])
        self.assertEqual(stop.MAXIMUM_TICKS, 20)
        self.assertLessEqual(
            stop.MAXIMUM_TICKS * stop.TICK_DELAY_MS,
            15_000,
        )

    def test_expected_error_is_exact(self):
        expected_error = self.modules["error"]
        self.assertIn(
            expected_error.ERROR_MESSAGE,
            expected_error.announcement_message(),
        )
        with self.assertRaisesRegex(ValueError, "part of the lesson"):
            expected_error.raise_expected_error()

    def test_directory_listing_is_limited_and_safe(self):
        listing = self.modules["list"]
        self.assertEqual(listing.validate_directory("/examples"), "/examples")
        with self.assertRaises(ValueError):
            listing.validate_directory("/other")
        shown, omitted = listing.choose_names(iter(("a", "bad\nname", "c")), 2)
        self.assertEqual(shown, ["a", "bad?name"])
        self.assertIs(omitted, True)
        self.assertEqual(listing.short_name("é\n"), "??")

        consumed = []

        def many_names():
            for index in range(100):
                consumed.append(index)
                yield str(index)

        listing.choose_names(many_names(), 2)
        self.assertEqual(consumed, [0, 1, 2])
        widest = listing.short_name("\U0001f4a1" * 17)
        maximum_rendered = listing.folder_message(
            "/",
            [widest] * listing.MAXIMUM_NAMES,
            True,
        )
        self.assertNotIn("\n", maximum_rendered)
        self.assertLessEqual(len(maximum_rendered.encode("utf-8")), 1_800)

        class Closeable:
            closed = False

            def close(self):
                self.closed = True

        names = Closeable()
        listing.close_names(names)
        self.assertTrue(names.closed)

        class FakeOS:
            @staticmethod
            def ilistdir(path):
                self.assertEqual(path, "/")
                return iter((("first", 0, 0), ("second", 0, 0)))

        self.assertEqual(
            list(listing.read_folder_names(FakeOS, "/")),
            ["first", "second"],
        )


if __name__ == "__main__":
    unittest.main()
