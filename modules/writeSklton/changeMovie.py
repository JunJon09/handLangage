import cv2
import mediapipe as mp
import numpy as np

def main(file_path, write_path, output):
    # mediapipeのモデルを初期化
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # 入力動画ファイル
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print("Error opening video stream or file")

    # 出力動画ファイル
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output, fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(3)), int(cap.get(4))))
    skeleton = cv2.VideoWriter(write_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(3)), int(cap.get(4))))


    # 骨格点の色を固定値で定義
    colors = [(i*15 % 256, i*25 % 256, i*35 % 256) for i in range(mp_pose.PoseLandmark.__len__())]

    # 骨格を結ぶための線のリストを定義
    connections = mp_pose.POSE_CONNECTIONS

    # Pose Estimationモデルを初期化
    with mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # RGBに変換
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 骨格座標を推定
            results = pose.process(image)

            # 骨格を描画
            annotated_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.pose_landmarks:
                for id, lm in enumerate(results.pose_landmarks.landmark):
                    h, w, c = annotated_image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(annotated_image, (cx, cy), 5, colors[id], cv2.FILLED)
                # 骨格を線で結ぶ
                for connection in connections:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    if results.pose_landmarks.landmark[start_idx].visibility > 0.5 and results.pose_landmarks.landmark[end_idx].visibility > 0.5:
                        start_pos = (int(results.pose_landmarks.landmark[start_idx].x * w), int(results.pose_landmarks.landmark[start_idx].y * h))
                        end_pos = (int(results.pose_landmarks.landmark[end_idx].x * w), int(results.pose_landmarks.landmark[end_idx].y * h))
                        cv2.line(annotated_image, start_pos, end_pos, colors[start_idx], 2)
            
            skeleton_image = np.zeros_like(annotated_image)
            if results.pose_landmarks:
                for id, lm in enumerate(results.pose_landmarks.landmark):
                    h, w, c = skeleton_image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(skeleton_image, (cx, cy), 5, colors[id], cv2.FILLED)
                # 骨格を線で結ぶ
                for connection in connections:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    if results.pose_landmarks.landmark[start_idx].visibility > 0.5 and results.pose_landmarks.landmark[end_idx].visibility > 0.5:
                        start_pos = (int(results.pose_landmarks.landmark[start_idx].x * w), int(results.pose_landmarks.landmark[start_idx].y * h))
                        end_pos = (int(results.pose_landmarks.landmark[end_idx].x * w), int(results.pose_landmarks.landmark[end_idx].y * h))
                        cv2.line(skeleton_image, start_pos, end_pos, colors[start_idx], 2)
            
            out.write(annotated_image)
            skeleton.write(skeleton_image)

    cap.release()
    out.release()
