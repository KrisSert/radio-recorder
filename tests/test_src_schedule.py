import pytest
from unittest.mock import MagicMock, patch
from src.schedule import Schedule


@pytest.fixture
def schedule_instance():
    return Schedule()


def test_get_chrome_options(schedule_instance):
    chrome_options = schedule_instance.get_chrome_options()
    assert "--headless" in chrome_options.arguments
    assert chrome_options.binary_location == "your/chrome/binary/path"


def test_create_tuples_of_two_odd_length(schedule_instance):
    input_list = [1, 2, 3, 4, 5]
    result = schedule_instance.create_tuples_of_two(input_list)
    assert result == [(1, 2), (3, 4)]


def test_create_tuples_of_two_even_length(schedule_instance):
    input_list = [1, 2, 3, 4, 5, 6]
    result = schedule_instance.create_tuples_of_two(input_list)
    assert result == [(1, 2), (3, 4), (5, 6)]


def test_get_schedule_with_cookies(schedule_instance, mocker):
    mocker.patch('selenium.webdriver.Chrome')
    mock_driver = MagicMock()
    mocker.patch.object(mock_driver, 'find_element', side_effect=[MagicMock(), MagicMock()])
    mocker.patch.object(mock_driver, 'quit', return_value=None)

    with patch('your_module.driver', mock_driver):
        result = schedule_instance.get_schedule()

    assert result == schedule_instance.schedule_data


def test_get_schedule_no_cookies(schedule_instance, mocker):
    mocker.patch('selenium.webdriver.Chrome')
    mock_driver = MagicMock()
    mocker.patch.object(mock_driver, 'find_element',
                        side_effect=NoSuchElementException("Mocked NoSuchElementException"))
    mocker.patch.object(mock_driver, 'quit', return_value=None)

    with patch('your_module.driver', mock_driver):
        result = schedule_instance.get_schedule()

    assert result == [('Default Show', '00:00', '23:59')]


def test_get_schedule_exception(schedule_instance, mocker):
    mocker.patch('selenium.webdriver.Chrome')
    mock_driver = MagicMock()
    mocker.patch.object(mock_driver, 'find_element', side_effect=Exception("Mocked unexpected error"))
    mocker.patch.object(mock_driver, 'quit', return_value=None)

    with patch('your_module.driver', mock_driver):
        result = schedule_instance.get_schedule()

    assert result == [('Default Show', '00:00', '23:59')]
