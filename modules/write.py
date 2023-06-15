import cv2
import mediapipe as mp
import numpy as np

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

colors = {
    'NOSE': (255, 0, 0),
    'LEFT_EYE': (0, 0, 255),
    'RIGHT_EYE': (255, 0, 255),
    'LEFT_SHOULDER': (128, 0, 128),
    'RIGHT_SHOULDER': (255, 128, 0),
    'LEFT_ELBOW': (128, 255, 0),
    'RIGHT_ELBOW': (0, 255, 128),
    'LEFT_WRIST': (128, 0, 255),
    'RIGHT_WRIST': (255, 0, 128),
    'LEFT_PINKY': (0, 128, 255),
    'RIGHT_PINKY': (128, 128, 128),
    'LEFT_INDEX': (255, 255, 128),
    'RIGHT_INDEX': (128, 255, 255),
    'LEFT_THUMB': (255, 128, 255),
    'RIGHT_THUMB': (64, 0, 0),
}
print(colors["NOSE"])

cap = cv2.VideoCapture('../data/単語集/アメリカ/amerika1.mp4')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (640, 480))
connections = [
    (mp_holistic.PoseLandmark.LEFT_SHOULDER, mp_holistic.PoseLandmark.LEFT_ELBOW),
    (mp_holistic.PoseLandmark.LEFT_ELBOW, mp_holistic.PoseLandmark.LEFT_WRIST),
    (mp_holistic.PoseLandmark.RIGHT_SHOULDER, mp_holistic.PoseLandmark.RIGHT_ELBOW),
    (mp_holistic.PoseLandmark.RIGHT_ELBOW, mp_holistic.PoseLandmark.RIGHT_WRIST),
    (mp_holistic.PoseLandmark.LEFT_EYE, mp_holistic.PoseLandmark.NOSE),
    (mp_holistic.PoseLandmark.RIGHT_EYE, mp_holistic.PoseLandmark.NOSE),
]
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform pose estimation
        results = holistic.process(rgb_image)

        # Create a black image with the same size as the original frame
        frame = np.zeros((480, 640, 3), np.uint8)

        # Draw landmarks on the image
        if results.pose_landmarks:
            for landmark in mp_holistic.PoseLandmark:
                # if str(landmark) in colors:
                index = landmark.value
                position = results.pose_landmarks.landmark[index]
                pixel_coordinates = mp_drawing._normalized_to_pixel_coordinates(position.x, position.y, frame.shape[1], frame.shape[0])
                if pixel_coordinates:
                    c = str(landmark).split(".")
                    try: 
                        cv2.circle(frame, pixel_coordinates, 5, colors[c[1]], -1)
                    except Exception:
                        pass
        
        for connection in connections:
                start_index = connection[0].value
                end_index = connection[1].value
                start_position = results.pose_landmarks.landmark[start_index]
                end_position = results.pose_landmarks.landmark[end_index]
                start_coordinates = mp_drawing._normalized_to_pixel_coordinates(start_position.x, start_position.y, frame.shape[1], frame.shape[0])
                end_coordinates = mp_drawing._normalized_to_pixel_coordinates(end_position.x, end_position.y, frame.shape[1], frame.shape[0])
                if start_coordinates and end_coordinates:
                    cv2.line(frame, start_coordinates, end_coordinates, colors[str(connection[0]).split(".")[1]], 2)
        # Write the frame into the file 'output.mp4'
        out.write(frame)

# Release everything after recording
cap.release()
out.release()
cv2.destroyAllWindows()