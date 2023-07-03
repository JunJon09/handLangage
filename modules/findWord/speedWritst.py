#手首の速度を極小、極大で考えて分割

import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd
import ffmpeg

def main():
    frame_count,wrist_speeds = findSklton()
    s = pd.Series(wrist_speeds)
    k = 20
    s_moving_average = s.rolling(k).mean() #k点移動平均
    s_moving_average = s_moving_average.dropna() #NaNの削除
    list_from_series = s_moving_average.tolist() #listに変更
    extrema = findPoint(frame_count,list_from_series, k)
    print(extrema)
    for i, t in enumerate(extrema):
        text = "./" + str(i) + ".mp4"
        if i == 0:
            cutMovie(0, t[0]/30, text)
        else:
            print(extrema[i-1][0], t[0], "aaa")
            cutMovie((extrema[i-1][0]+3)/30, t[0]/30, text)
        if i == len(extrema) - 1:
            print(t[0], t[0]/30, "vvv")
            text = "./" + str(i + 1) + ".mp4"
            cutMovie((t[0]+3)/30, frame_count/30, text)
    showPlt(list_from_series, frame_count, k)

def findSklton():
    mp_holistic = mp.solutions.holistic

    # For storing the wrist speeds
    wrist_speeds = []
    wrist_speeds.append(0)

    # For calculating relative coordinates
    def calculate_relative_coordinate(x, y, nose_center):
        return np.array([x - nose_center.x, y - nose_center.y])

    # For calculating speed
    def calculate_speed(p1, p2, t):
        speed = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        return speed/t

    cap = cv2.VideoCapture('../../data/OneSentenceMovie/vvv.mp4')

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        frame_count = 0
        prev_wrist_position = None
        prev_left = None
        prev_right = None
        while cap.isOpened():
            ret, image = cap.read()
            if not ret:
                print("Video file finished.")
                break
            
            # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = holistic.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                nose = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE]
                if results.left_hand_landmarks:
                    left_Wrist = results.left_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
                    left_W = calculate_relative_coordinate(left_Wrist.x, left_Wrist.y, nose)
                else:
                    if prev_left is None:
                        print("aa")
                        continue
                    else:
                        left_W = prev_left
                if results.right_hand_landmarks:
                    right_Wrist = results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
                    right_W = calculate_relative_coordinate(right_Wrist.x, right_Wrist.y, nose)
                else:
                    if prev_right is None:
                        print("rr")
                        continue
                    else:
                        right_W = prev_right
                average_postion = [(a + b) / 2 for a, b in zip(left_W, right_W)]
                if prev_wrist_position is not None:
                    wrist_speed = calculate_speed(prev_wrist_position, average_postion, 1.0/30.0)  # Assuming 1 frame = 1 second
                    wrist_speeds.append(wrist_speed)
                prev_wrist_position = average_postion
                prev_left = left_W
                prev_right = right_W
                frame_count += 1
            cv2.imshow('Middle Finger Second Joint Detection', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print(frame_count)
            
            if frame_count == 45:
                cv2.imwrite("./a.png", 45)
            elif frame_count == 66:
                cv2.imwrite("./b.png", 66)
            elif cv2.imwrite == 90:
                cv2.imwrite("./c.png", 90)
            
                
    cap.release()
    return frame_count,wrist_speeds

def findPoint(frame_count, listA, k):
    extrema = []
    front_frame = 0
    
    flag = 1 #動いてる状態
    i = 0
    while True:
        if i >= frame_count -k - 8:
            break
        if i <= 20 or front_frame + 10 > i:
            i += 1
            continue
        
        frame_number = i
        print(i, frame_count)
        if listA[i-1] < listA[i] > listA[i+1] and flag == 0:
            max = listA[i]
            for t in range(1, 11):
                if max < listA[t+i]:
                    max = listA[t+i]
                    frame_number = t+i
            extrema.append((frame_number, 'max'))
            flag = 1
            front_frame = frame_number
        elif listA[i-1] > listA[i] < listA[i+1] and flag == 1 and listA[i] < 0.3:
            min = listA[i]
            for t in range(1, 21):
                if min > listA[t+i]:
                    min = listA[t+i]
                    frame_number = t+i
            extrema.append((frame_number, 'min'))
            flag = 0
            front_frame = frame_number
        i = frame_number
        i += 1

    return extrema




def cutMovie(t1, t2, text):
    # stream = ffmpeg.input('../../data/OneSentenceMovie/test.mp4', ss=t1, t=t2).output(text)
    # ffmpeg.run(stream)
    input_file = '../../data/OneSentenceMovie/vvv.mp4'
    output_file = text
    start = t1  # 開始時間を指定
    end = t2   # 終了時間を指定

    stream = (
        ffmpeg
        .input(input_file, ss=start)
        .output(text, t=end-start, vcodec='libx264', acodec='copy')
        .run()
    )



def showPlt(listA, count, k):
    plt.plot([i for i in range(count-k+1)], listA, label="Average Speed")
    plt.show()




main()