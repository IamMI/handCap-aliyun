# HandCapture on aliyun

This code works for *Embedded Competition*, which would run on **aliyun platform**.

| **基本思路** | **涉及模型** | **日期** | **创建者** |
| --- | --- | --- | --- |
| 对手部图片使用Mediapipe提取关节点，最后使用SVC预测手势类别 | MediaPipe、 SVC | 2025.7.1 | 黄佳溢，吕展航，尤智宣 |

## Procedure  
We use **MediaPipe** + **LinearSVC** to classify.  
More information about them, please visit  

- [MediaPipe](https://chuoling.github.io/mediapipe/solutions/hands.html) 
- [LinearSVC](https://wiki.sipeed.com/maixpy/doc/zh/vision/hand_gesture_classification.html)


## Build Dependencies
- opencv-python
- mediapipe
- numpy
- asyncio
- websockets


## Notes
At our testing, we found that your palm should face to camera view. Otherwise the accuracy would be bad.

