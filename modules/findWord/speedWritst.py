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
    for i, t in enumerate(extrema):
        text = "./" + str(i) + ".mp4"
        if i == 0:
            cutMovie(0, t[0]/30, text)
        else:
            cutMovie(extrema[i-1][0]/30, t[0]/30, text)
            print(t[0]/30)
        if i == len(extrema) - 1:
            text = "./" + str(i + 1) + ".mp4"
            print(t[0]/30)
            cutMovie(t[0]/30, frame_count/30, text)


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

    cap = cv2.VideoCapture('../../data/OneSentenceMovie/b.mp4')

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        frame_count = 0
        prev_wrist_position = None
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
            # if results.multi_hand_landmarks:
            #     nose_center = [results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x, results.face_landmarks.landmark[mp_holistic.FaceLandmark.NOSE_TIP].y]
            #     for hand_landmarks in results.multi_hand_landmarks:
            #         wrist_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            #         wrist_position = calculate_relative_coordinate(wrist_landmark.x, wrist_landmark.y, nose_center)
            #         if prev_wrist_position is not None:
            #             wrist_speed = calculate_speed(prev_wrist_position, wrist_position, 1.0)  # Assuming 1 frame = 1 second
            #             wrist_speeds.append(wrist_speed)
            #         prev_wrist_position = wrist_position
            
            if results.pose_landmarks:
                nose = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE]
                if results.left_hand_landmarks:
                    left_Wrist = results.left_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
                    left_W = calculate_relative_coordinate(left_Wrist.x, left_Wrist.y, nose)
                else:
                    print("rrr")
                    continue
                if results.right_hand_landmarks:
                    right_Wrist = results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
                    right_W = calculate_relative_coordinate(right_Wrist.x, right_Wrist.y, nose)
                else:
                    print("aaa")
                    continue
                average_postion = [(a + b) / 2 for a, b in zip(left_W, right_W)]
                if prev_wrist_position is not None:
                    wrist_speed = calculate_speed(prev_wrist_position, average_postion, 1.0/30.0)  # Assuming 1 frame = 1 second
                    wrist_speeds.append(wrist_speed)
                prev_wrist_position = average_postion
                frame_count += 1
            cv2.imshow('Middle Finger Second Joint Detection', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                    print(frame_count)
    cap.release()
    return frame_count,wrist_speeds

def findPoint(frame_count, listA, k):
    extrema = []
    front_frame = 0
    
    flag = 1 #動いてる状態
    i = 0
    while True:
        if i >= frame_count -k -8:
            break
        if i <= 20 or front_frame + 20 > i:
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
    stream = ffmpeg.input('../../data/OneSentenceMovie/b.mp4', ss=t1, t=t2).output(text)
    ffmpeg.run(stream)





main()