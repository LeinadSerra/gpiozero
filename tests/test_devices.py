from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import warnings

import pytest

from gpiozero import *


def teardown_function(function):
    Device._pin_factory.reset()


# TODO add more devices tests!

def test_device_bad_pin():
    with pytest.raises(GPIOPinMissing):
        device = GPIODevice()
    with pytest.raises(PinInvalidPin):
        device = GPIODevice(60)

def test_device_non_physical():
    with warnings.catch_warnings(record=True) as w:
        device = GPIODevice(37)
        assert len(w) == 1
        assert w[0].category == PinNonPhysical

def test_device_init():
    pin = Device._pin_factory.pin(2)
    with GPIODevice(pin) as device:
        assert not device.closed
        assert device.pin == pin

def test_device_init_twice_same_pin():
    with GPIODevice(2) as device:
        with pytest.raises(GPIOPinInUse):
            GPIODevice(2)

def test_device_init_twice_different_pin():
    with GPIODevice(2) as device:
        with GPIODevice(3) as device2:
            pass

def test_device_close():
    device = GPIODevice(2)
    device.close()
    assert device.closed
    assert device.pin is None

def test_device_reopen_same_pin():
    pin = Device._pin_factory.pin(2)
    device = GPIODevice(pin)
    device.close()
    device2 = GPIODevice(pin)
    assert not device2.closed
    assert device2.pin is pin
    assert device.closed
    assert device.pin is None
    device2.close()

def test_device_repr():
    with GPIODevice(2) as device:
        assert repr(device) == '<gpiozero.GPIODevice object on pin %s, is_active=False>' % device.pin

def test_device_repr_after_close():
    device = GPIODevice(2)
    device.close()
    assert repr(device) == '<gpiozero.GPIODevice object closed>'

def test_device_unknown_attr():
    with GPIODevice(2) as device:
        with pytest.raises(AttributeError):
            device.foo = 1

def test_device_context_manager():
    with GPIODevice(2) as device:
        assert not device.closed
    assert device.closed

def test_composite_device_sequence():
    with CompositeDevice(
            InputDevice(2),
            InputDevice(3)
            ) as device:
        assert len(device) == 2
        assert device[0].pin.number == 2
        assert device[1].pin.number == 3
        assert device.namedtuple._fields == ('_0', '_1')

def test_composite_device_values():
    with CompositeDevice(
            InputDevice(2),
            InputDevice(3)
            ) as device:
        assert device.value == (0, 0)
        assert not device.is_active
        device[0].pin.drive_high()
        assert device.value == (1, 0)
        assert device.is_active

def test_composite_device_named():
    with CompositeDevice(
            foo=InputDevice(2),
            bar=InputDevice(3),
            _order=('foo', 'bar')
            ) as device:
        assert device.namedtuple._fields == ('foo', 'bar')
        assert device.value == (0, 0)
        assert not device.is_active

def test_composite_device_bad_init():
    with pytest.raises(ValueError):
        CompositeDevice(foo=1, bar=2, _order=('foo',))
    with pytest.raises(ValueError):
        CompositeDevice(close=1)
    with pytest.raises(ValueError):
        CompositeDevice(2)
    with pytest.raises(ValueError):
        CompositeDevice(Device._pin_factory.pin(2))

def test_composite_device_read_only():
    with CompositeDevice(
        foo=InputDevice(2),
        bar=InputDevice(3)
        ) as device:
        with pytest.raises(AttributeError):
            device.foo = 1

