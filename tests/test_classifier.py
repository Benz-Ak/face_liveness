# tests/test_classifier.py
import torch
from src.classifier import LivenessClassifier

clf = LivenessClassifier()

def test_predict_output_keys():
    tensor = torch.randn(1, 3, 224, 224)
    result = clf.predict(tensor)
    assert "label" in result
    assert "confidence" in result
    assert "raw_scores" in result

def test_predict_label_values():
    tensor = torch.randn(1, 3, 224, 224)
    result = clf.predict(tensor)
    assert result["label"] in ("Real", "Spoof")

def test_predict_confidence_range():
    tensor = torch.randn(1, 3, 224, 224)
    result = clf.predict(tensor)
    assert 0.0 <= result["confidence"] <= 1.0

def test_predict_none_returns_none():
    assert clf.predict(None) is None

def test_scores_sum_to_one():
    tensor = torch.randn(1, 3, 224, 224)
    result = clf.predict(tensor)
    total = sum(result["raw_scores"])
    assert abs(total - 1.0) < 1e-5