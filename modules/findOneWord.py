import cv2
import mediapipe as mp
from matplotlib import pyplot as pyp
import math
import ffmpeg
import subprocess
import os


#内田らの手法
#手話映像の一文から単語を切り取る
def OneWord():

    oneSentencePath = "../data/OneSentenceMovie/test.mov"
    cap = cv2.VideoCapture(oneSentencePath)
    nosePositions, leftWristPositions, rightWristPositions, FPS = getSkeletonMovie(cap)
    tmp = showSignLanguageSpeed(nosePositions, leftWristPositions, rightWristPositions, FPS)
    result_path = "../data/OneSentenceMovie/NHKNews"
    current_directory = os.getcwd()
    print("現在の作業ディレクトリ:", current_directory)

    for i, t in enumerate(tmp):
        result_file = str(i) + ".mp4"
        print(t)
        if i == 0:
            stream = ffmpeg.input(oneSentencePath, ss=0, t=t).output(result_file)
            ffmpeg.run(stream)

        else:
            stream = ffmpeg.input(oneSentencePath, ss=t, t= t - tmp[i-1]).output(result_file)
            ffmpeg.run(stream)
       

#手話映像に骨格付与する
def getSkeletonMovie(cap):
    #MediaPipeのPoseモデルの読み込み 詳しくはcreateOneSentece.pyに記述
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp.solutions.pose.Pose(
        model_complexity=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    nosePositions = []
    leftWristPositions = []
    rightWristPositions = []
    postionCount = 0
    frameCount = 0
    FPS = cap.get(cv2.CAP_PROP_FPS)
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break

        # BGRからRGBに変換
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # MediaPipeで骨格検出
        result = pose.process(frame_rgb)

        # 検出した骨格を描画
        frame_draw = frame.copy()
        mp_drawing.draw_landmarks(frame_draw, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        if result.pose_landmarks:
            nose = result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            leftWrist = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
            rightWrist = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            if nose.visibility > 0.5 and leftWrist.visibility > 0.5 and rightWrist.visibility > 0.5:
                if frameCount == 0:
                    nosePositions.append([nose.x * width, nose.y * height])
                    leftWristPositions.append([leftWrist.x * width, leftWrist.y * height])
                    rightWristPositions.append([rightWrist.x * width, rightWrist.y * height])
                else:
                    postionCount += 1
        # 結果を表示
        cv2.imshow("Pose Detection", frame_draw)

        if postionCount >= 10:
            postionCount = 0
            nosePositions.append([(nose.x ) * width, nose.y * height])
            leftWristPositions.append([leftWrist.x * width, leftWrist.y * height])
            rightWristPositions.append([rightWrist.x * width, rightWrist.y * height])
        # キー入力で終了
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        frameCount += 1
        
    cap.release()
    cv2.destroyAllWindows()
    
    return nosePositions, leftWristPositions, rightWristPositions, FPS

def showSignLanguageSpeed(nosePositions, leftWristPositions, rightWristPositions, FPS):
    x = [i * 10 for i, j in enumerate(nosePositions)]
    y = []
    for i, (left, right) in enumerate(zip(leftWristPositions, rightWristPositions)):
        if i == 0:
            y.append(0)
        else:
            speed = math.sqrt(pow(left[0] - leftWristPositions[i-1][0], 2) + pow(left[1] - leftWristPositions[i-1][1], 2)) + math.sqrt(pow(right[0] - rightWristPositions[i-1][0], 2) + pow(right[1] - rightWristPositions[i-1][1], 2))
            y.append(speed/2)

    tmp = []
    print(FPS, "knrknignignirngi")
    print(len(y), y)
    for i, s in enumerate(y):
        if i != 0 and i+1 != len(y):
            if abs(s - y[i-1]) > 70 and abs(s-y[i+1]) > 70:
                tmp.append((i / FPS) * 10)
    
    
    return tmp
    

OneWord()
'echo n | ffmpeg -ss 0 -i "../data/OneSentenceMovie/test.mov" -t 0.03330112721417069 "../data/OneSentenceMovie/NHKNews/0.mp4"'
# echo n | ffmpeg -ss 60.25386666666668 -i "../data/Movie/NHKNews/2023-03-22.mp4" -t 13.179833333333335 "../data/OneSentenceMovie/NHKNews/2023-03-22_05.mp4"