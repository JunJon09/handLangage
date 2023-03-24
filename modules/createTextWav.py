import speech_recognition as sr
import datetime

"""
.wavの音声ファイルをテキストに変換する
"""
def changeWav_Text():

    dt_now = datetime.datetime.now()
    currentDay = str(dt_now.year) + "-" + str(dt_now.month).zfill(2) + "-" + str(dt_now.day).zfill(2)
    wavPath = "../data/Wav/NHKNews/" + currentDay + ".wav"

    r = sr.Recognizer()
    with sr.AudioFile(wavPath) as source:
        audio = r.record(source)
    
    text = r.recognize_google(audio, language='ja-JP')
    
    textPath = "../data/TranslateText/NHKNews/" + currentDay + ".txt"

    with open(textPath, mode="w") as f:
        f.write(text)
    f.close()

changeWav_Text()