import ffmpeg
import datetime

"""
.mp4の動画から.wavの音声だけを抜き取る
"""
def changeMp4_Wav():
    dt_now = datetime.datetime.now()
    currentDay = str(dt_now.year) + "-" + str(dt_now.month).zfill(2) + "-" + str(dt_now.day).zfill(2)

    moviePath = "../data/Movie/NHKNews/" + currentDay + ".mp4"
    stream = ffmpeg.input(moviePath)

    wavPath = "../data/Wav/NHKNews/" + currentDay + ".wav"
    stream = ffmpeg.output(stream, wavPath)
    ffmpeg.run(stream)
changeMp4_Wav()
