

import requests
from passwords import parameters

stream_url = 'http://your-stream-source.com/stream'

r = requests.get(parameters.stream_url, stream=True)

with open('stream.mp3', 'wb') as f:
    try:
        for block in r.iter_content(1024):
            f.write(block)
    except Exception as e:
        # log the error e