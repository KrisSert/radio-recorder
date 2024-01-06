# tests/test_main.py
import datetime
import logging
from unittest.mock import patch

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import main


def test_main_with_schedule(tmpdir):
    # Mock the Schedule class to return a predefined schedule for testing
    with patch('src.main.Schedule') as mock_schedule:
        mock_schedule.return_value.get_schedule.return_value = [
            ['Show1', '10:00', '11:00'],
            ['Show2', '12:00', '13:00']
            # Add more shows if needed
        ]

        # Mock datetime to simulate time passing during the main function execution
        with patch('src.main.datetime.datetime.now') as mock_now:
            mock_now.side_effect = [
                datetime.datetime(2023, 1, 1, 10, 0),  # Start time
                datetime.datetime(2023, 1, 1, 11, 30),  # Ongoing show
                datetime.datetime(2023, 1, 1, 12, 30),  # End time

                # Add more datetime objects as needed
            ]

            # Call the main function
            main()

    # Add assertions based on the expected behavior of your main function
    # For example, check if recordings are created, uploaded, and maintenance is performed


def test_main_no_schedule():
    # Test the scenario where there are no shows in the schedule
    with patch('src.main.Schedule') as mock_schedule:
        mock_schedule.return_value.get_schedule.return_value = []

        # Call the main function
        main()

    # Add assertions based on the expected behavior when there are no shows in the schedule
