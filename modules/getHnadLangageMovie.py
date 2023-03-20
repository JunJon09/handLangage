import datetime
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service #driver.getの時の警告回避
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import traceback
from time import sleep
import os
import subprocess
from selenium.webdriver.chrome.options import Options


#NHK動画を取得する。
def scrapingMovie():
    """
    https://www.nhk.or.jp/shuwa から毎日ショートニュースデータを取得する。
    """
    url = "https://www.nhk.or.jp/shuwa/sp/index.html"
    chromDriverPath = "../chromdriver"
    dt_now = datetime.datetime.now()
    currentDay = str(dt_now.year) + "-" + str(dt_now.month).zfill(2) + "-" + str(dt_now.day).zfill(2)

    try:
        driver = openChrom(chromDriverPath, url)
        path = getNHKNewsPath(driver)
        cmd = changePath(path, currentDay)
        driver.quit()
        getNHKNewMovie(cmd)

    except Exception as e:
        print(traceback.print_exc())
        print("失敗したので終了")

#Chromeの立ち上げ
def openChrom(chromDriverPath, url):
    service = Service(executable_path=chromDriverPath) #driver.getの警告回避
    options = Options()
    # ヘッドレスモードで実行する場合
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "mnbox")))

    return driver

#動画のパスを取得
def getNHKNewsPath(driver):
    setClassElements = driver.find_elements(By.CLASS_NAME, "mnbox")

    for i, elements in enumerate(setClassElements): #日が短いショートニュースを取得
        if elements.text.find("ショートニュース") != -1:
            getClassNumber = i
            break
        
    setClassElements[getClassNumber].click() #clickしてshuwaplayerを表示させる
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "shuwaplayer")))
    sleep(1) #念の為
    setClassElements = driver.find_element(By.CLASS_NAME, "shuwaplayer")

    path = setClassElements.get_attribute("src")
    
    return path

#動画のパスを変更してダウンロードできる形にする
def changePath(path, day):
    """https://www.nhk.or.jp/shuwa/mov/230317/230317_n41arp.html?movie=trueのパスを
    https://vod-stream.nhk.jp/shuwa/mov/230317/230317_n41arp/index.m3u8に変更して.shに入れる
    """
    temp = path.split('shuwa')
    movieName = temp[1].split(".html?")

    cmd = "echo n | ffmpeg -i  https://vod-stream.nhk.jp/shuwa" + movieName[0] + "/index.m3u8 -c copy -bsf:a aac_adtstoasc " + "'../data/Movie/NHKNews/" + day + ".mp4'\n"
    
    return cmd
    

def getNHKNewMovie(cmd):
    with open("./movie.sh", mode='w') as f:
        f.write(cmd)
    
    subprocess.run("chmod 777 ./movie.sh", shell = True)
    subprocess.run('./movie.sh', shell = True)

    os.remove("./movie.sh")
