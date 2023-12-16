from __future__ import print_function
import logging
import os.path
import pickle
import time
import requests
from datetime import datetime
from urllib.request import urlopen
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


logging.basicConfig(filename='../logfile.log', level=logging.INFO, format='%(asctime)s;%(message)s')
# to silence the "ModuleNotFoundError: No module named 'oauth2client'" Error
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def upload(path):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../passwords/token.pickle'):
        with open('../passwords/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('passwords/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../passwords/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds,
                    cache_discovery=False)  # cache_discovery=false avoids "ModuleNotFoundError: No module named 'oauth2client'" Error

    # Call the Drive v3 API
    # Iterate over the folders in Google Drive to find "Äripäeva raadio"
    results = service.files().list(fields="nextPageToken, files(id, name)", pageSize=1000).execute()
    items = results.get('files', [])
    if not items:
        logging.info('upload() :: No files/folders existing in Google Drive directory')
    else:
        for item in items:
            # item['name'] is the desired folder name in google drive
            # item['id'] is specific to the distinct folder
            if item['name'] == 'Äripäeva raadio' and item['id'] == '1rtqiz_L-hp1ibL_KGhpgdlL1KF0bRCAx':

                logging.info('syncgoogledrive.upload() :: ' + item['name'] + ' folder found in GoogleDrive')

                # this part breaks out of the function if file with the same name already exists in Gdrive
                results = service.files().list(q="'" + '1rtqiz_L-hp1ibL_KGhpgdlL1KF0bRCAx' + "' in parents",
                                               pageSize=1000,
                                               fields="nextPageToken, files(id, name)").execute()
                files = results.get('files', [])
                for file in files:
                    if file.get('name') == path[11:]:
                        logging.info('syncgoogledrive.upload() :: Denied upload of file: ' + path + ' to GoogleDrive, since file with same name already present')
                        return


                logging.info('syncgoogledrive.upload() :: Starting upload of file: ' + path + ' to GoogleDrive')

                # prepare the new audio file to be uploaded to GoogleDrive
                file_metadata = {'name': path[11:],  # name in Gdrive
                                 'parents': [item['id']]}  # folder_id in Gdrive
                media = MediaFileUpload(path, mimetype='audio/mp3', resumable=True,
                                        chunksize=3000000)  # chunksize = ca. 3 MB

                # upload via insert() chunks
                request = service.files().create(body=file_metadata, media_body=media, fields='id')
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        logging.info("Uploaded %d%%." % int(status.progress() * 100))
                logging.info('upload() :: Upload succeeded')


def main():
    """ Main running function which writes new audio files into recordings/ folder
        & after writing each new file, calls upload() to google drive
    """
    logging.info('_____________________________________________________')
    logging.info("Start of execution:")
    # runs until time has reached limit (last_show_end_time)
    logging.info('script running..')

    # initiate recording of show
    path = 'recordings/test_upload - Copy.mp3'
    # call upload() to upload file to google drive
    logging.info('Starting upload of file: ' + path + ' to GoogleDrive')
    upload(path)


    # maintenance processes. (cleans recordings & logfile)
    # recordings_state = maintanance.clean_recordings('recordings/')
    # maintanance.clean_Drive(recordings_state)
    # maintanance.clean_log()


if __name__ == '__main__':
    main()
