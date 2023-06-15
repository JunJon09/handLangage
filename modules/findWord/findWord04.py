import cv2
import mediapipe as mp
import random
import math
#映像構造ベイズ推定を用いた手法
# https://eprints.lib.hokudai.ac.jp/dspace/bitstream/2115/58919/1/Yan_Song.pdf

# MediaPipe の Pose ソリューションと描画ユーティリティを初期化
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

def oneWord():
    #oneSentencePath = "../data/OneSentenceMovie/NHKNews/2023-03-22_00.mp4"
    oneSentencePath = "../data/OneSentenceMovie/test.mov"
    
    cap = cv2.VideoCapture(oneSentencePath)
    shotFrame, shotResult = getshot(cap)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    getCandidateSegmentationPoint(shotResult, width, height)
   
#フレームデータをshotに直した
def getshot(cap): 
    shotFrame = []
    shotResults = []
    frameData = []
    resultData = []


    if not cap.isOpened():
        print("動画ファイルが開けませんでした。正しいパスを指定してください。")
        return
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # BGR画像をRGB画像に変換
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # フレームに対して骨格検出を実行
        results = pose.process(rgb_frame)

        # 骨格検出の結果を元のフレームに描画
        annotated_frame = frame.copy()
        mp_drawing.draw_landmarks(annotated_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        if results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value].visibility > 0.5 and results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].visibility > 0.5:
            frameData.append(frame)
            resultData.append(results)

        if len(frameData) >= 5:
            shotFrame.append(frameData)
            shotResults.append(resultData)
            frameData = []
            resultData = []

        # 描画されたフレームを表示
        cv2.imshow('Skeleton Detection', annotated_frame)
        
        # キー入力があればループを終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    return shotFrame, shotResults

#step1 (手話映像から分割候補点を見つける)
def getCandidateSegmentationPoint(shots, width, height):
    kMax = 10
    
    #(i)について
    split_numberList = []
    split_numberList.append(random.randint(1, len(shots) -1))
    split_numberList.append(2)
    #(ii)について
    while True:
        Th = random.random()
        flag = transitionProbability(split_numberList)
        print("fffff")
        if flag == 1: #merge
            pass
        elif flag == 2: #split
            pass
        else: #shift
            pass
        break


def transitionProbability(split_numberList):
    flag = 0
    if len(split_numberList) == 0 or len(split_numberList) == 1:
        return 2
    
    c = 0.7
    b = c * min(1, priorProbability(len(split_numberList)-1)/priorProbability(len(split_numberList)))
    d = c * min(1, priorProbability(len(split_numberList)+1)/priorProbability(len(split_numberList)))
    n = 1 - (b + d)
    number = random.random()
    if 0 <= number and number <= b:
        flag = 1
    elif number <= (b + d):
        flag = 2
    else:
        flag = 3
    return flag

def priorProbability(k):
    λ = 8
    p = (math.e ** (-1*λ)) * (λ**k)/math.factorial(k)
    return p

def getMerge(): #merge処理
    pass
    
def getSplit(): #split処理
    pass
def getShift(split_numberList, shots): #shift処理
    #mを[0, k-1]の間で決めてシーンSmとSm+1の間のショットを比べてあげてp(t)が最大のものを採用する
    m = random.randint(0, len(split_numberList)-1)
    t = -1
    if m == 0:
        for shot in shots[0:split_numberList[m+1]]:
            pass
    elif m == len(split_numberList):
        for shot in shots[split_numberList[m-1]+1:]:
            pass
    else:
        for shot in shots[split_numberList[m-1]+1:split_numberList[m+1]]:
            pass


oneWord()