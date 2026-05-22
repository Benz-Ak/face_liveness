# tests/test_utils.py
from src.utils import compute_iou, compute_metrics, compute_hter

def test_iou_perfect_overlap():
    box = [0, 0, 10, 10]
    assert compute_iou(box, box) == 1.0

def test_iou_no_overlap():
    assert compute_iou([0,0,5,5], [10,10,20,20]) == 0.0

def test_metrics_perfect():
    m = compute_metrics([1,1,0,0], [1,1,0,0])
    assert round(m["f1"], 2) == 1.0

def test_hter_perfect():
    h = compute_hter([1,1,0,0], [1,1,0,0])
    assert h["HTER"] < 0.01