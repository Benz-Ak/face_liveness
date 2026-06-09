# src/detector.py
import numpy as np
import torch
from facenet_pytorch import MTCNN


class FaceDetector:

    def __init__(self, min_face_size=40, thresholds=None, device=None):
        if thresholds is None:
            thresholds = [0.6, 0.7, 0.7]
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = device
        self.mtcnn = MTCNN(
            min_face_size=min_face_size,
            thresholds=thresholds,
            keep_all=True,          # detect ALL faces in frame
            device=device
        )

    def detect(self, frame):
        """
        Input : np.ndarray BGR (H, W, 3)
        Output: list of dicts — {bbox: [x1,y1,x2,y2], confidence: float}
        Never raises — returns [] if no face found.
        """
        if frame is None or frame.size == 0:
            return []

        # MTCNN expects RGB
        rgb = frame[:, :, ::-1]

        try:
            boxes, probs = self.mtcnn.detect(rgb)
        except Exception:
            return []

        if boxes is None:
            return []

        results = []
        for box, prob in zip(boxes, probs):
            if prob is None or prob < self.mtcnn.thresholds[0]:
                continue
            x1, y1, x2, y2 = [int(v) for v in box]
            results.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": float(prob)
            })

        return results