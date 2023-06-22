import math
import numpy as np
from fastdtw import fastdtw
from statistics import variance 
from scipy.spatial.distance import euclidean


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
    #1, 25　[時系列、[関節21 , [x,y,z]]]
    for te in test: #1
        data1 = setData(te, len(train[0][0])) #len(42)
        for tr in train: #25
            data2 = setData(tr, len(train[0][0]))
            distance_sum_1 = 0
            distance_sum_2 = 0
            for d_1, d_2 in zip(data1, data2):
                print(len(d_1[0]), len(d_2[0]))
                distance, path = fastdtw(d_1, d_2, dist=euclidean)
                distance_sum_1 += distance
                distance_sum_2 += (distance**2)
            distanceDispersionList.append(distance_sum_1)
            distanceList.append(distance)
    return distanceList

#データをnumpyに変換して例として手の親指の付け根のx座標を時系列順にする。(他のも同様)
def setData(data, data_len):
    dataSets = []
    data = np.array(data)
    for i in range(data_len):
        dataSet = []
        for j in range(2):
            tmp = data[:, i, j]
            dataSet.append(tmp)
        dataSets.append(dataSet)
    print(len(dataSets))
    return dataSets