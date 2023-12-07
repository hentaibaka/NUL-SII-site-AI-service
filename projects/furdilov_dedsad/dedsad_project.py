import time
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from av import VideoFrame
import os

ROOT = os.path.dirname(__file__)


class DedSad:
    _COLORS = {"blue": (255, 0, 0), "green": (0, 255, 0),
               "red": (0, 0, 255), "white": (255, 255, 255)}
    _model = YOLO(os.path.join(ROOT, 'yolov8n.pt'), task='detect')
    _names = _model.names

    @staticmethod
    def draw_polylines(polylines, classes, scores, frame, color):
        for polyline, cls, score in zip(polylines, classes, scores):
            label = f"{cls}: {round(float(score), 2)}"
            cv2.polylines(frame, [np.array(polyline, dtype=np.int32)], True, color, 2)
            cv2.putText(frame, label, np.array(polyline[0], dtype=np.int32), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        return frame

    @staticmethod
    def boxes_to_polylines(boxes):
        polylines = []
        for box in boxes:
            if not type(box) == list:
                box = box.tolist()[0]
            polyline = [[box[0], box[1]],
                        [box[0], box[3]],
                        [box[2], box[3]],
                        [box[2], box[1]]]
            polylines.append(polyline)
        return polylines

    @staticmethod
    def draw_boxes(boxes, classes, scores, frame, color):
        polylines = DedSad.boxes_to_polylines(boxes)
        frame = DedSad.draw_polylines(polylines, classes, scores, frame, color)
        return frame

    @staticmethod
    def detect(frame, classes=None):
        start = time.time()

        results = DedSad._model.predict(frame, save=False, classes=classes, conf=0.55)

        names = results[0].names
        boxes = results[0].boxes
        classes = results[0].boxes.cls
        confidences = results[0].boxes.conf

        boxes = [box.xyxy.to(torch.int32) for box in boxes]
        classes = [names[int(cls)] for cls in classes]

        end = time.time()

        return end - start, boxes, classes, confidences
    
    @staticmethod
    async def run(frame, **kwargs):
        img = frame.to_ndarray(format="bgr24")
        time, boxes, classes, confidences = DedSad.detect(img)

        img = DedSad.draw_boxes(boxes, classes, confidences, img, DedSad._COLORS['green'])
        
        cv2.putText(img, f'{round(1 / time, 1)} FPS, {round(time * 1000)} ms per frame', (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, DedSad._COLORS['white'], 1)
        
        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame

