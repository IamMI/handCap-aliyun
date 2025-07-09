"""
Code frame of Mediapipe+LinearSVC with stability improvements
- About Mediapipe
    Please visit https://chuoling.github.io/mediapipe/solutions/hands.html for more info
- About LinearSVC
    Please visit https://wiki.sipeed.com/maixpy/doc/zh/vision/hand_gesture_classification.html for more info
"""

import cv2
import mediapipe as mp
from LinearSVC import LinearSVC, LinearSVCManager
import numpy as np
import asyncio
import websockets
import json
import time

# 初始化 MediaPipe 手势检测模块
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.4,
    model_complexity=0
)

# WebSocket 地址（根据你的后端设置）
WS_SERVER_URI = "ws://Your server IP:Port2"
# RTMP 地址（由龙芯开发板推送来的检测流）
rtmp_url = "rtmp://Your server IP:Port1/stream1"

# 手势类别（请确保与你的模型一致）
name_classes = (
    "one", "five", "fist", "ok", "heartSingle", "yearh", "three",
    "four", "six", "Iloveyou", "gun", "thumbUp", "nine", "pink"
)

# 加载训练好的 LinearSVC 分类器和训练集
try:
    npzfile = np.load("trainSets.npz")
    X_train = npzfile["X"]
    y_train = npzfile["y"]

    clfm = LinearSVCManager(LinearSVC.load("clf_dump.npz"), X_train, y_train, pretrained=True)

    print("[INFO] 模型加载成功")

except Exception as e:
    print(f"[ERROR] 模型加载失败: {e}")
    exit(1)


def preprocess(hand_landmarks, is_left=False):
    try:
        hand_landmarks = np.array(hand_landmarks).reshape((21, -1))
        vector = hand_landmarks[:, :2]
        vector = vector[1:] - vector[0]
        vector = vector.astype('float64') / 1.0

        if not is_left:
            vector[:, 0] *= -1

        return vector
    except Exception as e:
        print(f"[ERROR] 预处理失败: {e}")
        return None


async def send_gesture_to_client(gesture_name):
    retry = 3
    for i in range(retry):
        try:
            async with websockets.connect(WS_SERVER_URI) as websocket:
                payload = {
                    "type": "gesture",
                    "data": gesture_name
                }
                await websocket.send(json.dumps(payload))
                print(f"[Gesture] 已发送手势指令: {gesture_name}")
                break
        except Exception as e:
            print(f"[Error] WebSocket 连接失败 (第{i+1}/{retry}): {e}")
            await asyncio.sleep(1)


def main():
    global hands

    cap = None
    last_frame_time = time.time()
    frame_count = 0
    fps = 0

    process_interval = 0.5  # 每 0.2 秒处理一次
    last_process_time = time.time()

    last_gesture_time = 0
    min_send_interval = 2  # 同一手势至少间隔 0.8 秒才能再次发送

    gesture_history = []
    gesture_threshold = 1  # 至少连续 3 帧一致才触发

    while True:
        cap = cv2.VideoCapture(rtmp_url)

        if cap.isOpened():
            print("[INFO] 成功连接到 RTMP 流，开始接收视频帧...")
            while True:
                ret, image = cap.read()

                if not ret:
                    print("[INFO] 读取帧失败，可能推流中断，尝试重新连接...")
                    break

                frame_count += 1
                current_time = time.time()
                elapsed_time = current_time - last_frame_time

                if elapsed_time >= 1:
                    fps = frame_count / elapsed_time
                    print(f"[DEBUG] 当前 FPS: {fps:.2f}")
                    frame_count = 0
                    last_frame_time = current_time

                # 图像缩放统一尺寸
                image = cv2.resize(image, (640, 480))

                # 控制检测频率
                if current_time - last_process_time < process_interval:
                    continue
                last_process_time = current_time

                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(image_rgb)

                if results.multi_hand_landmarks:
                    for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        single_hand_keypoints = []
                        for lm in hand_landmarks.landmark:
                            single_hand_keypoints.append([lm.x, lm.y, lm.z])

                        is_left = False
                        if results.multi_handedness and idx < len(results.multi_handedness):
                            handedness = results.multi_handedness[idx]
                            label = handedness.classification[0].label
                            is_left = (label == 'Left')

                        processed_vector = preprocess(single_hand_keypoints, is_left=is_left)
                        if processed_vector is None:
                            continue

                        features = np.array([processed_vector.flatten()])
                        class_idx, pred_conf = clfm.test(features)

                        if pred_conf.ndim > 0:
                            pred_conf = pred_conf[0]
                        if class_idx.ndim > 0:
                            class_idx = class_idx[0]

                        if pred_conf > 0.7:
                            gesture_name = name_classes[class_idx]
                            gesture_history.append(gesture_name)

                            if len(gesture_history) > gesture_threshold:
                                gesture_history.pop(0)

                            if len(gesture_history) >= gesture_threshold and all(g == gesture_name for g in gesture_history[-gesture_threshold:]):
                                if  (current_time - last_gesture_time) > min_send_interval:
                                    print(f"[Gesture] 识别到手势: {gesture_name} (置信度: {pred_conf:.2f})")
                                    asyncio.run(send_gesture_to_client(gesture_name))
                                    last_gesture_time = current_time

                else:
                    gesture_history.clear()  # 清空历史记录，防止误判

        else:
            print(f"[INFO] 尚未检测到 RTMP 流，{5} 秒后重试...")
            if cap:
                cap.release()
            time.sleep(5)

        if cap:
            cap.release()


if __name__ == "__main__":
    main()