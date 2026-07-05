# src/preprocessor.py
import cv2
import torch
import numpy as np
from torchvision import transforms


class FacePreprocessor:

    def __init__(self, training=False):
        """
        training=True  : active les augmentations (entraînement uniquement)
        training=False : pipeline déterministe (inférence)
        """
        imagenet_mean = [0.485, 0.456, 0.406]
        imagenet_std  = [0.229, 0.224, 0.225]

        if training:
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.ColorJitter(brightness=0.2, contrast=0.2),
                transforms.ToTensor(),
                transforms.Normalize(imagenet_mean, imagenet_std),
            ])
        else:
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(imagenet_mean, imagenet_std),
            ])

    def crop(self, frame, bbox):
        """
        Crop face region from frame using bbox [x1, y1, x2, y2].
        Clamps coordinates to frame boundaries.
        Returns RGB np.ndarray or None if bbox is invalid.
        """
        h, w = frame.shape[:2]
        x1 = max(0, bbox[0])
        y1 = max(0, bbox[1])
        x2 = min(w, bbox[2])
        y2 = min(h, bbox[3])

        if x2 <= x1 or y2 <= y1:
            return None

        face_bgr = frame[y1:y2, x1:x2]
        face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        return face_rgb

    def process(self, frame, bbox):
        """
        Full pipeline: crop → resize → normalize → tensor.
        Input : BGR frame + bbox [x1,y1,x2,y2]
        Output: torch.FloatTensor [1, 3, 224, 224] or None
        """
        face = self.crop(frame, bbox)
        if face is None:
            return None

        tensor = self.transform(face)        # [3, 224, 224]
        return tensor.unsqueeze(0)           # [1, 3, 224, 224]