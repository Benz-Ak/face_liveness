import torch
import cv2

from src.classifier import LivenessClassifier
from src.preprocessor import FacePreprocessor

clf = LivenessClassifier("models/best_checkpoint_v2.pth")
prep = FacePreprocessor(False)

frame = cv2.imread("data/Real.png")

print("Image shape :", frame.shape)

tensor = prep.process(frame, [0,0,frame.shape[1],frame.shape[0]])

print("Tensor shape :", tensor.shape)
print("Tensor min :", tensor.min().item())
print("Tensor max :", tensor.max().item())

with torch.no_grad():
    logits = clf.model(tensor.to(clf.device))
    probs = torch.softmax(logits,1)

print("Logits :", logits)
print("Softmax :", probs)
print("Prediction :", probs.argmax(1).item())