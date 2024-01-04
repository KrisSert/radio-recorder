#import imageio_ffmpeg as ffmpeg
from pydub import AudioSegment

audio_file = "test.mp3"
audio = AudioSegment.from_file(audio_file)
print("Success")

#print(ffmpeg.get_ffmpeg_version())
