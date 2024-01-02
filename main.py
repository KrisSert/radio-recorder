# Daily runs to be scheduled on workdays at 06:50 before any radio shows start.
import datetime
import logging
import os.path
import time

import params
import util
from src import maintanance
from src.gdrive import GoogleDriveManager
from src.recording import Recording
from src.schedule import Schedule
from src.maintenance import Maintenance


def main():
    """ Main logic:
        - reads the daily radio schedule.
        - records the radio shows defined in the schedule into mp3 locally
        - uploads the recorded radio shows to google drive.
        - runs data cleanup: locally, on Google Drive, on logfile.
    """

    # initiate logging
    util.configure_logging()
    logging.info('_____________________________________________________')
    logging.info("Start of execution:")

    # get today's radio schedule
    today_schedule = Schedule().get_schedule
    logging.info('shows_on_today:' + str(today_schedule))

    # go here if there is something to record today:
    if todays_schedule:

        current_time = datetime.datetime.now().time()
        today_end_time = util.calculate_end_time(today_schedule)
        # if schedule is empty: today_end_time is current_time

        logging.info('script running..')
        # runs until time has reached limit (last_show_end_time)
        while current_time <= today_end_time:

            ongoing_show = util.check_if_any_show_running(today_schedule)
            if ongoing_show:
                # initiate recording of show
                new_recording = Recording(stream_url=params.stream_url,
                                          show_name=ongoing_show[0],
                                          start_time=ongoing_show[1],
                                          end_time=ongoing_show[2]
                                          )
                recording_file_path = new_recording.record()

                #  upload file to google drive
                new_gdrive_manager = GoogleDriveManager()
                new_gdrive_manager.upload(recording_file_path)

            time.sleep(1)
            current_time = datetime.datetime.now().time()

        logging.info('End time met.. ending process')

        # maintenance processes. (cleans recordings folder & logfile, if too large)
        new_local_maintenance = Maintenance()
        new_local_maintenance.clean_recordings('recordings/')
        new_local_maintenance.clean_log()

        # clean files in Google Drive target folder, if execution has also deleted locally
        if new_local_maintenance.rec_path_content_post_delete:
            new_gdrive_manager = GoogleDriveManager()
            new_gdrive_manager.clean_gdrive(new_local_maintenance.rec_path_content_post_delete)

    else:
        logging.info('there are no shows to record today, ending process...')


if __name__ == '__main__':
    main()

    # TODO: create venv and regenerate the requirements.txt
    # Create tests
