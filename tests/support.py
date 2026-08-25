# SPDX-License-Identifier: MIT
"""Host-only loading and fake-hardware helpers for example tests."""

from contextlib import contextmanager, redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import sys
import types
import uuid


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def load_example(relative_path):
    """Import one example under a fresh name and return it plus captured I/O."""
    path = ROOT / relative_path
    name = "_pyble_example_test_" + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load {}".format(path))
    module = importlib.util.module_from_spec(spec)
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        spec.loader.exec_module(module)
    return module, stdout.getvalue(), stderr.getvalue()


@contextmanager
def installed_modules(replacements):
    """Temporarily install deterministic fake modules in ``sys.modules``."""
    missing = object()
    previous = {name: sys.modules.get(name, missing) for name in replacements}
    sys.modules.update(replacements)
    try:
        yield
    finally:
        for name, value in previous.items():
            if value is missing:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


class FakePin:
    IN = 0
    OUT = 1
    PULL_UP = 2
    PULL_DOWN = 3
    instances = []
    default_input = 0

    def __init__(self, identifier, mode=None, pull=None, value=None, **kwargs):
        self.identifier = identifier
        self.mode = mode
        self.pull = pull
        self.level = self.default_input if value is None else value
        self.history = [("construct", mode, pull, value, kwargs)]
        self.__class__.instances.append(self)

    @classmethod
    def reset(cls):
        cls.instances = []
        cls.default_input = 0

    def value(self, new_value=None):
        if new_value is None:
            self.history.append(("read", self.level))
            return self.level
        self.level = new_value
        self.history.append(("value", new_value))
        return None

    def __call__(self, new_value=None):
        return self.value(new_value)

    def init(self, mode=None, pull=None, **kwargs):
        self.mode = mode
        self.pull = pull
        self.history.append(("init", mode, pull, kwargs))


class FakePWM:
    instances = []

    def __init__(self, pin, freq, duty_u16):
        self.pin = pin
        self.freq = freq
        self.duties = [duty_u16]
        self.deinitialized = False
        self.__class__.instances.append(self)

    @classmethod
    def reset(cls):
        cls.instances = []

    def duty_u16(self, value):
        self.duties.append(value)

    def deinit(self):
        self.deinitialized = True


class FakeADC:
    instances = []

    def __init__(self, pin):
        self.pin = pin
        self.deinitialized = False
        self.read_count = 0
        self.__class__.instances.append(self)

    @classmethod
    def reset(cls):
        cls.instances = []

    def read_u16(self):
        self.read_count += 1
        return min(65535, 1000 * self.read_count)

    def deinit(self):
        self.deinitialized = True


class FakeSoftI2C:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.__class__.instances.append(self)

    @classmethod
    def reset(cls):
        cls.instances = []

    def scan(self):
        return [0x3C]


class FakeSoftSPI:
    MSB = 0
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.deinitialized = False
        self.__class__.instances.append(self)

    @classmethod
    def reset(cls):
        cls.instances = []

    def write_readinto(self, sent, received):
        received[:] = sent

    def deinit(self):
        self.deinitialized = True


class FakeNeoPixel:
    instances = []

    def __init__(self, pin, count):
        self.pin = pin
        self.values = [(0, 0, 0)] * count
        self.write_count = 0
        self.__class__.instances.append(self)

    @classmethod
    def reset(cls):
        cls.instances = []

    def __len__(self):
        return len(self.values)

    def __setitem__(self, index, value):
        self.values[index] = tuple(value)

    def __getitem__(self, index):
        return self.values[index]

    def fill(self, value):
        self.values = [tuple(value)] * len(self.values)

    def write(self):
        self.write_count += 1


class FakeDisplay:
    instances = []

    def __init__(self, *args):
        self.args = args
        self.operations = []
        self.backlight_state = False
        self.deinitialized = False
        self.__class__.instances.append(self)

    @classmethod
    def reset(cls):
        cls.instances = []

    def _record(self, name, *args):
        self.operations.append((name, args))

    def fill(self, *args):
        self._record("fill", *args)

    def fill_rect(self, *args):
        self._record("fill_rect", *args)

    def pixel(self, *args):
        self._record("pixel", *args)

    def line(self, *args):
        self._record("line", *args)

    def rect(self, *args):
        self._record("rect", *args)

    def text(self, *args):
        self._record("text", *args)

    def show(self):
        self._record("show")

    def backlight(self, enabled):
        self.backlight_state = enabled
        self._record("backlight", enabled)

    def deinit(self):
        self.deinitialized = True
        self._record("deinit")


class FakeClock:
    def __init__(self, interrupt_after=None):
        self.sleep_calls = []
        self.now = 0
        self.interrupt_after = interrupt_after

    def sleep_ms(self, duration):
        self.sleep_calls.append(duration)
        self.now += duration
        should_interrupt = (
            self.interrupt_after is not None
            and len(self.sleep_calls) >= self.interrupt_after
        )
        if should_interrupt:
            raise KeyboardInterrupt()

    def ticks_ms(self):
        self.now += 10
        return self.now

    @staticmethod
    def ticks_diff(new, old):
        return new - old


class FakeGC(types.ModuleType):
    def __init__(self):
        super().__init__("gc")
        self.collections = 0

    def collect(self):
        self.collections += 1

    @staticmethod
    def mem_free():
        return 123456


def reset_fakes():
    for fake in (FakePin, FakePWM, FakeADC, FakeSoftI2C, FakeSoftSPI,
                 FakeNeoPixel, FakeDisplay):
        fake.reset()


def fake_modules(interrupt_after=None):
    """Return a complete module map and its controllable fake clock."""
    reset_fakes()
    machine = types.ModuleType("machine")
    machine.Pin = FakePin
    machine.PWM = FakePWM
    machine.ADC = FakeADC
    machine.SoftI2C = FakeSoftI2C
    machine.SoftSPI = FakeSoftSPI

    neopixel = types.ModuleType("neopixel")
    neopixel.NeoPixel = FakeNeoPixel

    clock = FakeClock(interrupt_after=interrupt_after)
    time_module = types.ModuleType("time")
    time_module.sleep_ms = clock.sleep_ms
    time_module.ticks_ms = clock.ticks_ms
    time_module.ticks_diff = clock.ticks_diff

    display = types.ModuleType("pyble_st7789")
    display.ST7789 = FakeDisplay
    display.rgb565 = lambda red, green, blue: (red, green, blue)

    marker = types.ModuleType("pyble_waveshare_lcd147b")
    return {
        "machine": machine,
        "neopixel": neopixel,
        "time": time_module,
        "pyble_st7789": display,
        "pyble_waveshare_lcd147b": marker,
    }, clock
