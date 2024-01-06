import os
from datetime import datetime

import pytest
from unittest.mock import MagicMock, mock_open

from src.maintenance import Maintenance


@pytest.fixture
def maintenance_instance():
    return Maintenance(local_path='recordings/')


def test_clean_recordings_space_left(maintenance_instance, mocker):
    mocker.patch('os.walk', return_value=[('/recordings', [], ['file1.mp3', 'file2.mp3'])])
    mocker.patch('os.path.getsize', return_value=4 * 10 ** 9)  # Mocking 4GB space used

    maintenance_instance.clean_recordings()

    assert maintenance_instance.rec_path_content_post_delete is None
    assert "plenty of space left" in caplog.text


def test_clean_recordings_space_exceeded(maintenance_instance, mocker, caplog):
    mocker.patch('os.walk', return_value=[('/recordings', [], ['file1.mp3', 'file2.mp3'])])
    mocker.patch('os.path.getsize', return_value=6 * 10 ** 9)  # Mocking 6GB space used
    mocker.patch('os.remove', return_value=None)

    maintenance_instance.clean_recordings()

    assert maintenance_instance.rec_path_content_post_delete is not None
    assert "clean_recordings() deleting" in caplog.text


def test_clean_log_no_cleanup_needed(maintenance_instance, mocker, caplog):
    mocker.patch('os.path.getsize', return_value=0.05 * 10 ** 9)  # Mocking 50MB log file size

    maintenance_instance.clean_log()

    assert "clean_log() no actions performed" in caplog.text


def test_clean_log_cleanup_needed(maintenance_instance, mocker, caplog):
    mocker.patch('os.path.getsize', return_value=0.2 * 10 ** 9)  # Mocking 200MB log file size
    mocker.patch('builtins.open', mock_open(read_data="line1\nline2\nline3\nline4\nline5\n"))

    maintenance_instance.clean_log()

    assert "clean_log() detected that logfile is too big" in caplog.text
    assert "clean_log() cleanup completed" in caplog.text
