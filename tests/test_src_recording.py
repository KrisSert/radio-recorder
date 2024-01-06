import os
from datetime import datetime, timedelta

import pytest
from unittest.mock import MagicMock, mock_open

from src.recording import Recording


@pytest.fixture
def recording_instance():
    stream_url = "https://example.com/stream"
    show_name = "TestShow"
    start_time = "12:00"
    end_time = "13:00"
    return Recording(stream_url, show_name, start_time, end_time)


def test_construct_target_filepath(recording_instance):
    target_filepath = recording_instance.construct_target_filepath("TestShow")
    assert target_filepath.endswith("recordings/TestShow.mp3")


def test_is_file_nonempty_nonexistent_file(recording_instance, tmpdir):
    non_existent_file = tmpdir.join("non_existent_file.mp3")
    assert not recording_instance.is_file_nonempty(str(non_existent_file))


def test_is_file_nonempty_empty_file(recording_instance, tmpdir):
    empty_file = tmpdir.join("empty_file.mp3")
    empty_file.write('')
    assert not recording_instance.is_file_nonempty(str(empty_file))


def test_is_file_nonempty_nonempty_file(recording_instance, tmpdir):
    non_empty_file = tmpdir.join("non_empty_file.mp3")
    non_empty_file.write('data')
    assert recording_instance.is_file_nonempty(str(non_empty_file))


def test_compress_successful(recording_instance, mocker, caplog, tmpdir):
    audio_file = tmpdir.join("audio_file.mp3")
    audio_file.write('data')
    mocker.patch('pydub.AudioSegment.from_file', return_value=MagicMock())
    mocker.patch('pydub.AudioSegment.export', return_value=None)

    recording_instance.compress(str(audio_file))

    assert "Compression completed successfully." in caplog.text


def test_compress_failure(recording_instance, mocker, caplog, tmpdir):
    audio_file = tmpdir.join("audio_file.mp3")
    audio_file.write('data')
    mocker.patch('pydub.AudioSegment.from_file', side_effect=Exception("Mocked error"))

    recording_instance.compress(str(audio_file))

    assert "Compression failed" in caplog.text


def test_record_successful(recording_instance, mocker, tmpdir):
    mocker.patch('requests.get', return_value=MagicMock(iter_content=lambda _: b'data'))
    mocker.patch('builtins.open', mock_open())

    target_path = recording_instance.record()

    assert os.path.isfile(target_path)
    assert "Recording finalized" in caplog.text


def test_record_request_failure(recording_instance, mocker, caplog):
    mocker.patch('requests.get', side_effect=requests.RequestException("Mocked request exception"))

    target_path = recording_instance.record()

    assert not os.path.isfile(target_path)
    assert "Request failed" in caplog.text


def test_record_unexpected_error(recording_instance, mocker, caplog):
    mocker.patch('requests.get', side_effect=Exception("Mocked unexpected error"))

    target_path = recording_instance.record()

    assert not os.path.isfile(target_path)
    assert "An unexpected error occurred" in caplog.text
