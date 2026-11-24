import os
import cv2
import numpy as np
from ultralytics import YOLO

BASE = os.path.join(os.path.dirname(__file__), "models")
model_bola = YOLO(os.path.join(BASE, "rgb_openvino_model"), task="detect")
model_kotak = YOLO(os.path.join(BASE, "best_openvino_model"), task="detect")

# (model, {class name in model: object name used by main.py}, minimum confidence)
SUMBER = [
    (model_bola,  {"bola_merah": "merah", "bola_hijau": "hijau"}, 0.5),
    (model_kotak, {"blue_box": "biru"}, 0.5),   # green_box is not listed, so it's ignored
]


def deteksi_yolo(frame):
    hasil = {}
    for model, peta, conf in SUMBER:
        r = model.predict(frame, imgsz=640, conf=conf, verbose=False)[0]
        for box in r.boxes:
            nama = peta.get(model.names[int(box.cls)])
            if nama is None:
                continue
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()
            k = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
                         dtype=np.int32).reshape(-1, 1, 2)
            # keep only the largest box per object
            if nama not in hasil or cv2.contourArea(k) > cv2.contourArea(hasil[nama]):
                hasil[nama] = k
    return hasil, None