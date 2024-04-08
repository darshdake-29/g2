import cv2
import os
import numpy as np
from ultralytics import YOLO
from werkzeug.utils import secure_filename
from base import app
from base.com.vo.detection_vo import FileVO, PotholeVO, CattleVO
from base.com.dao.detection_dao import FileDAO, PotholeDAO, CattleDAO
import torch
import cvzone


class PerformDetection:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model_path = f'base/static/models/{self.model_name}.pt'
        self.model = YOLO(self.model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.model_name == 'cattle':
            self.classes = [15, 16, 17, 18, 19, 20, 21, 22, 23]
        elif self.model_name == 'pothole':
            self.classes = [1]
        else:
            self.classes = [0]

    def image_detection_service(self, file_save_path, file_output_path):
        try:
            image = cv2.imread(file_save_path)
            image = cv2.resize(image, (720, 480))
            results = self.model.predict(image, classes=self.classes,
                                    device=self.device)
            is_garbage = False
            if results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu()
                for box in boxes:
                    x1, y1, x2, y2 = box
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 100, 250), 2)
            else:
                boxes = results[0].obb.xyxyxyxy.cpu()
                for box in boxes:
                    points = np.array(box, np.int32)
                    points = points.reshape((-1, 1, 2))
                    cv2.polylines(image, [points], isClosed=True,
                                  color=(0, 100, 250), thickness=2)
            counts = len(results[0])

            if self.model_name == 'pothole':
                text = f'Pothole Counts: {counts}'
            elif self.model_name == 'cattle':
                text = f'Cattle Counts: {counts}'
            else:
                if counts > 0:
                    is_garbage = True
                text = f'Is Garbage: {is_garbage}'

            cvzone.putTextRect(image, text, [30, 40],
                               scale=1, thickness=2, colorR=(0, 0, 0),
                               colorT=(0, 100, 250), border=2,
                               colorB=(0, 100, 250),
                               font=cv2.FONT_HERSHEY_SIMPLEX)

            cv2.imwrite(file_output_path, image)
            return {'counts': counts}
        except Exception as e:
            return {'error': str(e)}

    def video_detection_service(self, file_save_path):
        pass
