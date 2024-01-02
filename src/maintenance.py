# for deleting old recordings
import logging
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Maintenance in local root/recordings, root/logs folders'

class Maintenance:
    def __init__(self, local_path='recordings/'):
        self.local_path = local_path
        self.log_file_path = os.path.join('logs', 'logfile.log')
        self.rec_path_content = None
        self.rec_path_content_post_delete = None

    def clean_recordings(self):
        limit = 5 * 10 ** 9  # 5GB
        self.rec_path_content = []  # [date:"filename"]
        current_path_size = 0

        # calculate path_size and path_content
        for path, dirs, files in os.walk(self.local_path):
            for f in files:
                self.rec_path_content.append([datetime.strptime(f[:10], '%d-%m-%Y'), f])
                fp = os.path.join(self.local_path, f)
                current_path_size += os.path.getsize(fp)

        # find the earliest recording date (date will be stored in smallest_key)
        smallest_key = datetime.today()
        for file in self.rec_path_content:
            if file[0] < smallest_key:
                smallest_key = file[0]

        # if path_size has exceeded the limit, deletes the oldest days recordings
        self.rec_path_content_post_delete = []
        if current_path_size > limit:
            for file in self.rec_path_content:
                if file[0] == smallest_key:
                    logging.info(f"maintenance.clean_recordings() deleting {self.local_path} {file[1]}")
                    os.remove(self.local_path + file[1])
                else:
                    self.rec_path_content_post_delete.append(file)

        else:
            logging.info(f"maintenance.clean_recordings() - plenty of space left in {self.local_path}")
            logging.info(f"Used space: {str(path_size / limit)}%")

    # logfile maintenance. if file size>100mb, cleans half the rows in the file
    def clean_log(self):
        limit = 0.1 * 10 ** 9  # 100Mb

        if os.path.getsize(self.log_file_path) > limit:

            # delete half of rows in the file.
            logging.info(f"Maintenance.clean_log() detected that logfile is too big. "
                         f"starting cleanup of: {self.log_file_path}")

            with open(self.log_file_path) as old:
                lines = old.readlines()
                halfway = int(round(len(lines) / 2))
                with open(self.log_file_path, 'w') as new:
                    new.writelines(lines[halfway:])
            logging.info(f"Maintenance.clean_log() cleanup completed in: {self.log_file_path}")

        else:
            logging.info(f"Maintenance.clean_log() no actions performed")
