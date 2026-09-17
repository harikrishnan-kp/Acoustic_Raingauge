# as a complete data-reading flow using a mocked serial device.

from unittest.mock import MagicMock, patch

from plugins.battery_monitor import BatteryMonitor


@patch("battery_monitor.serial.Serial")
def test_get_dataframe(mock_serial):
    mock_ser = MagicMock()
    mock_serial.return_value = mock_ser

    mock_ser.read.side_effect = [
        b"\x15",  # 21 - start marker
        b"\x78",  # 120 - solar voltage
        b"\x82",  # 130 - battery voltage
        b"\x19",  # 25 - solar current
        b"\x0f",  # 15 - charging current
        b"\x4b",  # 75 - end marker
    ]

    monitor = BatteryMonitor()

    result = monitor.get_dataframe()

    assert result == (
        12.0,
        13.0,
        2.5,
        1.5,
    )


@patch("battery_monitor.serial.Serial")
def test_get_dataframe_ignores_data_before_start_marker(mock_serial):
    mock_ser = MagicMock()
    mock_serial.return_value = mock_ser

    mock_ser.read.side_effect = [
        b"\x01",  # ignored
        b"\x02",  # ignored
        b"\x10",  # ignored
        b"\x15",  # start marker
        b"\x64",  # 100
        b"\x78",  # 120
        b"\x0a",  # 10
        b"\x05",  # 5
        b"\x4b",  # end marker
    ]

    monitor = BatteryMonitor()

    result = monitor.get_dataframe()

    assert result == (
        10.0,
        12.0,
        1.0,
        0.5,
    )


@patch("battery_monitor.serial.Serial")
def test_get_dataframe_reads_four_values(mock_serial):
    mock_ser = MagicMock()
    mock_serial.return_value = mock_ser

    mock_ser.read.side_effect = [
        b"\x15",  # start
        b"\x64",  # 100
        b"\x78",  # 120
        b"\x0a",  # 10
        b"\x05",  # 5
        b"\x4b",  # end
    ]

    monitor = BatteryMonitor()

    result = monitor.get_dataframe()

    assert result == (
        10.0,
        12.0,
        1.0,
        0.5,
    )

    assert mock_ser.read.call_count == 6


@patch("battery_monitor.serial.Serial")
def test_get_dataframe_passes_values_to_process_data(mock_serial):
    mock_ser = MagicMock()
    mock_serial.return_value = mock_ser

    mock_ser.read.side_effect = [
        b"\x15",
        b"\x64",
        b"\x78",
        b"\x0a",
        b"\x05",
        b"\x4b",
    ]

    monitor = BatteryMonitor()

    with patch.object(
        monitor,
        "process_data",
        return_value=(10.0, 12.0, 1.0, 0.5),
    ) as mock_process_data:

        result = monitor.get_dataframe()

    assert result == (
        10.0,
        12.0,
        1.0,
        0.5,
    )

    mock_process_data.assert_called_once_with(
        [100, 120, 10, 5]
    )


@patch("battery_monitor.serial.Serial")
def test_get_dataframe_with_missing_value(mock_serial):
    mock_ser = MagicMock()
    mock_serial.return_value = mock_ser

    mock_ser.read.side_effect = [
        b"\x15",  # start
        b"\x64",  # 100
        b"",      # no data
        b"\x0a",  # 10
        b"\x05",  # 5
        b"\x4b",  # end
    ]

    monitor = BatteryMonitor()

    result = monitor.get_dataframe()

    assert result == (
        None,
        None,
        None,
        None,
    )