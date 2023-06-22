import matplotlib.pyplot as plt
import numpy as np
hand_landmarks = [
    "Wrist",
    "Thumb CMC (carpometacarpal joint)",
    "Thumb MCP (metacarpophalangeal joint)",
    "Thumb IP (interphalangeal joint)",
    "Thumb Tip",
    "Index Finger MCP (metacarpophalangeal joint)",
    "Index Finger PIP (proximal interphalangeal joint)",
    "Index Finger DIP (distal interphalangeal joint)",
    "Index Finger Tip",
    "Middle Finger MCP (metacarpophalangeal joint)",
    "Middle Finger PIP (proximal interphalangeal joint)",
    "Middle Finger DIP (distal interphalangeal joint)",
    "Middle Finger Tip",
    "Ring Finger MCP (metacarpophalangeal joint)",
    "Ring Finger PIP (proximal interphalangeal joint)",
    "Ring Finger DIP (distal interphalangeal joint)",
    "Ring Finger Tip",
    "Pinky MCP (metacarpophalangeal joint)",
    "Pinky PIP (proximal interphalangeal joint)",
    "Pinky DIP (distal interphalangeal joint)",
    "Pinky Tip",
]

pose_landmarks = [
    "Nose",
    "Left Eye Inner",
    "Left Eye",
    "Left Eye Outer",
    "Right Eye Inner",
    "Right Eye",
    "Right Eye Outer",
    "Left Ear",
    "Right Ear",
    "Mouth Left",
    "Mouth Right",
    "Left Shoulder",
    "Right Shoulder",
    "Left Elbow",
    "Right Elbow",
    "Left Wrist",
    "Right Wrist",
    "Left Pinky",
    "Right Pinky",
    "Left Index",
    "Right Index",
    "Left Thumb",
    "Right Thumb",
    "Left Hip",
    "Right Hip",
    "Left Knee",
    "Right Knee",
    "Left Ankle",
    "Right Ankle",
    "Left Heel",
    "Right Heel",
    "Left Foot Index",
    "Right Foot Index",
]
left_combined_list = []
right_combined_list = []
body_combined_list = []
hand_landmark = []
pose_landmark = []
for hand in hand_landmarks:
    text_x = hand + "-x"
    text_y = hand + "-y"
    hand_landmark.append(text_x)
    hand_landmark.append(text_y)
for pose in pose_landmarks:
    text_x = pose + "-x"
    text_y = pose + "-y"
    pose_landmark.append(text_x)
    pose_landmark.append(text_y)

def main(distanceList, flag):
    if flag == 0: #左手
        left_combined_list.append(distanceList)
    elif flag == 1: #右手
        right_combined_list.append(distanceList)
    else: #ボディ
        body_combined_list.append(distanceList)

def showPlt():
    sum_left_combined_list = [sum(x) for x in zip(*left_combined_list)]
    sum_right_combined_list = [sum(x) for x in zip(*right_combined_list)]
    sum_body_combined_list = [sum(x) for x in zip(*body_combined_list)]

    left_combined_sort = list(zip(hand_landmark, sum_left_combined_list))
    left_combined_name = [(f"L-{x[0]}", x[1]) for x in left_combined_sort]
    right_combined_sort = list(zip(hand_landmark, sum_right_combined_list))
    right_combined_name = [(f"R-{x[0]}", x[1]) for x in right_combined_sort]
    body_combined_name = list(zip(pose_landmark, sum_body_combined_list))
    
    all_combined = left_combined_name + right_combined_name + body_combined_name
    all = x_yCombiList(all_combined)
    sorted_list = sorted(all_combined, key=lambda x: x[1], reverse=True)
    sorted_list_xy = sorted(all, key=lambda x: x[1], reverse=True)
    all_combined = sorted_list
    all_xy = sorted_list_xy
    print(all_combined)
    print("*"*100)
    print(all_xy)    
    createPlt(left_combined_name, "left.png")
    createPlt(right_combined_name, "right.png")
    createPlt(body_combined_name, "body.png")
    createPlt(all_combined, "all.png")
    createPlt(all_xy, "allx_y.png")

    

def createPlt(combined_list, name):
    plt.rcParams["font.size"] = 4
    x_values, y_values = zip(*combined_list)
    height = np.array(y_values)
    

    plt.bar(x_values, y_values)
    plt.xticks(rotation=90)
    plt.savefig(name)
    plt.clf()

def x_yCombiList(all_combined):#x, yを一緒にする
    tmp = 0
    all = []
    for i in range(len(all_combined)):
        x_y = []
        if i % 2 == 0:
            tmp = all_combined[i][1]
        else:
            tmp += all_combined[i][1]
            if (i + 1) / 2 <= 21: #left
                text = "L-" + hand_landmarks[int((i-1)/2)]
                x_y.append(text)
                x_y.append(tmp)
            elif (i + 1) / 2 <= 42: #right
                text = "R-" + hand_landmarks[int((i-1)/2)-21]
                x_y.append(text)
                x_y.append(tmp)
            else: #body
                text = pose_landmarks[int((i-1)/2) - 42]
                x_y.append(text)
                x_y.append(tmp)
            all.append(x_y)

    return all