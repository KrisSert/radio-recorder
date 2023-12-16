## for deleting old recordings
import logging
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Maintenance in local folders
def clean_recordings(path):
    limit = 5 * 10 ** 9  # 5GB
    path_content = []  # [date:"filename"]
    path_size = 0

    # calculate path_size and path_content
    for path, dirs, files in os.walk(path):
        for f in files:
            path_content.append([datetime.strptime(f[:10], '%d-%m-%Y'), f])
            fp = os.path.join(path, f)
            path_size += os.path.getsize(fp)

    # find the earliest recording date (date will be stored in smallest_key)
    smallest_key = datetime.today()
    for file in path_content:
        if file[0] < smallest_key:
            smallest_key = file[0]

    # if path_size has exceeded the limit, deletes the oldest days recordings
    post_delete = []
    if path_size > limit:
        for file in path_content:
            if file[0] == smallest_key:
                logging.info('maintenance.clean_recordings() deleting ' + path + file[1])
                os.remove(path + file[1])
            else:
                post_delete.append(file)
        return post_delete

    else:
        logging.info('maintenance.clean_recordings() - plenty of space left in ' + path)
        logging.info('Used space: ' + str(path_size / limit) + '%')
        return path_content


## logfile maint. if filesize>100mb, cleans half the rows in the file
def clean_log():
    limit = 0.1 * 10 ** 9  # 100Mb
    if os.path.getsize('logfile.log') > limit:
        #delete half of rows in the file.
        with open('logfile.log') as old:
            lines = old.readlines()
            halfway = int(round(len(lines)/2))
            with open('logfile.log', 'w') as new:
                new.writelines(lines[halfway:])
    return
