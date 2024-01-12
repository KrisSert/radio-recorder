
## Radio-Recorder

Radio-Recorder is a project to record radio shows from a web stream & store the recordings in your Google Drive account.
This enables to listen radio shows after they have been on air (feature commonly behind a paywall for private radio stations)

---

### Architecture:

<img src="https://docs.google.com/drawings/d/e/2PACX-1vRQvB4knx798OI9gv10m-4DAYSghBuSK2fbdf5lkov_F68bHEFGJyXWQruvO7se8Fqz_YDXOsw5k3YT/pub?w=749&amp;h=394">

---

### Installation & dependencies:

All dependencies are included in the venv and described in *requirements.txt*, except:
+ Chromedriver
  + find chromedriver binary here: https://chromedriver.chromium.org/ and place the executable in the project root.
+ Google Chrome
  + find chrome binaries here: https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json and place the library to the project root: *root/chrome-binary/chrome.exe*
+ ffmpeg
  + find ffmpeg here: https://ffmpeg.org/download.html and place the executable in the project root.
+ *../params/credentials.json* storing your Google Drive API credentials.

---

### How to run:

The application is designed to run once daily before any radio shows begin - usually a fixed time around 06:00 AM.
I use cron (running on Google Cloud):
`0 6 * * * python main.py`

Parameters for the run can be specified in params/parameters.py, for example:

`show_keywords = ['My_favourite_show_name_keyword', 'Another_favourite_show_name_keyword']`
*(records shows that contain the keywords)*

`schedule_url = "https://www.aripaev.ee/raadio/otse"` *(url to scrape the radio schedule)*

`stream_url = "https://www.aripaev.ee/raadio/stream.mp3"` *(url for the audio stream)*

---

### Structure:

```
radio-recorder
├───venv
├───main.py
├───util.py
├───src
│   ├───__init__.py
│   ├───gdrive.py
│   ├───maintenance.py
│   ├───recording.py
│   └───schedule.py
├───recordings
├───params
│   ├───__init__.py
│   ├───parameters.py
│   ├───token_path.py
│   ├───token.pickle
│   └───credentials.json
├───logs
│   └───logfile.log
├───tests
├───chromedriver.exe
├───ffmpeg-6.1-full_build
└───chrome-win64
```
