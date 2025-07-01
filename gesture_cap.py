"""
Code frame of Mediapipe+LinearSVC
- About Mediapipe
    Please visit https://chuoling.github.io/mediapipe/solutions/hands.html for more info
- About LinearSVC
    Please visit https://wiki.sipeed.com/maixpy/doc/zh/vision/hand_gesture_classification.html for more info
"""

import cv2
import mediapipe as mp
from LinearSVC import LinearSVC, LinearSVCManager
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


IMAGE_FILES = [f"imgs/img{i}.jpg" for i in range(23, 32)]

# 1. use mediapipe to predict keypoints
images_list = []
with mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5) as hands:
    for idx, file in enumerate(IMAGE_FILES):
        # Read an image, flip it around y-axis for correct handedness output (see
        # above).
        image = cv2.flip(cv2.imread(file), 1)
        # Convert the BGR image to RGB before processing.
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Print handedness and draw hand landmarks on the image.
        print('Handedness:', results.multi_handedness)
        if not results.multi_hand_landmarks:
            continue
        image_height, image_width, _ = image.shape
        annotated_image = image.copy()
        
        hand_list = []
        for id, (hand_landmarks, label) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):        
            single_hand = []
            for lm in hand_landmarks.landmark:
                single_hand.append([lm.x, lm.y, lm.z])

            hand_list.append({
                "id": id,
                "left_or_right": label.classification[0].label,
                "keypoints": single_hand
            })
        
        images_list.append({
            "file": file,
            "number_of_hands": len(hand_list),
            "hand_list": hand_list,
        })

# 2. use LinearSVC to recognize gesture
def preprocess(hand_landmarks, is_left=False, boundary=(1,1,1)):
    hand_landmarks = np.array(hand_landmarks).reshape((21, -1))
    vector = hand_landmarks[:,:2]
    vector = vector[1:] - vector[0]
    vector = vector.astype('float64') / boundary[:vector.shape[1]]
    if not is_left: # mirror
        vector[:,0] *= -1
    return vector

name_classes = ("one", "five", "fist", "ok", "heartSingle", "yearh", "three", "four", "six", "Iloveyou", "gun", "thumbUp", "nine", "pink")

npzfile = np.load("trainSets.npz")
X_train = npzfile["X"]
y_train = npzfile["y"]

clfm = LinearSVCManager(LinearSVC.load("clf_dump.npz"), X_train, y_train, pretrained=True)

for images_info in images_list:
    for hand_info in images_info['hand_list']:
        hand_landmarks_points = hand_info['keypoints']
        hand_landmarks = preprocess(hand_landmarks_points, is_left=False, boundary=(1, 1, 1))
        features = np.array([hand_landmarks.flatten()])

        class_idx, pred_conf = clfm.test(features)
        class_idx, pred_conf = class_idx[0], pred_conf[0]  
        
        print("")
        print(f"Images-Name: {images_info['file']}, Hands id: {hand_info['id']}")
        print(f"Predicted gesture: {name_classes[class_idx]}, Confidence: {pred_conf * 100:.2f}%")