# src/preprocessor.py

import cv2
import torch
import numpy as np
from torchvision import transforms


class FacePreprocessor:

    def __init__(self, training=False, padding_factor=0.20):
        """
        training=True  : active les augmentations (entraînement)
        training=False : pipeline déterministe (inférence)

        padding_factor :
            0.0  -> crop exact
            0.2  -> ajoute 20% de contexte autour du visage
        """

        self.padding_factor = padding_factor

        imagenet_mean = [0.485, 0.456, 0.406]
        imagenet_std = [0.229, 0.224, 0.225]

        if training:
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.ColorJitter(
                    brightness=0.2,
                    contrast=0.2
                ),
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
        Crop du visage avec un léger padding.
        """

        h, w = frame.shape[:2]

        x1, y1, x2, y2 = bbox

        bw = x2 - x1
        bh = y2 - y1

        pad_x = int(bw * self.padding_factor)
        pad_y = int(bh * self.padding_factor)

        x1 = max(0, x1 - pad_x)
        y1 = max(0, y1 - pad_y)
        x2 = min(w, x2 + pad_x)
        y2 = min(h, y2 + pad_y)

        if x2 <= x1 or y2 <= y1:
            return None

        face_bgr = frame[y1:y2, x1:x2]
        face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)

        return face_rgb

    def process(self, frame, bbox):
        """
        Pipeline complet :
            crop
            -> sauvegarde debug
            -> resize
            -> normalisation
            -> tensor
        """

        face = self.crop(frame, bbox)

        if face is None:
            return None

        # ==========================================================
        # IMAGE EXACTEMENT ENVOYÉE AU MODÈLE
        # ==========================================================
        cv2.imwrite(
            "debug_crop.jpg",
            cv2.cvtColor(face, cv2.COLOR_RGB2BGR)
        )

        tensor = self.transform(face)

        print("Tensor shape :", tensor.unsqueeze(0).shape)
        print("Tensor min :", tensor.min().item())
        print("Tensor max :", tensor.max().item())

        return tensor.unsqueeze(0)