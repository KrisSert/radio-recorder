# This is the main script recording & uploading to Google Drive.
# example: to be scheduled on workdays at 06:50 Estonian time; 05:50 Zurich time.

from __future__ import print_function
import logging
import os.path
import pickle
import time
import requests
from datetime import datetime
from urllib.request import urlopen
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import maintanance, gdrive
from params import parameters
from schedule import Schedule
from recording import Recording

logging.basicConfig(filename='logs/logfile.log', level=logging.INFO, format='%(asctime)s;%(message)s')
# to silence the "ModuleNotFoundError: No module named 'oauth2client'" Error
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# If modifying these scopes, delete the file token.pickle.
SCOPES = parameters.SCOPES



# inputs a list of shows
# returns only currently ongoing (1) show.
def determine_show_time(shows):
    for show in shows:
        current_time = datetime.today().time()
        show_start_time = datetime.strptime(show[2], '%H:%M:%S').time()
        show_end_time = datetime.strptime(show[3], '%H:%M:%S').time()
        if show_start_time <= current_time <= show_end_time:
            return show  # return the show to call recording
    return None


# Record the stream and write to mp3 audio file.
def record(destination_path, stream_url, end_time):
    logging.info('Starting recording: ' + destination_path)
    r = requests.get(stream_url, stream=True)
    with open(destination_path, 'wb') as f:
        try:
            for block in r.iter_content(1024):
                f.write(block)
                if datetime.today().time() > end_time:
                    break
        except Exception as e:
            logging.info(e)
    logging.info('Recording finalized, closing file')
    return None


def main():
    """ Main running function which writes new audio files into recordings/ folder
        & after writing each new file, calls upload() to google drive
    """
    logging.info('_____________________________________________________')
    logging.info("Start of execution:")
    todays_schedule = Schedule().get_schedule

    # the next if else should be a separate function: def calculate_end_time()
    if todays_schedule == []:
        break_time = datetime.today().time()
        logging.info('Break time: ' + str(break_time))
    else: 
        last_show_end_time = shows_on_today[-1][3]
        break_time = datetime.strptime(last_show_end_time, '%H:%M:%S').time()
        logging.info('Break time: ' + last_show_end_time)
    
    logging.info('shows_on_today:' + str(shows_on_today))

    # runs until time has reached limit (last_show_end_time)
    while datetime.today().time() <= break_time:  # HERE THERE IS AN ISSUE IN VM!!
        logging.info('script running..')
        while determine_show_time(shows_on_today) is None and datetime.today().time() <= break_time:
            time.sleep(1)
        if datetime.today().time() <= break_time:
            # initiate recording of show
            ongoing_show = determine_show_time(shows_on_today)
            path = 'recordings/' + datetime.now().strftime("%d-%m-%Y_") + ongoing_show[0] + '.mp3'
            record(path, parameters.stream_url, datetime.strptime(ongoing_show[3], '%H:%M:%S').time())
            # call upload() to upload file to google drive
            logging.info('Starting upload of file: ' + path + ' to GoogleDrive')
            gdrive.upload(path)
        else:
            logging.info('Break_time met.. Closing script')
            break

    # maintenance processes. (cleans recordings & logfile)
    recordings_state = maintanance.clean_recordings('recordings/')
    gdrive.clean_gdrive(recordings_state)
    maintanance.clean_log()


if __name__ == '__main__':
    main()
