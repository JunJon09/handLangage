import MeCab
import datetime
"""
音声をテキスト化したものを品詞分類を行う
"""
def setClassification():
    wakati = MeCab.Tagger("-Owakati")
    dt_now = datetime.datetime.now()
    currentDay = str(dt_now.year) + "-" + str(dt_now.month).zfill(2) + "-" + str(dt_now.day).zfill(2)
    TranslateText = "../data/TranslateText/NHKNews/" + currentDay + ".txt"
    with open(TranslateText) as f:
        text = f.read()
    f.close()
    print(wakati.parse(text))
setClassification()