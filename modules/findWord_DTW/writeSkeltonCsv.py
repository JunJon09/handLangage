import os
import cv2
import mediapipe as mp
import pickle
#単語集から関節のデータを集めてcsvに書き込むコード

def writeSKelton():
    files = getFile()
    leftList = []
    rightList = []
    bodyList = []
    print(files[0])
    for i, file in enumerate(files):
        left, right, body = getSkltooPosition(file)
        left = fixList(left)
        right = fixList(right)
        body = fixList(body)
        if len(left) == 0 or len(right) == 0 or len(body) == 0:
            print(i)
            continue
        writePickle(left, right, body, str(i))
    

#単語集からファイルを取得する
def getFile():
    word = "方針"
    filePath = "../../data/単語集/" + word + "/"
    files = os.listdir(filePath)
    filePathList = []
    [filePathList.append(filePath + file) for file in files]
    return filePathList


def getSkltooPosition(file):
    left_hand_positionList = []
    right_hand_positionList = []
    body_positionList = []

    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic

    # 動画ファイルを設定します
    cap = cv2.VideoCapture(file)

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            left_hand_position = []
            right_hand_position = []
            body_position = []
            # BGRからRGBへ変換して、ホリスティックモデルにフレームを送ります
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = holistic.process(image)

            # RGBからBGRへ変換して描画処理を行います
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # 手首の座標を取得
            if results.left_hand_landmarks:
                left_hand = results.left_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
                for id, lm in enumerate(results.left_hand_landmarks.landmark):
                    left_hand_position.append([lm.x - left_hand.x, lm.y - left_hand.y, lm.z - left_hand.z])
            if results.right_hand_landmarks:
                right_hand = results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
                for id, lm in enumerate(results.right_hand_landmarks.landmark):
                    right_hand_position.append([lm.x - right_hand.x, lm.y - right_hand.y, lm.z - right_hand.z])

            # 上半身の座標を取得
            if results.pose_landmarks:
                nose = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE]
                for id, lm in enumerate(results.pose_landmarks.landmark):
                    body_position.append([lm.x - nose.x, lm.y - nose.y, lm.z - nose.z])
            if len(left_hand_position) == 21:
                left_hand_positionList.append(left_hand_position)
            else:
                left_hand_positionList.append([])
            
            if len(right_hand_position) == 21:
                right_hand_positionList.append(right_hand_position)
            else:
                right_hand_positionList.append([])
            if len(body_position) == 33:
                body_positionList.append(body_position)
            else:
                body_positionList.append([])
                
            cv2.imshow('Middle Finger Second Joint Detection', image)
            # qキーで終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # キャプチャを解放します
    cap.release()
    fixPositionList(left_hand_positionList)
    fixPositionList(right_hand_positionList)
    fixPositionList(body_positionList)
    return left_hand_positionList, right_hand_positionList, body_positionList

"""座標リストに空が入ってる可能性があるので以下のルールに沿って変更する
空がある前後の平均の位置を代入するint型で
空が2個以上続いた場合も同様に平均値をとり、連続の空は全て同じ値になる
空が最初と最後の時は一番最初、もしくは最後にある値と同じにする
"""
def fixPositionList(input_list):
    #空が初めの時
    n = len(input_list)
    # 前と後ろの空白を処理
    for i in range(n):
        if len(input_list[i]) == 0:
            if i == 0:
                # 最初の要素が空白の場合、次の非空白要素で置き換え
                next_val = next(x for x in input_list if len(x) != 0)
                input_list[i] = next_val
            elif i == n-1:
                # 最後の要素が空白の場合、前の非空白要素で置き換え
                prev_val = next(x for x in reversed(input_list) if len(x) != 0)
                input_list[i] = prev_val
            else:
                # 真ん中の空白は前後の平均値で置き換え
                prev_val = input_list[i-1]
                next_val = next(x for x in input_list[i+1:] if len(x) != '')
                tmp = []
                for prev, back in zip(prev_val, next_val):
                    tmp.append([int(a + b) for a, b in zip(prev, back)])
                input_list[i] = tmp
    return input_list

def fixList(data):
    for i, d in enumerate(data):
        if len(d) == 0:
            if i == 0:
                next_list = next(x for x in data if len(x) != 0)
                data[i] = next_list
            else:
                prev_val = next(x for x in reversed(data) if len(x) != 0)
                data[i] = prev_val
    return data


def writePickle(left, right, body, number):
    textName = "./DTWList/policy" + number
    textLeft = textName + "_left.bin" 
    textRight = textName + "_right.bin"
    textBody = textName + "_body.bin"
    with open(textLeft, "wb") as p:
        pickle.dump(left, p)
    with open(textRight, "wb") as p:
        pickle.dump(right, p)
    with open(textBody, "wb") as p:
        pickle.dump(body, p)


writeSKelton()