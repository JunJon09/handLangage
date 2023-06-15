import cv2
import mediapipe as mp
import pickle


#手話単語の映像の特徴から判断する
def oneWord():
    #oneSentencePath = "../data/OneSentenceMovie/NHKNews/2023-03-22_00.mp4"
    oneSentencePath = "../data/OneSentenceMovie/test.mov"
    cap = cv2.VideoCapture(oneSentencePath)
    df = getJointList(cap)
    writeJointList(df)
    

def getJointList(cap):
    if not cap.isOpened():
        print("動画ファイルが開けませんでした。正しいパスを指定してください。")
        return
    df = []
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_holistic = mp.solutions.holistic
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # BGR画像をRGB画像に変換
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with mp_holistic.Holistic(static_image_mode=True,
                                        model_complexity=2,
                                        enable_segmentation=True,
                                        refine_face_landmarks=True) as holistic:
                    
            results = holistic.process(rgb_frame)
            annotated_image = frame.copy()
            mp_drawing.draw_landmarks(
                annotated_image,
                results.face_landmarks,
                mp_holistic.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
            mp_drawing.draw_landmarks(
                annotated_image,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                )
            mp_drawing.draw_landmarks(
                annotated_image,
                results.left_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
                )
        joint_list = []
        doll_list = []
        face_list = []
        right_hand_list = []
        left_hand_list = []
        try:
            poses = results.pose_landmarks.landmark
            for pose in poses:
                doll_list.append(pose)
            faces = results.face_landmarks.landmark
            for face in faces:
                face_list.append(face)
            right_hands = results.right_hand_landmarks.landmark
            for hand in right_hands:
                right_hand_list.append(hand)
            left_hands = results.left_hand_landmarks.landmark
            for hand in left_hands:
                left_hand_list.append(hand)
        except:
            pass
        else:
            joint_list.append(doll_list)
            joint_list.append(face_list)
            joint_list.append(right_hand_list)
            joint_list.append(left_hand_list)
            df.append(joint_list)
        
        # 描画されたフレームを表示
        cv2.imshow('Skeleton Detection', annotated_image)
         # キー入力があればループを終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    return df

def writeJointList(df):
    filePath = "../data/Pickle/data.pickle"
    with open(filePath, mode='wb') as f:
        pickle.dump(df, f)
    f.close()

oneWord()
filePath = "../data/Pickle/data.pickle"
with open(filePath, mode='br') as fi:
    b = pickle.load(fi)
    print(b, len(b[-1]), len(b))