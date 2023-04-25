import cv2
import mediapipe as mp
import math
from matplotlib import pyplot

#松尾 直志の手法 #https://www.jstage.jst.go.jp/article/his/15/1/15_85/_pdf/-char/ja
def oneWord():
    #oneSentencePath = "../data/OneSentenceMovie/NHKNews/2023-03-22_00.mp4"
    oneSentencePath = "../data/OneSentenceMovie/test.mov"
    cap = cv2.VideoCapture(oneSentencePath)
    getMovieSplitTime(cap)

def getMovieSplitTime(cap):
    # 描画用のモジュール
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    pose = mp.solutions.pose.Pose(
        model_complexity=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    # 手の検出モジュール
    mp_hands = mp.solutions.hands
    # Hand Trackingモデルのインスタンス化
    v = []
    frame_count = 0
    speed_list = []
    front_locate_x = 0
    front_locate_y = 0
    x = []
    front_d = 0
    FPS = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # カラー変換 (BGR to RGB)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 手の検出
            results = hands.process(image)
            face = pose.process(image)

            # RGBからBGRに戻す
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # 検出された手の骨格を描画
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    handedness = 'Left' if results.multi_handedness[idx].classification[0].label == 'Left' else 'Right'
                    if handedness == 'Right':
                        continue

                    #鼻の位置
                    nose = face.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
                    nose_x = nose.x * width
                    nose_y = nose.y * height
                
                    # 中指の第二関節の座標を取得
                    middle_finger_joint = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                    x_mfj = middle_finger_joint.x * width
                    y_mfj = middle_finger_joint.y * height

                    # 手首の座標を取得
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    x_wrist = wrist.x * width
                    y_wrist = wrist.y * height

                    # 中指の頂点を取得
                    Tip_middle_finger = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    x_tip_mfj = Tip_middle_finger.x * width
                    y_tip_mfj =  Tip_middle_finger.y + height
                
                    # 中点の座標を計算
                    midpoint_x = (x_mfj + x_wrist) / 2
                    midpoint_y = (y_mfj + y_wrist) / 2

                    #閾値の計算
                    
                    #閾値v (中指の頂点と手首の差)
                    d = abs(y_tip_mfj - y_wrist)
                    
                    if len(x) == 0:
                        speed_list.append(0)
                        x.append(0)
                        front_frame = frame_count
                        v.append(0)
                    else:
                        dt = (frame_count - front_frame) / FPS
                        if dt == 0:
                            print(frame_count, front_frame, dt, idx)
                        speed = changeRD(nose_x, nose_y, midpoint_x, midpoint_y, front_locate_x, front_locate_y, dt)
                        speed_list.append(speed)
                        x.append(frame_count)
                        front_frame = frame_count
                        tmp_d = abs(front_d - d) / dt
                        v.append(2 * tmp_d)
                    front_locate_x = midpoint_x
                    front_locate_y = midpoint_y
                    front_d = d
                    
                    
                    cv2.circle(image, (int(midpoint_x), int(midpoint_y)), 25, (0, 0, 0), -1)
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    break
            frame_count += 1
            # 描画
            cv2.imshow('Middle Finger Second Joint Detection', image)

            # qキーで終了
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print(frame_count)
                # break

    cap.release()
    cv2.destroyAllWindows()
    pyplot.plot(x, speed_list)
    # pyplot.plot(x, v,color="red")
    pyplot.plot([47, 47], [0, 6000],color="green")
    pyplot.plot([111, 111], [0, 6000],color="green")
    pyplot.plot([165, 165], [0, 6000],color="green")
    flag = 0
    # for i, (_speed, _v) in enumerate(zip(speed_list, v)):
    #     if not(28 < x[i] and x[i] < 380):
    #         continue
    #     if _speed > _v and flag == 0:
    #         flag = 1
    #         pyplot.plot([x[i], x[i]], [0, 6000],color="green")
    #     elif _speed < _v and flag == 1:
    #         flag = 0
    #         pyplot.plot([x[i], x[i]], [0, 6000],color="green")
    pyplot.show()

def changeRD(origin_x, origin_y, x, y, front_x, front_y, dt):
    _x, _y = (origin_x - x), (origin_y - y)
    r = math.sqrt(_x**2 + _y**2)
    rad = math.atan2(_y, _x)
    _front_x, _front_y = (origin_x - front_x), (origin_y - front_y)
    front_r = math.sqrt(_front_x**2 + _front_y**2)
    front_rad = math.atan2(_front_y, _front_x)
    #時間が非常に小さいので近似値として
    dr = r - front_r
    drad = rad - front_rad

    v_r = dr / dt
    v_rad = r * (drad / dt)
    v = math.sqrt(v_r**2 + v_rad**2)

    return v

oneWord()