show_keywords = ['investor', 'hommik', 'kinnisvara', 'kuum', 'eetris', 'finants', 'lava', 'top', 'pilk', 'kaupl']

chromedriver_path: str = "chromedriver.exe"

logfile_path: str = 'logs/logfile.log'

# find chrome binaries here: https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads
# .json
chrome_binary_path: str = "chrome-win64/chrome.exe"
schedule_url: str = "https://www.aripaev.ee/raadio/otse"
schedule_xpath: str = '/html/body/div[1]/div/div[1]/div[4]/ul/li[1]/div/ul'
cookies_button: str = "/html/body/div[1]/div/div[1]/div[5]/div/div/ul/li[1]/span/div/span"

stream_url: str = "https://www.aripaev.ee/raadio/stream.mp3"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

DEFAULT_SCHEDULE = [
    ['Hommikuprogramm', '07:00:00', '10:00:00'],
    ['tund_11_12', '11:00:00', '12:00:00'],
    ['tund_12_15', '12:00:00', '15:00:00']
]