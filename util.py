import logging
import datetime
import time

import params


def configure_logging():
    """
        Initiates and configures the logger for the execution.
    """
    logging.basicConfig(
        filename=params.logfile_path,
        level=logging.INFO,
        format='%(asctime)s;%(message)s'
    )
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


def check_if_any_show_running(todays_schedule):
    """
        Determines the currently ongoing radio show from the provided schedule.

        :param:
            todays_schedule (List of list): A list containing lists, which represent radio shows for the day.
            Each list contains [show name, show start time, show end time].

        Returns:
            Returns a list representing the ongoing radio show if one is found,
            or empty list if no show is currently running.
    """
    current_time = datetime.datetime.now().time()
    for show in todays_schedule:
        show_start_time = datetime.datetime.strptime(show[1], '%H:%M').time()
        show_end_time = datetime.datetime.strptime(show[2], '%H:%M').time()
        if show_start_time <= current_time <= show_end_time:
            return show  # return the show to call recording
    return []


# calculate when the script ends execution: end_time of last show by default
def calculate_end_time(schedule):
    """
        Gets the ending time of the script (usually the ending time of the last show in the daily schedule).

        :param schedule: (List of list):
            A list containing lists, which represent radio shows for the day.
            Each list contains [show name, show start time, show end time].

        Returns:
            Returns the ending time of the last show in the daily schedule,
            or current time if the schedule is empty,
            or None if any error occurs.
    """
    try:
        if not schedule:
            # If the schedule is empty, return the current time
            end_time = datetime.datetime.now().time()
        else:
            # Extract the end time of the last show from the schedule
            last_show_end_time = schedule[-1][2]
            end_time = datetime.datetime.strptime(last_show_end_time, '%H:%M').time()

        logging.info('End time: ' + str(end_time))
        return end_time

    except ValueError as e:
        # Handle the case where there is an issue with the schedule format
        logging.error('Error in schedule format: ' + str(e))
        return None
