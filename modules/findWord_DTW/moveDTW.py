import numpy as np
import matplotlib.pyplot as plt
from fastdtw import fastdtw
import pickle
from sklearn.model_selection import train_test_split
import math
from statistics import variance 

def moveDTW():
    word = "Japan"
    left, right, body = getData(word) #データ取得
    #データを訓練データとテストデータに分割
    train_left, test_left = split_data(left)
    train_right, test_right = split_data(right)
    train_body, test_body = split_data(body)
    learning(train_left, test_left, train_right, test_right, train_body, test_body)
    
#Listデータを取得して一括でまとめる
def getData(word):
    Path = "./DTWList/"
    left = []
    right = []
    body = []
    for i in range(30):
        absolutePath = Path + word + str(i)
        leftPath = absolutePath+ "_left.bin"
        rightPath = absolutePath + "_right.bin"
        bodyPath = absolutePath + "_body.bin"
        try:
            with open(leftPath, "rb") as p:
                l = pickle.load(p)
            left.append(l)
            with open(rightPath, "rb") as p:
                l = pickle.load(p)
            right.append(l)
            with open(bodyPath, "rb") as p:
                l = pickle.load(p)
            body.append(l)
        except Exception as e:
            continue

    
    return left, right, body

#訓練データとテストデータで分割する
def split_data(data):
    train_data, test_data = train_test_split(data, test_size=1, random_state=42)
    return train_data, test_data

#DTWを実行
"""
リストの配列構造
train_dataは、三次元配列で一番中には時系列の座標[x, y, z] それが薬指とか親指とかがあるの個数、それの時系列、最後にそのデータの個数
dataは[[[x, y, z],....]], [[x, y, z]....]]]
"""

def learning(train_left, test_left, train_right, test_right, train_body, test_body):
    left_distance, left_dispersion = getDistance(test_left, train_left)
    right_distance, right_dispersion = getDistance(train_right, test_right)
    body_distance, body_dispersion = getDistance(train_body, test_body)
    distanceList = []

    for i in range(len(left_distance)): 
        distance = left_distance[i] + right_distance[i] + body_distance[i]
        distance = math.sqrt(distance)
        distanceList.append(distance)
   
    #分散
    dispersionList = left_dispersion + right_dispersion + body_dispersion

    return sum(distanceList) / len(distanceList), variance(dispersionList)
    
#DTWを使用してテストデータと訓練データの距離を取得する
def getDistance(test, train):
    distanceList = []
    distanceDispersionList = [] #分散のために使用
    for te in test:
        data1_left = setData(te, len(train[0][0]))
        for tr in train:
            data2_left = setData(tr, len(train[0][0]))
            distance_sum_1 = 0
            distance_sum_2 = 0
            for d_1, d_2 in zip(data1_left, data2_left):
                distance, path = fastdtw(d_1, d_2)
                distance_sum_1 += distance
                distance_sum_2 += (distance**2)
            distanceDispersionList.append(distance_sum_1)
            distanceList.append(distance_sum_2)
    return distanceList, distanceDispersionList

#データをnumpyに変換して例として手の親指の付け根のx座標を時系列順にする。(他のも同様)
def setData(data, data_len):
   dataSet = []
   data = np.array(data)
   for i in range(data_len):
        for j in range(2):
            tmp = data[:, i, j]
            dataSet.append(tmp)
   return dataSet

#エラーが起きた時に使用するテストコード
def test_error(data):
    """
    dataは[[[x, y, z],....]], [[x, y, z]....]]]
    """
    print("error"*100)
    print(len(data))
    for i, d in enumerate(data):
        print(len(d))
        print(d)
        if i == 2:
            break
        
moveDTW()