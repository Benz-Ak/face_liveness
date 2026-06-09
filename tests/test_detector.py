# tests/test_detector.py
import numpy as np
from src.detector import FaceDetector

detector = FaceDetector()

def test_no_crash_on_blank_frame():
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    result = detector.detect(blank)
    assert isinstance(result, list)

def test_no_crash_on_none():
    result = detector.detect(None)
    assert result == []

def test_output_format():
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    result = detector.detect(blank)
    for det in result:
        assert "bbox" in det
        assert "confidence" in det
        assert len(det["bbox"]) == 4