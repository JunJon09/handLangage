import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

def main():
    cap = cv2.VideoCapture('../data/単語集/アメリカ/amerika1.mp4')  # 入力動画ファイルのパス
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 出力ファイルのフォーマット
    out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))  # 出力動画ファイルのパス

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("動画ファイルの読み込みが終了しました。")
                break

            # Convert the BGR image to RGB before processing.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = holistic.process(image)
            
            # Draw landmarks of the pose, left hand, and right hand.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            # Draw the nose landmark with a different color.
            if results.pose_landmarks:
                nose = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE]
                image = cv2.circle(image, (int(nose.x * image.shape[1]), int(nose.y * image.shape[0])), radius=5, color=(255, 0, 0), thickness=-1)

            out.write(image)

    cap.release()
    out.release()

if __name__ == '__main__':
    main()
"""
枝切り
並列計算
"""