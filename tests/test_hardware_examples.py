# SPDX-License-Identifier: MIT
"""Behavior and lifecycle tests for all hardware-facing examples."""

import ast
from contextlib import redirect_stdout
import io
import json
import types
import unittest
from unittest.mock import patch

from support import (
    ROOT,
    FakeADC,
    FakeDisplay,
    FakeGC,
    FakeNeoPixel,
    FakePWM,
    FakePin,
    FakeSoftI2C,
    FakeSoftSPI,
    fake_modules,
    installed_modules,
    load_example,
)


PATHS = {
    "cap_blink": (
        "examples/capabilities/gpio/blink_external_led/"
        "pyble_gpio_blink.py"
    ),
    "cap_button": (
        "examples/capabilities/gpio/read_external_button/"
        "pyble_gpio_button.py"
    ),
    "cap_button_led": (
        "examples/capabilities/gpio/button_controls_led/"
        "pyble_gpio_button_led.py"
    ),
    "cap_pwm": (
        "examples/capabilities/gpio/pwm_fade/pyble_gpio_pwm_fade.py"
    ),
    "cap_adc": (
        "examples/capabilities/gpio/adc_sampling/pyble_gpio_adc_sampling.py"
    ),
    "cap_i2c": (
        "examples/capabilities/buses/i2c_scan/pyble_i2c_scan.py"
    ),
    "cap_spi": (
        "examples/capabilities/buses/spi_loopback/pyble_spi_loopback.py"
    ),
    "cap_pixel": (
        "examples/capabilities/neopixel/single_pixel/"
        "pyble_neopixel_single.py"
    ),
    "cap_chase": (
        "examples/capabilities/neopixel/strip_chase/"
        "pyble_neopixel_chase.py"
    ),
    "pico_led": (
        "examples/exact_hardware/rpi_pico2_w/onboard_led/"
        "pyble_pico2w_onboard_led.py"
    ),
    "pico_patterns": (
        "examples/exact_hardware/rpi_pico2_w/onboard_led_patterns/"
        "pyble_pico2w_led_patterns.py"
    ),
    "lcd_hello": (
        "examples/exact_hardware/waveshare_esp32_s3_lcd_147b/lcd_hello/"
        "pyble_waveshare_lcd147b_hello.py"
    ),
    "lcd_shapes": (
        "examples/exact_hardware/waveshare_esp32_s3_lcd_147b/lcd_shapes/"
        "pyble_waveshare_lcd147b_shapes.py"
    ),
    "lcd_dashboard": (
        "examples/exact_hardware/waveshare_esp32_s3_lcd_147b/"
        "lcd_dashboard/pyble_waveshare_lcd147b_dashboard.py"
    ),
    "lcd_pixel": (
        "examples/exact_hardware/waveshare_esp32_s3_lcd_147b/"
        "onboard_pixel/pyble_waveshare_lcd147b_pixel.py"
    ),
    "project_counter": (
        "examples/projects/button_press_counter/"
        "pyble_project_button_counter.py"
    ),
    "project_logger": (
        "examples/projects/adc_data_logger/pyble_project_adc_logger.py"
    ),
    "project_button_pixel": (
        "examples/projects/button_neopixel/pyble_project_button_neopixel.py"
    ),
}

CAPABILITY_NAMES = tuple(name for name in PATHS if name.startswith("cap_"))
PROJECT_NAMES = (
    "project_counter",
    "project_logger",
    "project_button_pixel",
)
LCD_NAMES = ("lcd_hello", "lcd_shapes", "lcd_dashboard")


class MemoryStream:
    """Minimal text stream that remains inspectable after close()."""

    def __init__(self):
        self.parts = []
        self.flush_count = 0
        self.closed = False

    @property
    def text(self):
        return "".join(self.parts)

    def write(self, text):
        self.parts.append(text)
        return len(text)

    def flush(self):
        self.flush_count += 1

    def close(self):
        self.closed = True


def run_main(module, replacements):
    """Run one example with fake modules and return bounded console output."""
    output = io.StringIO()
    with installed_modules(replacements), redirect_stdout(output):
        module.main()
    return output.getvalue()


def pin_with_identifier(identifier):
    """Return the unique constructed fake pin with an identifier."""
    matches = [pin for pin in FakePin.instances if pin.identifier == identifier]
    if len(matches) != 1:
        raise AssertionError(
            "expected one pin {!r}, found {}".format(identifier, len(matches))
        )
    return matches[0]


def missing_os_module():
    """Return an os fake whose stat() reports a missing path."""
    module = types.ModuleType("os")

    def missing(_path):
        raise OSError(2)

    module.stat = missing
    return module


def published_setup_values(example_name, constants):
    """Read concrete literals from one source's comment-only setup recipe."""
    source = (ROOT / PATHS[example_name]).read_text(encoding="utf-8")
    guide = source.split("# SETUP GUIDE", 1)[1].split(
        "# END OF SETUP GUIDE", 1
    )[0]
    values = {}
    for constant in constants:
        prefix = "# {} =".format(constant)
        matches = [line for line in guide.splitlines() if line.startswith(prefix)]
        if len(matches) != 1:
            raise AssertionError(
                "expected one example assignment for {} in {}".format(
                    constant, example_name
                )
            )
        assignment = ast.parse(matches[0][1:].lstrip()).body[0]
        values[constant] = ast.literal_eval(assignment.value)
    return values


class HardwareExamplesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = {}
        for name, relative in PATHS.items():
            module, stdout, stderr = load_example(relative)
            if stdout or stderr:
                raise AssertionError("{} import produced output".format(relative))
            cls.modules[name] = module

    def test_inventory_and_all_imports_are_inert(self):
        catalog = json.loads(
            (ROOT / "catalog/examples.json").read_text(encoding="utf-8")
        )
        expected = {
            record["path"] + "/" + record["entrypoint"]
            for record in catalog["examples"]
            if record["classification"]
            in ("capability", "exact-hardware", "project")
        }
        self.assertEqual(len(PATHS), 18)
        self.assertEqual(expected, set(PATHS.values()))

    def test_unset_generic_defaults_fail_before_hardware_imports(self):
        blocked_hardware = {"machine": None, "neopixel": None}
        with installed_modules(blocked_hardware):
            for name in CAPABILITY_NAMES + PROJECT_NAMES:
                with self.subTest(example=name):
                    with self.assertRaises(ValueError):
                        self.modules[name].main()

    def test_exact_board_guards_run_before_gpio_construction(self):
        replacements, _clock = fake_modules()
        module = self.modules["lcd_pixel"]
        self.assertIs(module.CONFIRM_EXACT_BOARD, False)
        with installed_modules(replacements):
            with self.assertRaisesRegex(RuntimeError, "CONFIRM_EXACT_BOARD"):
                module.main()
        self.assertEqual(FakePin.instances, [])

        for name in LCD_NAMES:
            replacements, _clock = fake_modules()
            replacements["pyble_waveshare_lcd147b"] = None
            with self.subTest(example=name), installed_modules(replacements):
                with self.assertRaisesRegex(RuntimeError, "requires"):
                    self.modules[name]._open_display()
                self.assertEqual(FakePin.instances, [])

    def test_capability_gpio_pure_seams(self):
        blink = self.modules["cap_blink"]
        self.assertEqual(blink.validate_config(1, 1, 2, 50), (1, 1, 2, 50))
        FakePin.reset()
        led = FakePin(1, FakePin.OUT, value=0)
        delays = []
        blink.run_blinks(led, 1, 2, 50, delays.append)
        self.assertEqual(delays, [50, 50, 50, 50])
        self.assertEqual(
            [item for item in led.history if item[0] == "value"],
            [("value", 1), ("value", 0), ("value", 1), ("value", 0)],
        )

        button = self.modules["cap_button"]
        self.assertEqual(
            button.validate_config(
                2,
                "up",
                0,
                button.SAMPLE_COUNT,
                button.SAMPLE_INTERVAL_MS,
            ),
            (2, "up", 0, 16, 200),
        )
        self.assertTrue(button.is_pressed(0, 0))
        self.assertFalse(button.is_pressed(1, 0))
        FakePin.reset()
        input_pin = FakePin(2, FakePin.IN, FakePin.PULL_UP)
        input_pin.level = 1
        output = []
        delays = []
        button.observe_button(input_pin, 0, 2, 20, delays.append, output.append)
        self.assertEqual(output, ["Button released."])
        self.assertEqual(delays, [20])

        combined = self.modules["cap_button_led"]
        self.assertEqual(combined.led_level_for_button(0, 0, 1), 1)
        self.assertEqual(combined.led_level_for_button(1, 0, 1), 0)

        pwm = self.modules["cap_pwm"]
        self.assertEqual(pwm.duty_sequence(8, 2), (0, 4, 8, 4, 0))

        adc = self.modules["cap_adc"]
        self.assertEqual(
            adc.validate_config(6, adc.SAMPLE_COUNT, adc.SAMPLE_INTERVAL_MS),
            (6, 12, 200),
        )
        self.assertEqual(adc.normalize_reading(0), 0.0)
        self.assertEqual(adc.normalize_reading(65535), 1.0)

    def test_capability_bus_and_pixel_pure_seams(self):
        i2c = self.modules["cap_i2c"]
        self.assertEqual(
            i2c.validate_config(1, 2, 100_000, 1_000),
            (1, 2, 100_000, 1_000),
        )
        with self.assertRaisesRegex(ValueError, "100 to 1000"):
            i2c.validate_config(1, 2, 100_000, 1_001)
        self.assertEqual(i2c.format_addresses((0x08, 0x3C)), "0x08, 0x3C")

        FakeSoftSPI.reset()
        spi_bus = FakeSoftSPI()
        spi = self.modules["cap_spi"]
        received = spi.perform_loopback(spi_bus, b"test")
        self.assertTrue(spi.loopback_matches(b"test", received))

        single = self.modules["cap_pixel"]
        self.assertEqual(single.PIXEL_COUNT, 1)
        self.assertEqual(single.validate_color((8, 1, 0)), (8, 1, 0))
        with self.assertRaises(ValueError):
            single.validate_color((17, 0, 0))

        chase = self.modules["cap_chase"]
        self.assertEqual(chase.chase_indices(3, 2), (0, 1, 2, 0, 1, 2))

    def test_published_setup_recipes_pass_the_example_validators(self):
        blink = self.modules["cap_blink"]
        values = published_setup_values(
            "cap_blink", ("LED_PIN", "LED_ACTIVE_LEVEL")
        )
        blink.validate_config(
            values["LED_PIN"],
            values["LED_ACTIVE_LEVEL"],
            blink.BLINK_COUNT,
            blink.STEP_DELAY_MS,
        )

        button = self.modules["cap_button"]
        values = published_setup_values(
            "cap_button", ("BUTTON_PIN", "BUTTON_PULL", "PRESSED_LEVEL")
        )
        button.validate_config(
            values["BUTTON_PIN"],
            values["BUTTON_PULL"],
            values["PRESSED_LEVEL"],
            button.SAMPLE_COUNT,
            button.SAMPLE_INTERVAL_MS,
        )

        combined = self.modules["cap_button_led"]
        values = published_setup_values(
            "cap_button_led",
            (
                "BUTTON_PIN",
                "BUTTON_PULL",
                "PRESSED_LEVEL",
                "LED_PIN",
                "LED_ACTIVE_LEVEL",
            ),
        )
        combined.validate_config(
            values["BUTTON_PIN"],
            values["BUTTON_PULL"],
            values["PRESSED_LEVEL"],
            values["LED_PIN"],
            values["LED_ACTIVE_LEVEL"],
            combined.SAMPLE_COUNT,
            combined.SAMPLE_INTERVAL_MS,
        )

        pwm = self.modules["cap_pwm"]
        values = published_setup_values(
            "cap_pwm", ("PWM_PIN", "PWM_FREQUENCY_HZ")
        )
        pwm.validate_config(
            values["PWM_PIN"],
            values["PWM_FREQUENCY_HZ"],
            pwm.MAX_DUTY_U16,
            pwm.FADE_STEPS,
            pwm.FADE_CYCLES,
            pwm.STEP_DELAY_MS,
        )

        adc = self.modules["cap_adc"]
        values = published_setup_values("cap_adc", ("ADC_PIN",))
        adc.validate_config(
            values["ADC_PIN"], adc.SAMPLE_COUNT, adc.SAMPLE_INTERVAL_MS
        )

        i2c = self.modules["cap_i2c"]
        values = published_setup_values(
            "cap_i2c", ("SDA_PIN", "SCL_PIN", "I2C_FREQUENCY_HZ")
        )
        i2c.validate_config(
            values["SDA_PIN"],
            values["SCL_PIN"],
            values["I2C_FREQUENCY_HZ"],
            i2c.I2C_TIMEOUT_US,
        )

        spi = self.modules["cap_spi"]
        values = published_setup_values(
            "cap_spi",
            ("SCK_PIN", "MOSI_PIN", "MISO_PIN", "SPI_BAUDRATE_HZ"),
        )
        spi.validate_config(
            values["SCK_PIN"],
            values["MOSI_PIN"],
            values["MISO_PIN"],
            values["SPI_BAUDRATE_HZ"],
            spi.LOOPBACK_PAYLOAD,
        )

        single = self.modules["cap_pixel"]
        values = published_setup_values("cap_pixel", ("PIXEL_PIN",))
        single.validate_config(
            values["PIXEL_PIN"],
            single.PIXEL_COUNT,
            single.DIM_COLORS,
            single.COLOR_DELAY_MS,
        )

        chase = self.modules["cap_chase"]
        values = published_setup_values(
            "cap_chase", ("PIXEL_PIN", "PIXEL_COUNT")
        )
        chase.validate_config(
            values["PIXEL_PIN"],
            values["PIXEL_COUNT"],
            chase.CHASE_COLOR,
            chase.CHASE_CYCLES,
            chase.STEP_DELAY_MS,
            chase.MAX_PIXEL_COUNT,
        )

        exact_pixel = self.modules["lcd_pixel"]
        values = published_setup_values(
            "lcd_pixel", ("CONFIRM_EXACT_BOARD",)
        )
        self.assertIs(values["CONFIRM_EXACT_BOARD"], True)
        exact_pixel.validate_colors(
            exact_pixel.DIM_COLORS, exact_pixel.PIXEL_HOLD_MS
        )

        counter = self.modules["project_counter"]
        values = published_setup_values(
            "project_counter", ("BUTTON_PIN", "BUTTON_PULL", "PRESSED_LEVEL")
        )
        counter.validate_configuration(
            values["BUTTON_PIN"],
            values["BUTTON_PULL"],
            values["PRESSED_LEVEL"],
        )

        logger = self.modules["project_logger"]
        values = published_setup_values("project_logger", ("ADC_PIN",))
        logger.validate_configuration(values["ADC_PIN"])

        button_pixel = self.modules["project_button_pixel"]
        values = published_setup_values(
            "project_button_pixel",
            (
                "BUTTON_PIN",
                "BUTTON_PULL",
                "PRESSED_LEVEL",
                "PIXEL_PIN",
                "PIXEL_COUNT",
            ),
        )
        button_pixel.validate_configuration(
            values["BUTTON_PIN"],
            values["BUTTON_PULL"],
            values["PRESSED_LEVEL"],
            values["PIXEL_PIN"],
            values["PIXEL_COUNT"],
        )

    def test_exact_hardware_pure_seams(self):
        pico = self.modules["pico_led"]
        self.assertEqual(
            pico.blink_steps(1, 20, 30),
            ((1, 20), (0, 30)),
        )

        patterns = self.modules["pico_patterns"]
        checked = patterns.validate_patterns((("pulse", ((1, 20), (0, 20))),))
        self.assertEqual(checked, (("pulse", ((1, 20), (0, 20))),))

        display = FakeDisplay()
        self.modules["lcd_hello"].draw_hello(display, lambda *rgb: rgb)
        self.assertIn("text", [operation[0] for operation in display.operations])

        display = FakeDisplay()
        self.modules["lcd_shapes"].draw_shapes(display, lambda *rgb: rgb)
        names = {operation[0] for operation in display.operations}
        self.assertTrue({"fill", "pixel", "line", "rect", "text"} <= names)

        dashboard = self.modules["lcd_dashboard"]
        lines = dashboard.dashboard_values(1, 20, 30)
        self.assertEqual(lines, ("Frame 1/5", "Elapsed: 20 ms", "Free: 30 B"))
        display = FakeDisplay()
        dashboard.draw_dashboard(display, lambda *rgb: rgb, lines, 30)
        self.assertIn("fill_rect", [item[0] for item in display.operations])

        pixel = self.modules["lcd_pixel"]
        self.assertEqual(pixel.validate_colors(((8, 0, 0),), 50), ((8, 0, 0),))

    def test_project_pure_seams(self):
        counter = self.modules["project_counter"]
        self.assertEqual(
            counter.validate_configuration(15, "up", 0),
            (15, "up", 0),
        )
        with self.assertRaisesRegex(ValueError, "pull-up"):
            counter.validate_configuration(1, "up", 1)
        state = (0, 0, 3, False)
        for _ in range(3):
            state = counter.debounce_step(1, state[0], state[1], state[2], 3)
        self.assertEqual(state, (1, 1, 3, True))

        logger = self.modules["project_logger"]
        self.assertEqual(logger.validate_configuration(26), 26)
        self.assertEqual(logger.LOG_PATH, "/examples/pyble_adc_log.csv")
        self.assertEqual(
            logger.csv_sample_line(0, 10, 65_535),
            "0,10,65535,1000\n",
        )
        stream = MemoryStream()
        count = logger.write_bounded(stream, "abc", 0, 3)
        self.assertEqual((count, stream.text), (3, "abc"))
        with self.assertRaises(RuntimeError):
            logger.write_bounded(stream, "d", count, 3)

        button_pixel = self.modules["project_button_pixel"]
        self.assertEqual(
            button_pixel.validate_configuration(25, "up", 0, 27, 1),
            (25, "up", 0, 27, 1),
        )
        with self.assertRaisesRegex(ValueError, "pull-down"):
            button_pixel.validate_configuration(1, "down", 0, 2, 1)
        self.assertEqual(button_pixel.color_for_level(0, 0), (0, 8, 0))
        self.assertEqual(button_pixel.color_for_level(1, 0), (0, 0, 0))

    def test_fixed_safety_caps_and_unambiguous_pin_ids(self):
        chase = self.modules["cap_chase"]
        with self.assertRaisesRegex(ValueError, "fixed safety cap"):
            chase.validate_config(1, 1, (8, 2, 0), 1, 20, 64)

        pico = self.modules["pico_led"]
        with self.assertRaisesRegex(ValueError, "within 5 seconds"):
            pico.blink_steps(20, 2_000, 2_000)

        button_pixel = self.modules["project_button_pixel"]
        with patch.object(button_pixel, "MAX_PIXELS", 17):
            with self.assertRaisesRegex(ValueError, "fixed safety cap"):
                button_pixel.validate_configuration(1, "up", 0, 2, 1)
        with patch.object(button_pixel, "DIM_ACTIVE_COLOR", (17, 0, 0)):
            with self.assertRaisesRegex(ValueError, "channels"):
                button_pixel.validate_configuration(1, "up", 0, 2, 1)

        with self.assertRaisesRegex(ValueError, "numeric GPIO"):
            self.modules["cap_button_led"].validate_config(
                "GPIO1", "up", 0, "GPIO2", 1, 1, 20
            )
        with self.assertRaisesRegex(ValueError, "numeric GPIO"):
            self.modules["cap_i2c"].validate_config(
                "GPIO1", "GPIO2", 100_000, 1_000
            )
        with self.assertRaisesRegex(ValueError, "numeric GPIO"):
            self.modules["cap_spi"].validate_config(
                "GPIO1", "GPIO2", "GPIO3", 100_000, b"x"
            )
        with self.assertRaisesRegex(ValueError, "numeric GPIO"):
            button_pixel.validate_configuration(
                "GPIO1", "up", 0, "GPIO2", 1
            )

    def test_runtime_budgets_reject_oversized_paced_work(self):
        with self.assertRaisesRegex(ValueError, "5 seconds"):
            self.modules["cap_blink"].validate_config(1, 1, 20, 2_000)
        with self.assertRaisesRegex(ValueError, "5 seconds"):
            self.modules["cap_button"].validate_config(
                1, "up", 0, 50, 20
            )
        self.assertEqual(
            self.modules["cap_button"].validate_config(1, "up", 0, 49, 20),
            (1, "up", 0, 49, 20),
        )
        with self.assertRaisesRegex(ValueError, "5 seconds"):
            self.modules["cap_button_led"].validate_config(
                1, "up", 0, 2, 1, 200, 1_000
            )
        with self.assertRaisesRegex(ValueError, "5 seconds"):
            self.modules["cap_pwm"].validate_config(
                1, 1_000, 16_384, 32, 5, 1_000
            )
        with self.assertRaisesRegex(ValueError, "3.5 seconds"):
            self.modules["cap_adc"].validate_config(1, 35, 20)
        self.assertEqual(
            self.modules["cap_adc"].validate_config(1, 34, 20),
            (1, 34, 20),
        )
        with self.assertRaisesRegex(ValueError, "4 seconds"):
            self.modules["cap_pixel"].validate_config(
                1, 1, ((8, 0, 0),) * 8, 2_000
            )
        with self.assertRaisesRegex(ValueError, "6 seconds"):
            self.modules["cap_chase"].validate_config(
                1, 32, (8, 2, 0), 5, 1_000, 32
            )

        with self.assertRaisesRegex(ValueError, "4 seconds"):
            self.modules["pico_patterns"].validate_patterns(
                (("long", ((1, 2_000), (0, 2_000), (1, 2_000))),)
            )
        with self.assertRaisesRegex(ValueError, "50..3000"):
            self.modules["lcd_hello"].validate_hold_ms(3_001)
        with self.assertRaisesRegex(ValueError, "50..4000"):
            self.modules["lcd_shapes"].validate_hold_ms(4_001)
        with self.assertRaisesRegex(ValueError, "2 seconds"):
            self.modules["lcd_pixel"].validate_colors(
                ((8, 0, 0), (0, 8, 0)), 2_000
            )
        dashboard = self.modules["lcd_dashboard"]
        with patch.multiple(
            dashboard,
            FRAME_COUNT=10,
            FRAME_INTERVAL_MS=2_000,
        ), self.assertRaisesRegex(ValueError, "4 seconds"):
            dashboard.main()

        logger = self.modules["project_logger"]
        with patch.multiple(
            logger,
            SAMPLE_COUNT=32,
            SAMPLE_INTERVAL_MS=2_000,
        ), self.assertRaisesRegex(ValueError, "3 seconds"):
            logger.validate_configuration(1)

        counter = self.modules["project_counter"]
        self.assertEqual(counter.press_report(12), "Press 12")
        self.assertIn("without per-press", counter.press_report(13))
        self.assertIsNone(counter.press_report(14))
        with patch.object(counter, "MAX_REPORTED_PRESSES", 13):
            with self.assertRaisesRegex(ValueError, "fixed output cap"):
                counter.validate_configuration(1, "up", 0)

        button_pixel = self.modules["project_button_pixel"]
        with patch.object(button_pixel, "OBSERVATION_MS", 9_000):
            with self.assertRaisesRegex(ValueError, "1000..8000"):
                button_pixel.validate_configuration(1, "up", 0, 2, 1)

    def test_capability_gpio_mains_complete_and_cleanup(self):
        module = self.modules["cap_blink"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            LED_PIN=1,
            LED_ACTIVE_LEVEL=1,
            BLINK_COUNT=2,
            STEP_DELAY_MS=50,
        ):
            self.assertIn("Blink complete", run_main(module, replacements))
        led = pin_with_identifier(1)
        self.assertEqual((led.level, led.mode, led.pull), (0, FakePin.IN, None))

        module = self.modules["cap_button"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            BUTTON_PIN=2,
            BUTTON_PULL="up",
            PRESSED_LEVEL=0,
            SAMPLE_COUNT=2,
            SAMPLE_INTERVAL_MS=20,
        ):
            self.assertIn("observation complete", run_main(module, replacements))
        button = pin_with_identifier(2)
        self.assertEqual((button.mode, button.pull), (FakePin.IN, None))

        module = self.modules["cap_button_led"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            BUTTON_PIN=3,
            BUTTON_PULL="up",
            PRESSED_LEVEL=0,
            LED_PIN=4,
            LED_ACTIVE_LEVEL=1,
            SAMPLE_COUNT=2,
            SAMPLE_INTERVAL_MS=20,
        ):
            run_main(module, replacements)
        button = pin_with_identifier(3)
        led = pin_with_identifier(4)
        self.assertEqual((button.mode, button.pull), (FakePin.IN, None))
        self.assertEqual((led.level, led.mode), (0, FakePin.IN))
        self.assertIn(("value", 1), led.history)

        module = self.modules["cap_pwm"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            PWM_PIN=5,
            PWM_FREQUENCY_HZ=1_000,
            FADE_STEPS=2,
            FADE_CYCLES=1,
            STEP_DELAY_MS=50,
        ):
            run_main(module, replacements)
        pwm = FakePWM.instances[-1]
        self.assertTrue(pwm.deinitialized)
        self.assertEqual(pwm.duties[-1], 0)
        self.assertEqual(pwm.pin.mode, FakePin.IN)

        module = self.modules["cap_adc"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            ADC_PIN=6,
            SAMPLE_COUNT=2,
            SAMPLE_INTERVAL_MS=20,
        ):
            run_main(module, replacements)
        adc = FakeADC.instances[-1]
        self.assertTrue(adc.deinitialized)
        self.assertEqual(adc.pin.mode, FakePin.IN)

    def test_capability_bus_mains_complete_and_cleanup(self):
        module = self.modules["cap_i2c"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            SDA_PIN=7,
            SCL_PIN=8,
            I2C_FREQUENCY_HZ=100_000,
            I2C_TIMEOUT_US=1_000,
        ):
            output = run_main(module, replacements)
        self.assertIn("0x3C", output)
        self.assertEqual(FakeSoftI2C.instances[-1].kwargs["timeout"], 1_000)
        self.assertTrue(
            all(pin.mode == FakePin.IN for pin in FakePin.instances)
        )

        module = self.modules["cap_spi"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            SCK_PIN=9,
            MOSI_PIN=10,
            MISO_PIN=11,
            SPI_BAUDRATE_HZ=100_000,
        ):
            output = run_main(module, replacements)
        self.assertIn("SPI loopback PASS", output)
        self.assertTrue(
            all(pin.mode == FakePin.IN for pin in FakePin.instances)
        )

    def test_capability_neopixel_mains_complete_and_cleanup(self):
        module = self.modules["cap_pixel"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            PIXEL_PIN=12,
            PIXEL_COUNT=1,
            DIM_COLORS=((8, 0, 0),),
            COLOR_DELAY_MS=20,
        ):
            run_main(module, replacements)
        pixels = FakeNeoPixel.instances[-1]
        self.assertEqual(pixels.values, [(0, 0, 0)])
        self.assertEqual(pixels.write_count, 2)
        self.assertEqual(pixels.pin.mode, FakePin.IN)

        module = self.modules["cap_chase"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            PIXEL_PIN=13,
            PIXEL_COUNT=3,
            CHASE_CYCLES=1,
            STEP_DELAY_MS=20,
        ):
            run_main(module, replacements)
        pixels = FakeNeoPixel.instances[-1]
        self.assertEqual(pixels.values, [(0, 0, 0)] * 3)
        self.assertEqual(pixels.write_count, 4)
        self.assertEqual(pixels.pin.mode, FakePin.IN)

    def test_exact_pico_mains_complete_and_leave_led_off(self):
        module = self.modules["pico_led"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            BLINK_COUNT=1,
            ON_TIME_MS=20,
            OFF_TIME_MS=20,
        ):
            run_main(module, replacements)
        self.assertEqual(pin_with_identifier("LED").level, 0)

        module = self.modules["pico_patterns"]
        replacements, _clock = fake_modules()
        with patch.object(module, "PATTERNS", (("pulse", ((1, 20), (0, 20))),)):
            run_main(module, replacements)
        self.assertEqual(pin_with_identifier("LED").level, 0)

    def test_exact_lcd_mains_complete_and_deinitialize(self):
        for name in LCD_NAMES:
            replacements, _clock = fake_modules()
            gc_module = None
            if name == "lcd_dashboard":
                gc_module = FakeGC()
                replacements["gc"] = gc_module
                patches = {"FRAME_COUNT": 2, "FRAME_INTERVAL_MS": 100}
            else:
                patches = {"DISPLAY_HOLD_MS": 50}
            with self.subTest(example=name), patch.multiple(
                self.modules[name], **patches
            ):
                run_main(self.modules[name], replacements)
            display = FakeDisplay.instances[-1]
            self.assertFalse(display.backlight_state)
            self.assertTrue(display.deinitialized)
            names = [operation[0] for operation in display.operations]
            self.assertIn("show", names)
            self.assertIn(("backlight", (True,)), display.operations)
            self.assertIn(("backlight", (False,)), display.operations)
            if gc_module is not None:
                self.assertEqual(gc_module.collections, 2)

    def test_exact_onboard_pixel_main_completes_and_turns_off(self):
        module = self.modules["lcd_pixel"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            CONFIRM_EXACT_BOARD=True,
            PIXEL_HOLD_MS=50,
            DIM_COLORS=((8, 0, 0),),
        ):
            run_main(module, replacements)
        pixels = FakeNeoPixel.instances[-1]
        self.assertEqual(pixels.values, [(0, 0, 0)])
        self.assertEqual(pixels.write_count, 2)
        self.assertEqual(pin_with_identifier(38).level, 0)

    def test_project_mains_complete_and_cleanup(self):
        module = self.modules["project_counter"]
        replacements, clock = fake_modules()
        with patch.multiple(
            module,
            BUTTON_PIN=20,
            BUTTON_PULL="up",
            PRESSED_LEVEL=0,
            OBSERVATION_MS=1_000,
            POLL_MS=100,
            DEBOUNCE_MS=100,
        ):
            run_main(module, replacements)
        button = pin_with_identifier(20)
        self.assertEqual((button.mode, button.pull), (FakePin.IN, None))
        self.assertGreaterEqual(len(clock.sleep_calls), 8)
        self.assertLessEqual(sum(clock.sleep_calls), 1_000)

        module = self.modules["project_logger"]
        replacements, _clock = fake_modules()
        replacements["os"] = missing_os_module()
        stream = MemoryStream()

        def fake_open(path, mode):
            self.assertEqual((path, mode), (module.LOG_PATH, "x"))
            return stream

        with patch.multiple(
            module,
            ADC_PIN=21,
            SAMPLE_COUNT=2,
            SAMPLE_INTERVAL_MS=50,
        ), patch("builtins.open", side_effect=fake_open):
            output = run_main(module, replacements)
        self.assertTrue(stream.closed)
        self.assertIn(
            "sample,elapsed_ms,raw_0_to_65535,scaled_0_to_1000",
            stream.text,
        )
        self.assertIn("Retained", output)
        self.assertTrue(FakeADC.instances[-1].deinitialized)
        self.assertEqual(FakeADC.instances[-1].pin.mode, FakePin.IN)

        module = self.modules["project_button_pixel"]
        replacements, clock = fake_modules()
        with patch.multiple(
            module,
            BUTTON_PIN=22,
            BUTTON_PULL="up",
            PRESSED_LEVEL=0,
            PIXEL_PIN=23,
            PIXEL_COUNT=2,
            OBSERVATION_MS=1_000,
            POLL_MS=200,
        ):
            run_main(module, replacements)
        pixels = FakeNeoPixel.instances[-1]
        self.assertEqual(pixels.values, [(0, 0, 0)] * 2)
        self.assertEqual(pin_with_identifier(23).level, 0)
        button = pin_with_identifier(22)
        self.assertEqual((button.mode, button.pull), (FakePin.IN, None))
        self.assertEqual(len(clock.sleep_calls), 5)

    def test_representative_stop_paths_cleanup_every_resource_kind(self):
        module = self.modules["cap_blink"]
        replacements, _clock = fake_modules(interrupt_after=1)
        with patch.multiple(
            module,
            LED_PIN=30,
            LED_ACTIVE_LEVEL=1,
            BLINK_COUNT=2,
            STEP_DELAY_MS=50,
        ), installed_modules(replacements), redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.main()
        led = pin_with_identifier(30)
        self.assertEqual((led.level, led.mode), (0, FakePin.IN))

        module = self.modules["cap_pwm"]
        replacements, _clock = fake_modules(interrupt_after=1)
        with patch.multiple(
            module,
            PWM_PIN=31,
            PWM_FREQUENCY_HZ=1_000,
            FADE_STEPS=2,
            FADE_CYCLES=1,
            STEP_DELAY_MS=20,
        ), installed_modules(replacements), redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.main()
        self.assertTrue(FakePWM.instances[-1].deinitialized)
        self.assertEqual(FakePWM.instances[-1].duties[-1], 0)
        self.assertEqual(FakePWM.instances[-1].pin.mode, FakePin.IN)

        module = self.modules["cap_i2c"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            SDA_PIN=35,
            SCL_PIN=36,
            I2C_FREQUENCY_HZ=100_000,
            I2C_TIMEOUT_US=1_000,
        ), patch.object(
            FakeSoftI2C, "scan", side_effect=KeyboardInterrupt
        ), installed_modules(replacements), redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.main()
        self.assertTrue(
            all(pin.mode == FakePin.IN for pin in FakePin.instances)
        )

        module = self.modules["cap_spi"]
        replacements, _clock = fake_modules()
        with patch.multiple(
            module,
            SCK_PIN=37,
            MOSI_PIN=38,
            MISO_PIN=39,
            SPI_BAUDRATE_HZ=100_000,
        ), patch.object(
            FakeSoftSPI, "write_readinto", side_effect=KeyboardInterrupt
        ), installed_modules(replacements), redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.main()
        self.assertTrue(
            all(pin.mode == FakePin.IN for pin in FakePin.instances)
        )

        module = self.modules["lcd_hello"]
        replacements, _clock = fake_modules(interrupt_after=1)
        with patch.object(module, "DISPLAY_HOLD_MS", 50), installed_modules(
            replacements
        ), redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.main()
        display = FakeDisplay.instances[-1]
        self.assertFalse(display.backlight_state)
        self.assertTrue(display.deinitialized)

        module = self.modules["lcd_pixel"]
        replacements, _clock = fake_modules(interrupt_after=1)
        with patch.multiple(
            module,
            CONFIRM_EXACT_BOARD=True,
            PIXEL_HOLD_MS=50,
            DIM_COLORS=((8, 0, 0),),
        ), installed_modules(replacements), redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.main()
        self.assertEqual(FakeNeoPixel.instances[-1].values, [(0, 0, 0)])
        self.assertEqual(pin_with_identifier(38).level, 0)

        module = self.modules["project_logger"]
        replacements, _clock = fake_modules(interrupt_after=1)
        replacements["os"] = missing_os_module()
        stream = MemoryStream()
        with patch.multiple(
            module,
            ADC_PIN=32,
            SAMPLE_COUNT=2,
            SAMPLE_INTERVAL_MS=50,
        ), patch("builtins.open", return_value=stream), installed_modules(
            replacements
        ), redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.main()
        self.assertTrue(stream.closed)
        self.assertTrue(FakeADC.instances[-1].deinitialized)
        self.assertEqual(FakeADC.instances[-1].pin.mode, FakePin.IN)

        module = self.modules["project_button_pixel"]
        replacements, _clock = fake_modules(interrupt_after=1)
        with patch.multiple(
            module,
            BUTTON_PIN=33,
            BUTTON_PULL="up",
            PRESSED_LEVEL=0,
            PIXEL_PIN=34,
            PIXEL_COUNT=2,
            OBSERVATION_MS=1_000,
            POLL_MS=200,
        ), installed_modules(replacements), redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                module.main()
        self.assertEqual(FakeNeoPixel.instances[-1].values, [(0, 0, 0)] * 2)
        self.assertEqual(pin_with_identifier(34).level, 0)
        button = pin_with_identifier(33)
        self.assertEqual((button.mode, button.pull), (FakePin.IN, None))


if __name__ == "__main__":
    unittest.main()
