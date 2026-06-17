import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import requests   # ✅ IMPORTANT (for backend connection)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle

def play_sound():
    from playsound import playsound
    playsound('alert.mp3')

alert_active = False
bad_start_time = None
bad_duration = 0
total_bad_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        shoulder = [
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
        ]

        hip = [
            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
        ]

        ear = [
            landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y
        ]

        angle = calculate_angle(ear, shoulder, hip)

        if angle < 40:
            posture = "Bad Posture"
            color = (0, 0, 255)

            if bad_start_time is None:
                bad_start_time = time.time()

            bad_duration = int(time.time() - bad_start_time)

            if not alert_active:
                alert_active = True
                threading.Thread(target=play_sound).start()

        else:
            posture = "Good Posture"
            color = (0, 255, 0)

            if bad_start_time is not None:
                total_bad_time += bad_duration

            bad_start_time = None
            bad_duration = 0
            alert_active = False

        # TEXT DISPLAY
        cv2.putText(image, posture, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.putText(image, f"Current Bad: {bad_duration}s", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(image, f"Total Bad: {total_bad_time}s", (50, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        # ✅ SEND DATA TO BACKEND (VERY IMPORTANT)
        try:
            requests.get(f"http://127.0.0.1:5000/update/{bad_duration}/{total_bad_time}")
            print("Sent:", bad_duration, total_bad_time)
        except:
            print("API Error")

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("Posture Detection", image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()