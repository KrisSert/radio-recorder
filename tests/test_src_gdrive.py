import pytest
from unittest.mock import MagicMock

from src.gdrive import GoogleDriveManager


@pytest.fixture
def google_drive_manager():
    # Mocking the necessary methods for testing
    manager = GoogleDriveManager()
    manager.build_drive_service = MagicMock(return_value=None)
    manager.load_credentials = MagicMock(return_value=None)
    return manager


def test_load_credentials(google_drive_manager, mocker):
    # Mocking the refresh_or_obtain_credentials method
    google_drive_manager.refresh_or_obtain_credentials = mocker.MagicMock(return_value=None)

    # Testing load_credentials
    creds = google_drive_manager.load_credentials()

    google_drive_manager.refresh_or_obtain_credentials.assert_called_once_with(None)
    assert creds is None


def test_refresh_or_obtain_credentials(google_drive_manager, mocker):
    creds = MagicMock()
    creds.valid = False
    creds.refresh_token = "refresh_token"
    google_drive_manager.refresh_or_obtain_credentials = mocker.MagicMock(return_value=creds)

    # Testing refresh_or_obtain_credentials with existing credentials
    refreshed_creds = google_drive_manager.refresh_or_obtain_credentials(creds)

    creds.refresh.assert_called_once_with(Request())
    assert refreshed_creds == creds

    # Testing refresh_or_obtain_credentials without existing credentials
    new_creds = google_drive_manager.refresh_or_obtain_credentials(None)

    flow = google_drive_manager.flow
    flow.run_local_server.assert_called_once_with(port=0)
    creds_dumped = pickle.dumps(new_creds)
    with open(params.token_path, 'wb') as token:
        token.write.assert_called_once_with(creds_dumped)
    assert new_creds == creds


def test_build_drive_service(google_drive_manager, mocker):
    google_drive_manager.load_credentials = MagicMock(return_value=None)
    service_mock = MagicMock()
    mocker.patch("googleapiclient.discovery.build", return_value=service_mock)

    # Testing build_drive_service
    service = google_drive_manager.build_drive_service()

    assert service == service_mock
    google_drive_manager.load_credentials.assert_called_once()


def test_find_google_drive_folder(google_drive_manager, mocker):
    folder_name = "Äripäeva raadio"
    mocker.patch("googleapiclient.discovery.build")
    mock_service = google_drive_manager.service
    mock_service.files().list().execute.return_value = {'files': [{'id': '123', 'name': folder_name}]}

    # Testing find_google_drive_folder
    folder = google_drive_manager.find_google_drive_folder(folder_name)

    assert folder is not None
    assert folder['name'] == folder_name


def test_upload(google_drive_manager, mocker):
    path = "test.mp3"
    folder_mock = MagicMock()
    google_drive_manager.find_google_drive_folder = MagicMock(return_value=folder_mock)
    google_drive_manager.upload_file_in_chunks = mocker.MagicMock(return_value="file_id")

    # Testing upload
    google_drive_manager.upload(path)

    google_drive_manager.find_google_drive_folder.assert_called_once_with(params.google_drive_folder)
    google_drive_manager.upload_file_in_chunks.assert_called_once_with(google_drive_manager.service, folder_mock, path)

# Additional tests for other methods can be similarly created.
