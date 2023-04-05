import copy
import cv2
import mediapipe as mp
import os
import numpy as np
import subprocess
import csv
import removeSilence as rs
from pydub import AudioSegment

#手話映像を一文の映像に切り取る
def oneSentence():
    movie_file = '../data/Movie/NHKNews/2023-03-22.mp4'
    wav_file = '../data/Wav/NHKNews/2023-03-24.wav'
    file_name = os.path.splitext(os.path.basename(movie_file))[0] #hoge.pyのhoge取得(ファイル名)
    result_path = "../data/OneSentenceMovie/NHKNews"
    # 音声ファイルで振幅調査
    voice_sentence = rs.get_no_silence_time(wav_file)
    # 動画ファイルの準備 ########################################################
    cap = cv2.VideoCapture(movie_file)
    
    """
    動画と音声のファイルでは時間が一致してないので合わせる 理
    """
    sound_time = AudioSegment.from_file(wav_file, "wav").duration_seconds #音声の秒数を取得
    time_difference =  abs(sound_time - cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)) # |音声の秒数 - (動画の総フレームレート/FPS)| ...(動画の総フレームレート/FPS) = 動画の秒数

    sentences = getSentence(time_difference, cap, voice_sentence)
    cutOneSentence(sentences, file_name, movie_file, result_path, time_difference)


def getSentence(time_difference, cap, voice_sentence):
    #MediaPipeのPoseモデルの読み込み
    """
    model_complexityはモデルの調整をするためのパラメータ
     値が小さいほどモデルの複雑さが低くなり推定速度向上精度低くなる 高いほど逆になる 値(0, 1, 2)
    min_detection_confidenceは物体検出の最小信頼度を指定するパラメータ
     指定した値が低い場合はその物体検出を無視 値(0-1.0)
    min_tracking_confidenceは姿勢検出の最小信頼度を指定するパラメータ
     上記とほとんど同じ
    """
    pose = mp.solutions.pose.Pose(
        model_complexity=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # FPS計測
    flame = 0 #現在のフレーム数
    flame_count_flag = False #cross_hand判定のフレームをカウントするフラグ
    flame_count = 0 #cross_hand判定を行うためフレームをカウントする
    
    voice_end = False  #声の終わり
    cross_hand = False #手の交差
    end_count = 0 #文章の終わりを記録するためのフラグ
    #右手と左手の座標
    lhand = {"x":0, "y":0}
    rhand = {"x":0, "y":0}

    elbow = {"r":0, "l":0} #右腕左腕の肘の高さ

	#一文の時間を格納
    sentences = []
    sentence_start_time = cap.get(cv2.CAP_PROP_POS_MSEC)/1000 + time_difference #現在のフレームを取得してミリから秒単位に変換. 時間差をプラス

    #肘より手が下にあるフレーム数
    flame_num = 0
    
    #手が下にある状態（文章の一が音声より手が先に動くときの
    under_hand_flag = True

    while True:
        display_fps = cap.get(cv2.CAP_PROP_FPS) #フレームレート取得
        cap_sec = cap.get(cv2.CAP_PROP_POS_MSEC)/1000 + time_difference  #現在のフレームを取得してミリから秒単位に変換. 時間差をプラス
        flame += 1

        # カメラキャプチャ #####################################################
        # 動画   ######
        ret, image = cap.read()
        if not ret:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        debug_image = copy.deepcopy(image)

        # 検出実施 #############################################################
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #BGR->RGBに変換
        results = pose.process(image) #画像から姿勢推定を行う

        # 描画 ################################################################
        if results.pose_landmarks is not None: 
            # 外接矩形の計算
            brect = calcBoundingRect(debug_image, results.pose_landmarks)
            # 描画
            debug_image = drawLandmarks(
                debug_image,
                results.pose_landmarks,
                rhand,
                lhand,
                elbow
            )
            debug_image = drawBoundingRect(True, debug_image, brect)
        

        cv2.putText(debug_image, "FPS:" + str(display_fps), (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.putText(debug_image, str(rhand["x"]), (0, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(debug_image, str(lhand["x"]), (0, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2, cv2.LINE_AA)

        #手の交差条件
        hand_distance_x = abs(rhand["x"] - lhand["x"]) #右手左手のx軸の距離
        hand_distance_y = abs(rhand["y"] - lhand["y"]) #右手左手のy軸の距離
        cv2.putText(debug_image, "x:" + str(hand_distance_x), (0, 300),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(debug_image, "y:" + str(hand_distance_y), (0, 350),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2, cv2.LINE_AA)


        #音声からスタート時間を取得
        for time in voice_sentence:
            if time["from"] < cap_sec and time["to"] > cap_sec:
                cv2.putText(debug_image, "voice", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
                voice_end = False
                break             
            else:
                cv2.putText(debug_image, str(cap_sec), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)
                voice_end = True

        #肘より手が下
        if elbow["r"] < rhand["y"] and elbow["l"] < lhand["y"]:
            under_hand_flag = True
            flame_num += 1
        else:
            #前フレームで手が交差している状態で今フレームは肘より上に手がある場合
            #手が動いていた時間を取得
            under_hand_flag = False
        

        if hand_distance_x <= 170 and hand_distance_y <=30 and under_hand_flag:
            flame_count_flag = True
            cv2.putText(debug_image, "flag", (0, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            flame_count_flag = False
        
        if flame_count_flag:
            flame_count += 1
        else:
            flame_count = 0

        #15フレーム以上手が上記の条件であれば交差していると判定
        if flame_count >= 15:
            cross_hand = True
            cv2.putText(debug_image, "cross", (0, 500),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 5, cv2.LINE_AA)
        else:
            cross_hand = False



        # キー処理(ESC：終了) #################################################
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break

        #
        if voice_end == False or cross_hand == False:
            cv2.putText(debug_image, "speak", (0, 500), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
            #手が音声より先に動き出したと言うフラグは文章の終わりでFalseに変更
            end_count = 0
        else:
            end_count+=1
            if end_count == 1:
                if cap_sec < 3:
                    continue
                elif len(sentences) == 0:
                    sentences.append({"from": sentence_start_time, "to": cap_sec})
                    print("from:{} to:{}".format(sentence_start_time,cap_sec))
                elif not sentences[-1]["from"] == sentence_start_time:
                    sentences.append({"from": sentence_start_time, "to": cap_sec})
                    print("from:{} to:{}".format(sentence_start_time,cap_sec))
            #TODO シュワ動作からは字丸文は前がほんの少し切れるのでcap_secから数秒引いて丁度いいのを探す
            sentence_start_time = cap_sec
        cv2.putText(debug_image, str(sentence_start_time), (0, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
        # 画面反映 #############################################################
        cv2.imshow('MediaPipe Pose', debug_image)


    print(sentences)
    cap.release()
    cv2.destroyAllWindows()

    return sentences


#長方形の描画
def calcBoundingRect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv2.boundingRect(landmark_array)

    return [x, y, x + w, y + h]

#骨格座標を検出
def drawLandmarks(
    image,
    landmarks,
    rhand,
    lhand,
    elbow,
    visibility_th=0.5,
):
    image_width, image_height = image.shape[1], image.shape[0]

 
    landmark_point = []

    for index, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_z = landmark.z
        landmark_point.append([landmark.visibility, (landmark_x, landmark_y)])

        if landmark.visibility < visibility_th:
            continue

        if index == 11:  # 右肩
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
        if index == 12:  # 左肩
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
        if index == 13:  # 右肘
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            elbow["r"] = landmark_y
        if index == 14:  # 左肘
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            elbow["l"] = landmark_y
        if index == 15:  # 右手首
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            lhand["x"] = landmark_x
            lhand["y"] = landmark_y

            cv2.putText(image, str(landmark_x), (landmark_x,landmark_y), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 0, 0), 5, cv2.LINE_AA)
        if index == 16:  # 左手首
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            rhand["x"] = landmark_x
            rhand["y"] = landmark_y

            cv2.putText(image, str(landmark_x), (landmark_x, landmark_y), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 5, cv2.LINE_AA)

        if index == 17:  # 左手(外側端)
            cv2.circle(image, (landmark_x, landmark_y), 5, (255, 0, 0), 2)

        if index == 18:  #（右手）(外側端)
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 0, 255), 2)
            if landmark_x == None:
                cv2.putText(image, "None", (0, 200), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 5, cv2.LINE_AA)

        if index == 23:  # 腰(右側)
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)

        if index == 24:  # こっちから左（右腰）　腰(左側)
            cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)

        # if not upper_body_only:
        if True:
            cv2.putText(image, "z:" + str(round(landmark_z, 3)),
                       (landmark_x - 10, landmark_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
                       cv2.LINE_AA)

    if len(landmark_point) > 0:

        # 肩
        if landmark_point[11][0] > visibility_th and landmark_point[12][
                0] > visibility_th:
            cv2.line(image, landmark_point[11][1], landmark_point[12][1],
                    (0, 255, 0), 2)

        # 右腕
        if landmark_point[11][0] > visibility_th and landmark_point[13][
                0] > visibility_th:
            cv2.line(image, landmark_point[11][1], landmark_point[13][1],
                    (0, 255, 0), 2)
        if landmark_point[13][0] > visibility_th and landmark_point[15][
                0] > visibility_th:
            cv2.line(image, landmark_point[13][1], landmark_point[15][1],
                    (0, 255, 0), 2)

        # 左腕
        if landmark_point[12][0] > visibility_th and landmark_point[14][
                0] > visibility_th:
            cv2.line(image, landmark_point[12][1], landmark_point[14][1],
                    (0, 255, 0), 2)
        if landmark_point[14][0] > visibility_th and landmark_point[16][
                0] > visibility_th:
            cv2.line(image, landmark_point[14][1], landmark_point[16][1],
                    (0, 255, 0), 2)

        # 右手
        if landmark_point[15][0] > visibility_th and landmark_point[17][
                0] > visibility_th:
            cv2.line(image, landmark_point[15][1], landmark_point[17][1],
                    (0, 255, 0), 2)
        if landmark_point[17][0] > visibility_th and landmark_point[19][
                0] > visibility_th:
            cv2.line(image, landmark_point[17][1], landmark_point[19][1],
                    (0, 255, 0), 2)
        if landmark_point[19][0] > visibility_th and landmark_point[21][
                0] > visibility_th:
            cv2.line(image, landmark_point[19][1], landmark_point[21][1],
                    (0, 255, 0), 2)
        if landmark_point[21][0] > visibility_th and landmark_point[15][
                0] > visibility_th:
            cv2.line(image, landmark_point[21][1], landmark_point[15][1],
                    (0, 255, 0), 2)

        # 左手
        if landmark_point[16][0] > visibility_th and landmark_point[18][
                0] > visibility_th:
            cv2.line(image, landmark_point[16][1], landmark_point[18][1],
                    (0, 255, 0), 2)
        if landmark_point[18][0] > visibility_th and landmark_point[20][
                0] > visibility_th:
            cv2.line(image, landmark_point[18][1], landmark_point[20][1],
                    (0, 255, 0), 2)
        if landmark_point[20][0] > visibility_th and landmark_point[22][
                0] > visibility_th:
            cv2.line(image, landmark_point[20][1], landmark_point[22][1],
                    (0, 255, 0), 2)
        if landmark_point[22][0] > visibility_th and landmark_point[16][
                0] > visibility_th:
            cv2.line(image, landmark_point[22][1], landmark_point[16][1],
                    (0, 255, 0), 2)

        # 胴体
        if landmark_point[11][0] > visibility_th and landmark_point[23][
                0] > visibility_th:
            cv2.line(image, landmark_point[11][1], landmark_point[23][1],
                    (0, 255, 0), 2)
        if landmark_point[12][0] > visibility_th and landmark_point[24][
                0] > visibility_th:
            cv2.line(image, landmark_point[12][1], landmark_point[24][1],
                    (0, 255, 0), 2)
        if landmark_point[23][0] > visibility_th and landmark_point[24][
                0] > visibility_th:
            cv2.line(image, landmark_point[23][1], landmark_point[24][1],
                    (0, 255, 0), 2)

 
    return image


def drawBoundingRect(use_brect, image, brect):
    if use_brect:
        # 外接矩形
        cv2.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                     (0, 255, 0), 2)

    return image

# 動画を分割
def cutOneSentence(sentences, file_name, movie_file, result_path, time_difference):
    
    for i, sentence in enumerate(sentences):
        result_file = file_name + "_{:02d}".format(i)
        mov_duration = sentence["to"] - sentence["from"]
        print("to:{} from:{} duration:{}".format(sentence["to"], sentence["from"], mov_duration))
        cmd = 'echo n | ffmpeg -ss {} -i \"{}\" -t {} \"{}/{}.mp4\"'.format(sentence["from"], movie_file, mov_duration, result_path, result_file)

        subprocess.run(cmd, shell = True)  #動画切り取りコマンド実行
        with open(result_path + '/cut_time_target.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([movie_file.split('/')[-1],sentence["from"]-time_difference, sentence["to"]-time_difference])

oneSentence()
