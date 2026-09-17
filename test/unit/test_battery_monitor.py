import struct
from unittest.mock import MagicMock, patch

import pytest
import serial

from plugins.battery_monitor import BatteryMonitor


@patch("battery_monitor.serial.Serial")
def test_setup_serial_connection(mock_serial):
    monitor = BatteryMonitor(
        port="/dev/ttyUSB0",
        baudrate=9600,
    )

    mock_serial.assert_called_once_with(
        "/dev/ttyUSB0",
        baudrate=9600,
        timeout=1,
    )

    assert monitor.ser == mock_serial.return_value


@patch("battery_monitor.serial.Serial")
def test_setup_serial_connection_failure(mock_serial):
    mock_serial.side_effect = serial.SerialException(
        "Connection failed"
    )

    with pytest.raises(SystemExit):
        BatteryMonitor(port="/dev/ttyUSB0")


@patch("battery_monitor.serial.Serial")
def test_read_uint8(mock_serial):
    mock_ser = MagicMock()
    mock_ser.read.return_value = struct.pack("B", 42)
    mock_serial.return_value = mock_ser

    monitor = BatteryMonitor()

    result = monitor.read_uint8()

    assert result == 42
    mock_ser.read.assert_called_once_with(1)


@patch("battery_monitor.serial.Serial")
def test_read_uint8_returns_none_when_no_data(mock_serial):
    mock_ser = MagicMock()
    mock_ser.read.return_value = b""
    mock_serial.return_value = mock_ser

    monitor = BatteryMonitor()

    result = monitor.read_uint8()

    assert result is None


@patch("battery_monitor.serial.Serial")
def test_read_uint8_handles_exception(mock_serial):
    mock_ser = MagicMock()
    mock_ser.read.side_effect = Exception("Read error")
    mock_serial.return_value = mock_ser

    monitor = BatteryMonitor()

    result = monitor.read_uint8()

    assert result is None


@patch("battery_monitor.serial.Serial")
def test_process_data(mock_serial):
    monitor = BatteryMonitor()

    values = [120, 130, 25, 15]

    result = monitor.process_data(values)

    assert result == (
        12.0,  # solar voltage
        13.0,  # battery voltage
        2.5,   # solar current
        1.5,   # battery charging current
    )


@patch("battery_monitor.serial.Serial")
def test_process_data_with_zero_values(mock_serial):
    monitor = BatteryMonitor()

    result = monitor.process_data([0, 0, 0, 0])

    assert result == (0.0, 0.0, 0.0, 0.0)


@pytest.mark.parametrize(
    "values",
    [
        [],
        [100],
        [100, 120],
        [100, 120, 10],
        [100, 120, 10, 5, 20],
    ],
)
@patch("battery_monitor.serial.Serial")
def test_process_data_with_invalid_length(mock_serial, values):
    monitor = BatteryMonitor()

    result = monitor.process_data(values)

    assert result == (None, None, None, None)