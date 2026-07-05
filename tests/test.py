import torch
import cv2

from src.classifier import LivenessClassifier
from src.preprocessor import FacePreprocessor

clf = LivenessClassifier(weights_path="models/best_checkpoint_v2.pth")
prep = FacePreprocessor(training=False)

frame = cv2.imread("data/real.jpg")

if frame is None:
    print("Image introuvable")
    exit()

tensor = prep.process(frame, [0, 0, frame.shape[1], frame.shape[0]])

with torch.no_grad():
    logits = clf.model(tensor.to(clf.device))
    probs = torch.softmax(logits, dim=1)[0]
    pred = probs.argmax().item()

print("Logits :", logits.cpu())
print("Probabilités :", probs.cpu())
print("Classe prédite :", pred)
print(f"P(index 0) = {probs[0].item():.6f}")
print(f"P(index 1) = {probs[1].item():.6f}")
print("Labels du pipeline :", clf.LABELS)

print("Verdict :", clf.LABELS[pred])