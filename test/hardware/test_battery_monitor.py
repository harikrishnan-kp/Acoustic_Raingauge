import os

import pytest

from plugins.battery_monitor import BatteryMonitor


SERIAL_PORT = os.getenv("BATTERY_MONITOR_PORT", "/dev/ttyS0")
BAUDRATE = int(os.getenv("BATTERY_MONITOR_BAUDRATE", "9600"))


@pytest.mark.hardware
def test_battery_monitor_end_to_end():
    """
    End-to-end test using the real battery monitor hardware.

    The test:
        1. Opens the physical serial port.
        2. Reads a complete battery-monitor frame.
        3. Detects the start/end markers.
        4. Processes the four battery values.
        5. Validates the resulting measurements.
    """

    monitor = BatteryMonitor(
        port=SERIAL_PORT,
        baudrate=BAUDRATE,
    )

    solar_v, battery_v, solar_i, battery_charging_i = (
        monitor.get_dataframe()
    )

    assert solar_v is not None
    assert battery_v is not None
    assert solar_i is not None
    assert battery_charging_i is not None

    assert solar_v >= 0
    assert battery_v >= 0
    assert solar_i >= 0
    assert battery_charging_i >= 0


@pytest.mark.hardware
def test_battery_monitor_returns_reasonable_voltage_values():
    """
    Verify that the physical battery monitor returns plausible
    voltage measurements.
    """

    monitor = BatteryMonitor(
        port=SERIAL_PORT,
        baudrate=BAUDRATE,
    )

    solar_v, battery_v, _, _ = monitor.get_dataframe()

    assert solar_v is not None
    assert battery_v is not None

    # Adjust these limits according to the actual hardware.
    assert 0.0 <= solar_v <= 100.0
    assert 0.0 <= battery_v <= 100.0


@pytest.mark.hardware
def test_battery_monitor_returns_reasonable_current_values():
    """
    Verify that the physical battery monitor returns plausible
    current measurements.
    """

    monitor = BatteryMonitor(
        port=SERIAL_PORT,
        baudrate=BAUDRATE,
    )

    _, _, solar_i, battery_charging_i = monitor.get_dataframe()

    assert solar_i is not None
    assert battery_charging_i is not None

    # Adjust according to the actual hardware/current sensor.
    assert 0.0 <= solar_i <= 100.0
    assert 0.0 <= battery_charging_i <= 100.0