from datetime import datetime


show_keywords = ['investor', 'hommik', 'kinnisvara', 'kuum', 'eetris', 'finants', 'lava', 'top', 'pilk', 'kaupl']

chromedriver_path: str = "chromedriver.exe"

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
    ['Hommikuprogramm', [datetime.today().weekday()], '07:00:00', '10:00:00'],
    ['tund_11_12', [datetime.today().weekday()], '11:00:00', '12:00:00'],
    ['tund_12_15', [datetime.today().weekday()], '12:00:00', '15:00:00']
]

# this is an example schedule list which get_schedule() returns

# show_name, airtime_weekdays, hour_start, end_time
'''shows_ = [
    ["TEST_1", [datetime.today().weekday()], datetime.now().strftime("%H:%M:%S"),
     (datetime.now() + timedelta(seconds=10)).strftime("%H:%M:%S")],
    ["TEST_2", [datetime.today().weekday()], (datetime.now() + timedelta(seconds=15)).strftime("%H:%M:%S"),
     (datetime.now() + timedelta(seconds=25)).strftime("%H:%M:%S")],
    # ["Hommikuprogramm", [0, 1, 2, 3, 4], '07:00:00.0000', '10:00:00.0000'],
    # ["Äripäev eetris", [0], '11:00:00.0000', '12:00:00.0000'],
    # ["Lavajutud", [0], '16:00:00.0000', '17:00:00.0000']
    ["Investor Toomase tund", [1], '16:00:00', '17:00:00']
    # ["Kõik ärikinnisvarast", [1], '12:00:00.0000', '13:00:00.0000'],
    # ["Finantsuudised fookuses", [2], '12:00:00.0000', '13:00:00.0000'],
    # ["Uus Maa kinnisvarasaade", [4], '13:00:00.0000', '14:00:00.0000'],
    # ["Kuum tool", [4], '11:00:00.0000', '12:00:00.0000']
    # ["Kinnisvarainvestori ABC", ]
]'''
