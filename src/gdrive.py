import logging
import pickle
import os
from datetime import datetime
from urllib.request import urlopen

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import params


class GoogleDriveManager:
    def __init__(self):
        self.service = self.build_drive_service()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.credentials_path = os.path.join(self.script_dir, '..', 'params', 'credentials.json')

    def load_credentials(self):
        """Load credentials from the token file or initiate the OAuth flow if needed.
            :return: credentials
        """
        creds = None

        if os.path.exists(params.token_path):
            with open(params.token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            creds = self.refresh_or_obtain_credentials(creds)

        return creds


    def refresh_or_obtain_credentials(self, creds):
        """Refresh or obtain new credentials using the OAuth flow."""
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, params.SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(params.token_path, 'wb') as token:
            pickle.dump(creds, token)

        return creds


    def build_drive_service(self):
        """Build and return the Google Drive service."""
        creds = self.load_credentials()
        service = build('drive', 'v3', credentials=creds, cache_discovery=False)
        return service


    def upload_file_in_chunks(self, service, folder, local_file_path, chunksize=3 * 1024 * 1024):
        folder_name = folder['name']
        folder_id = folder['id']

        logging.info(f'gdrive.upload_file_in_chunks() :: {folder_name} folder found in Google Drive')
        logging.info(f'gdrive.upload_file_in_chunks() :: Starting upload of file: {local_file_path} to Google Drive')

        # Prepare metadata for the file
        file_metadata = {
            'name': os.path.basename(local_file_path),  # Name in Google Drive
            'parents': [folder_id]  # Folder ID in Google Drive
        }

        # Create a MediaFileUpload object with the specified chunksize
        media = MediaFileUpload(local_file_path, mimetype='audio/mp3', resumable=True, chunksize=chunksize)

        # Create the file in Google Drive and upload chunks
        request = service.files().create(body=file_metadata, media_body=media, fields='id')
        response = None

        while response is None:
            status, response = request.next_chunk()
            if status:
                logging.info(f"Uploaded {int(status.progress() * 100)}%")

        logging.info('gdrive.upload_file_in_chunks() :: Upload succeeded')
        return response.get('id')


    def find_google_drive_folder(self, folder_name):
        """Find a folder in Google Drive based on the given name."""
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"

        # Execute the API call
        results = self.service.files().list(q=query).execute()

        # Extract the first folder, if any
        folders = results.get('files', [])
        return folders[0] if folders else None


    def upload(self, path):
        '''
        Call the Google Drive API
           - find target folder in Google Drive
           - upload the file
        '''
        folder = self.find_google_drive_folder(params.google_drive_folder)

        if folder:
            # Upload the file once the folder has been found
            file_id = self.upload_file_in_chunks(self.service, folder, path)
        else:
            # Folder not found
            logging.info(f"No folder with the name '{params.google_drive_folder}' found.")


    # same logic as maintenance.clean_recordings(), except running in Google Drive folder.
    def clean_gdrive(self, recordings_state):
        drive_folder_name = 'Äripäeva raadio'
        drive_folder_id = '1rtqiz_L-hp1ibL_KGhpgdlL1KF0bRCAx'

        # Iterate over the folders in Google Drive to find "Äripäeva raadio"
        drive_folder = self.find_drive_folder(drive_folder_name, drive_folder_id)

        if drive_folder:

            # compare local recordings vs google drive recordings:
            local_recordings = [rec[1] for rec in recordings_state]
            drive_recordings = self.get_drive_files_in_folder(drive_folder_id)

            files_to_delete = self.find_files_to_delete(drive_recordings, local_recordings)

            for filename in files_to_delete:
                file_id = self.get_file_id_by_name(drive_recordings, filename)
                self.delete_file(file_id)
                logging.info(f'clean_Drive() :: Deleting file {filename} in GoogleDrive, id: {file_id}')
        else:
            logging.info('upload() :: No files/folders existing in Google Drive directory')


    def find_drive_folder(self, folder_name, folder_id):
        results = self.service.files().list(fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        # item['name'] is the desired folder name in google drive
        # item['id'] is specific to the distinct folder
        for item in items:
            if item['name'] == folder_name and item['id'] == folder_id:
                logging.info(
                    f'clean_Drive() :: Syncing "recordings" between local & Google Drive/{folder_name}')
                return item

        return None


    def get_drive_files_in_folder(self, folder_id):
        results = self.service.files().list(q=f"'{folder_id}' in parents", pageSize=10,
                                            fields="nextPageToken, files(id, name)").execute()
        return results.get('files', [])


    def find_files_to_delete(self, drive_recordings, local_recordings):
        return [filename for filename in drive_recordings if filename not in local_recordings]


    def get_file_id_by_name(self, drive_recordings, filename):
        for file in drive_recordings:
            if file.get('name') == filename:
                return file.get('id')
        return None


    def delete_file(self, file_id):
        self.service.files().delete(fileId=file_id).execute()
