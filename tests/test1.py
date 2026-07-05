import torch
import cv2

from src.detector import FaceDetector
from src.preprocessor import FacePreprocessor
from src.classifier import LivenessClassifier

detector = FaceDetector()
prep = FacePreprocessor(False)
clf = LivenessClassifier("models/best_checkpoint_v2.pth")

frame = cv2.imread("data/real.jpg")

detections = detector.detect(frame)

print(detections)

bbox = detections[0]["bbox"]

tensor = prep.process(frame, bbox)

with torch.no_grad():
    logits = clf.model(tensor.to(clf.device))
    probs = torch.softmax(logits,1)[0]

print("bbox :", bbox)
print("logits :", logits.cpu())
print("prob :", probs.cpu())
print("prediction :", probs.argmax().item())
import os

print(os.path.getsize("models/best_checkpoint_v2.pth"))