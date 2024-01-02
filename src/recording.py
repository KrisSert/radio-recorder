import requests
import logging
import time
import os
from datetime import datetime
from pydub import AudioSegment


class Recording:

    def __init__(self, stream_url, show_name, start_time, end_time):
        self.stream_url = stream_url
        self.show_name = show_name
        self.target_path = Recording.construct_target_filepath(show_name)
        today = datetime.now().date()
        self.start_datetime = datetime.combine(today, datetime.strptime(start_time, '%H:%M').time())
        self.end_datetime = datetime.combine(today, datetime.strptime(end_time, '%H:%M').time())

    @staticmethod
    def is_file_nonempty(file_path):
        return os.path.getsize(file_path) != 0

    # create a target name for the recorded show, which includes current date, time and show_name
    @staticmethod
    def construct_target_filepath(show_name):
        current_date = datetime.now().strftime("%d-%m-%Y")
        show_name = f"{current_date}_{show_name}.mp3"
        # Get the directory of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the project root by going up one level (assuming the script is in a subfolder)
        project_root = os.path.abspath(os.path.join(script_directory, '..'))
        # Construct the target file path by joining the project root and the "recordings" folder
        target_filepath = os.path.join(project_root, 'recordings', show_name)
        return target_filepath

    @staticmethod
    def compress(audio_file, target_bitrate=22):
        try:
            # Load audio using pydub
            audio = AudioSegment.from_file(audio_file)
            # Apply compression by setting the target bitrate
            compressed_audio = audio.set_frame_rate(target_bitrate * 1000)
            compressed_audio.export(audio_file, format="mp3")
            logging.info("Compression completed successfully.")
        except Exception as e:
            logging.error(f"Compression failed: {e}")

    def record(self):
        logging.info(f'Starting recording: {self.target_path}')
        try:
            with requests.get(self.stream_url, stream=True) as response, open(self.target_path, 'wb') as f:
                for block in response.iter_content(1024):
                    if datetime.now() > self.end_datetime:
                        break
                    f.write(block)
            logging.info('Recording finalized, closing file')
            # compressing the file if its not empty
            if Recording.is_file_nonempty(self.target_path):
                Recording.compress(self.target_path)
        except requests.RequestException as req_exception:
            logging.error(f'Request failed: {req_exception}')
        except Exception as e:
            logging.error(f'An unexpected error occurred: {e}')
        return self.target_path
