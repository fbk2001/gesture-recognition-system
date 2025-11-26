import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75)

cap = cv2.VideoCapture(0)
while True:
    ret,frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 因为摄像头是镜像的，所以将摄像头水平翻转
    # 不是镜像的可以不翻转
    frame= cv2.flip(frame,1)
    results = hands.process(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    if results.multi_handedness:
        for hand_label in results.multi_handedness:
            print(hand_label)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        print('hand_landmarks:' + str(hand_landmarks))
        # 关键点可视化
        mp_drawing.draw_landmarks(
            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    cv2.imshow('MediaPipe Hands', frame)
    # 按下'ESC'或关闭窗口退出
    if cv2.waitKey(1) & 0xFF == 27 or cv2.getWindowProperty('MediaPipe Hands', cv2.WND_PROP_VISIBLE) < 1:
        break
cap.release()
