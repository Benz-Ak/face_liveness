# tests/test_preprocessor.py
import numpy as np
import torch
from src.preprocessor import FacePreprocessor

prep = FacePreprocessor(training=False)
frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

def test_output_shape():
    tensor = prep.process(frame, [100, 100, 300, 300])
    assert tensor.shape == (1, 3, 224, 224)

def test_output_dtype():
    tensor = prep.process(frame, [100, 100, 300, 300])
    assert tensor.dtype == torch.float32

def test_invalid_bbox_returns_none():
    result = prep.process(frame, [300, 300, 100, 100])
    assert result is None

def test_out_of_bounds_bbox():
    tensor = prep.process(frame, [-50, -50, 800, 800])
    assert tensor.shape == (1, 3, 224, 224)