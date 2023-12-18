# This is the main script.
# Daily runs to be scheduled on workdays at 06:50 before any radio shows start.

import datetime
import logging
import os.path
import time

from params import parameters
from src import maintanance, gdrive
from src.recording import Recording
from src.schedule import Schedule


def configure_logging():
    """
        Initiates and configures the logger for the execution.
    """
    logging.basicConfig(
        filename=parameters.logfile_path,
        level=logging.INFO,
        format='%(asctime)s;%(message)s'
    )
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


def check_if_any_show_running(todays_schedule):
    """
        Determines the currently ongoing radio show from the provided schedule.

        Parameters:
            todays_schedule (List of list): A list containing lists, which represent radio shows for the day.
            Each list contains [show name, show start time, show end time].

        Returns:
            Returns a list representing the ongoing radio show if one is found,
            or empty list if no show is currently running.
    """
    current_time = datetime.datetime.now().time()
    for show in todays_schedule:
        show_start_time = datetime.datetime.strptime(show[1], '%H:%M:%S').time()
        show_end_time = datetime.datetime.strptime(show[2], '%H:%M:%S').time()
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
            end_time = datetime.datetime.strptime(last_show_end_time, '%H:%M:%S').time()

        logging.info('End time: ' + str(end_time))
        return end_time

    except ValueError as e:
        # Handle the case where there is an issue with the schedule format
        logging.error('Error in schedule format: ' + str(e))
        return None


def main():
    """ Main logic:
        - reads the daily radio schedule.
        - records the radio shows defined in the schedule into mp3 locally
        - uploads the recorded radio shows to google drive.
        - runs data cleanup: locally, on Google Drive, on logfile.
    """

    # initiate logging
    configure_logging()
    logging.info('_____________________________________________________')
    logging.info("Start of execution:")

    todays_schedule = Schedule().get_schedule
    logging.info('shows_on_today:' + str(todays_schedule))

    if todays_schedule:

        current_time = datetime.datetime.now().time()
        today_end_time = calculate_end_time(todays_schedule)
        # if schedule is empty: today_end_time is current_time

        # runs until time has reached limit (last_show_end_time)
        while current_time <= today_end_time:
            logging.info('script running..')

            ongoing_show = check_if_any_show_running(todays_schedule)
            if ongoing_show:
                # initiate recording of show
                new_recording = Recording(stream_url=parameters.stream_url,
                                          show_name=ongoing_show[0],
                                          start_time=ongoing_show[1],
                                          end_time=ongoing_show[2]
                                          )
                new_recording.record()
                # call upload() to upload file to google drive
                gdrive.upload(new_recording.target_path)

            time.sleep(1)
            current_time = datetime.datetime.now().time()

        logging.info('End time met.. ending process')

        # maintenance processes. (cleans recordings & logfile)
        recordings_state = maintanance.clean_recordings('recordings/')
        gdrive.clean_gdrive(recordings_state)
        maintanance.clean_log()

    else:

        logging.info('there are no shows to record today, ending process...')


if __name__ == '__main__':
    main()
