import datetime
import logging
import sys
import os

import pytest
from unittest.mock import patch, MagicMock

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import util


@pytest.fixture
def mock_schedule():
    return [['Show1', '10:00', '11:00'], ['Show2', '12:00', '13:00'], ['Show3', '14:00', '15:00']]


def test_configure_logging(tmpdir):
    logfile_path = tmpdir.join("logfile.log")

    with patch('util.logging.basicConfig') as mock_basic_config, \
         patch('util.logging.getLogger') as mock_get_logger:

        configure_logging()

    mock_basic_config.assert_called_once_with(
        filename=str(logfile_path),
        level=logging.INFO,
        format='%(asctime)s;%(message)s'
    )

    mock_get_logger.assert_called_once_with('googleapiclient.discovery_cache')
    mock_get_logger.return_value.setLevel.assert_called_once_with(logging.ERROR)


def test_check_if_any_show_running(mock_schedule):
    # Test when a show is currently running
    current_time = datetime.datetime.strptime('11:30', '%H:%M').time()
    with patch('util.datetime.datetime.now', return_value=datetime.datetime(2023, 1, 1, 11, 30)):
        result = check_if_any_show_running(mock_schedule)
    assert result == ['Show1', '10:00', '11:00']

    # Test when no show is currently running
    with patch('util.datetime.datetime') as mock_datetime:
        mock_datetime.now.side_effect = [
            datetime.datetime(2023, 1, 1, 16, 0),
            datetime.datetime(2023, 1, 1, 16, 0)  # You can add more if needed
        ]
        result = check_if_any_show_running(mock_schedule)

    assert result == []


def test_calculate_end_time_empty_schedule():
    with patch('util.datetime.datetime.now', return_value=datetime.datetime(2023, 1, 1, 16, 0)):
        result = calculate_end_time([])
    assert result == datetime.datetime(2023, 1, 1, 16, 0).time()


def test_calculate_end_time_non_empty_schedule(mock_schedule):
    with patch('util.datetime.datetime.now', return_value=datetime.datetime(2023, 1, 1, 16, 0)):
        result = calculate_end_time(mock_schedule)
    assert result == datetime.datetime.strptime('15:00', '%H:%M').time()


def test_calculate_end_time_error_in_schedule_format():
    with patch('util.datetime.datetime.now', return_value=datetime.datetime(2023, 1, 1, 16, 0)):
        with patch('util.logging.error') as mock_logging_error:
            result = calculate_end_time([['InvalidFormat']])
    assert result is None
    mock_logging_error.assert_called_once_with(
        'Error in schedule format: time data \'InvalidFormat\' does not match format \'%H:%M\'')
