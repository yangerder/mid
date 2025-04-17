from imutils import face_utils
from scipy.spatial import distance as dist
import numpy as np
import imutils
import dlib
import cv2

# EAR 計算函數
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])  # vertical
    B = dist.euclidean(eye[2], eye[4])  # vertical
    C = dist.euclidean(eye[0], eye[3])  # horizontal
    ear = (A + B) / (2.0 * C)
    return ear

# 設定 EAR 閾值與偵測結果提示
EAR_THRESHOLD = 0.21

# 載入模型
predictor_path = "model/shape_predictor_68_face_landmarks.dat"
image_path = "img.png"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

# 載入圖片與前處理
image = cv2.imread(image_path)
image = imutils.resize(image, width=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 偵測人臉
rects = detector(gray, 1)

for (i, rect) in enumerate(rects):
    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)

    # 抓取眼睛的關鍵點 (左眼: 42~47, 右眼: 36~41)
    leftEye = shape[42:48]
    rightEye = shape[36:42]

    # 計算 EAR
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0

    # 畫眼睛輪廓
    cv2.drawContours(image, [cv2.convexHull(leftEye)], -1, (0, 255, 0), 1)
    cv2.drawContours(image, [cv2.convexHull(rightEye)], -1, (0, 255, 0), 1)

    # 顯示 EAR 值
    cv2.putText(image, f"EAR: {ear:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 疲勞警告
    if ear < EAR_THRESHOLD:
        cv2.putText(image, "Drowsiness Detected!", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

# 顯示結果
cv2.imshow("Drowsiness Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
