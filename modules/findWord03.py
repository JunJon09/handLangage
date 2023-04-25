import cv2
import mediapipe as mp
import math
#映像構造の分割法とベイズ推定を用いた手法
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
    MTR = 1 #最長時間幅の閾値
    CT = 15 #クラスタリングの閾値
    clustering = []
    
    for i, shot in enumerate(shots):
        for j, compareShot in enumerate(shots[i+1:], i+1):
            leftWrist = shot[0].pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
            rightWrist = shot[0].pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
            leftWrist_x, leftWrist_y= int(leftWrist.x * width), int(leftWrist.y * height)
            rightWrist_x, rightWrist_y = int(rightWrist.x * width), int(rightWrist.y * height)

            compareLeftWrist = compareShot[0].pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST.value]
            compareRightWrist = compareShot[0].pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value]
            compareLeftWrist_x, compareLeftWrist_y = int(compareLeftWrist.x * width), int(compareLeftWrist.y * height)
            compareRightWrist_x, compareRightWrist_y = int(compareRightWrist.x * width), int(compareRightWrist.y * height)

            leftDistance = math.sqrt((leftWrist_x - compareLeftWrist_x)**2 + (leftWrist_y - compareLeftWrist_y)**2)
            rightDistance = math.sqrt((rightWrist_x - compareRightWrist_x)**2 + (rightWrist_y - compareRightWrist_y)**2)
            
            if leftDistance < CT and rightDistance < CT:
                print(i, j)
                print(leftDistance, rightDistance)
            
        

oneWord()