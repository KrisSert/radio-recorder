import logging
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from params import parameters
import requests
from datetime import datetime
from urllib.request import urlopen
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload(path):
    logging.info('Starting upload of file: ' + path + ' to GoogleDrive')
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../params/token.pickle'):
        with open('../params/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('../params/credentials.json', parameters.SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../params/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds,
                    cache_discovery=False)  # cache_discovery=false avoids "ModuleNotFoundError: No module named 'oauth2client'" Error

    # Call the Drive v3 API
    # Iterate over the folders in Google Drive to find "Äripäeva raadio"
    results = service.files().list(fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        logging.info('upload() :: No files/folders existing in Google Drive directory')
    else:
        for item in items:
            # item['name'] is the desired folder name in google drive
            # item['id'] is specific to the distinct folder
            if item['name'] == 'Äripäeva raadio' and item['id'] == '1rtqiz_L-hp1ibL_KGhpgdlL1KF0bRCAx':
                logging.info('syncgoogledrive.upload() :: ' + item['name'] + ' folder found in GoogleDrive')

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


# same algorithm as clean_recordings(), except running in Google Drive folder.
def clean_gdrive(recordings_state):
    creds = None
    if os.path.exists('../params/token.pickle'):
        with open('../params/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('../params/credentials.json', parameters.SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../params/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds,
                    cache_discovery=False)  # cache_discovery=false avoids "ModuleNotFoundError: No module named 'oauth2client'" Error

    # Call the Drive v3 API
    # Iterate over the folders in Google Drive to find "Äripäeva raadio"
    results = service.files().list(fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        logging.info('upload() :: No files/folders existing in Google Drive directory')
    else:
        for item in items:
            # item['name'] is the desired folder name in google drive
            # item['id'] is specific to the distinct folder
            if item['name'] == 'Äripäeva raadio' and item['id'] == '1rtqiz_L-hp1ibL_KGhpgdlL1KF0bRCAx':
                logging.info('maintenance.clean_Drive() :: '
                             + 'syncing "recordings" between local & Google_Drive/'
                             + item['name'])

                # clean the local recordings list by creating list of files.
                local_rec = []
                for rec in recordings_state:
                    local_rec.append(rec[1])

                # create list of files in Google drive folder
                g_drive_rec = []
                results = service.files().list(q="'" + '1rtqiz_L-hp1ibL_KGhpgdlL1KF0bRCAx' + "' in parents",
                                               pageSize=10,
                                               fields="nextPageToken, files(id, name)").execute()
                files = results.get('files', [])
                for file in files:
                    g_drive_rec.append(file.get('name'))

                # find the tracks to delete from Google Drive, by subtracting: g_drive_rec-local_rec
                files_to_delete = [x for x in g_drive_rec if x not in local_rec]

                for el in files_to_delete:
                    # delete based on file id
                    for file in files:
                        if file.get('name') == el:
                            logging.info('maintenance.clean_Drive() :: '
                                         + 'deleting file ' + file.get('name') + 'in GoogleDrive, '
                                         + 'id: ' + file.get('id'))
                            service.files().delete(fileId=file.get('id')).execute()
