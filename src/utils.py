# src/utils.py
import numpy as np
import cv2


# ─── Bounding Box ─────────────────────────────────────────────────────────────

def compute_iou(boxA, boxB):
    """
    Compute Intersection over Union between two bounding boxes.
    Format: [x1, y1, x2, y2]
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter = max(0, xB - xA) * max(0, yB - yA)
    if inter == 0:
        return 0.0

    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return inter / float(areaA + areaB - inter)


# ─── Classification Metrics ───────────────────────────────────────────────────

def compute_metrics(y_true, y_pred, pos_label=1):
    """
    Compute Precision, Recall, F1 for binary classification.
    pos_label: the class considered as 'positive' (default: 1 = Real)
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    TP = np.sum((y_pred == pos_label) & (y_true == pos_label))
    FP = np.sum((y_pred == pos_label) & (y_true != pos_label))
    FN = np.sum((y_pred != pos_label) & (y_true == pos_label))

    precision = TP / (TP + FP + 1e-8)
    recall    = TP / (TP + FN + 1e-8)
    f1        = 2 * precision * recall / (precision + recall + 1e-8)

    return {"precision": precision, "recall": recall, "f1": f1}


def compute_hter(y_true, y_pred):
    """
    Half Total Error Rate = (FAR + FRR) / 2
    FAR: spoof accepted as real  (False Acceptance Rate)
    FRR: real rejected as spoof  (False Rejection Rate)
    Labels: 1 = Real, 0 = Spoof
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    spoof_mask = (y_true == 0)
    real_mask  = (y_true == 1)

    FAR = np.sum((y_pred == 1) & spoof_mask) / (np.sum(spoof_mask) + 1e-8)
    FRR = np.sum((y_pred == 0) & real_mask)  / (np.sum(real_mask)  + 1e-8)

    return {"FAR": FAR, "FRR": FRR, "HTER": (FAR + FRR) / 2}


# ─── Visualization ────────────────────────────────────────────────────────────

def draw_prediction(frame, bbox, label, confidence):
    """
    Draw bounding box + label on frame.
    bbox: [x1, y1, x2, y2]
    label: 'Real' or 'Spoof'
    """
    color = (0, 200, 0) if label == "Real" else (0, 0, 220)
    x1, y1, x2, y2 = [int(v) for v in bbox]

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    text = f"{label}: {confidence:.2f}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
    cv2.putText(frame, text, (x1 + 3, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return frame# src/utils.py
import numpy as np
import cv2


# ─── Bounding Box ─────────────────────────────────────────────────────────────

def compute_iou(boxA, boxB):
    """
    Compute Intersection over Union between two bounding boxes.
    Format: [x1, y1, x2, y2]
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter = max(0, xB - xA) * max(0, yB - yA)
    if inter == 0:
        return 0.0

    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return inter / float(areaA + areaB - inter)


# ─── Classification Metrics ───────────────────────────────────────────────────

def compute_metrics(y_true, y_pred, pos_label=1):
    """
    Compute Precision, Recall, F1 for binary classification.
    pos_label: the class considered as 'positive' (default: 1 = Real)
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    TP = np.sum((y_pred == pos_label) & (y_true == pos_label))
    FP = np.sum((y_pred == pos_label) & (y_true != pos_label))
    FN = np.sum((y_pred != pos_label) & (y_true == pos_label))

    precision = TP / (TP + FP + 1e-8)
    recall    = TP / (TP + FN + 1e-8)
    f1        = 2 * precision * recall / (precision + recall + 1e-8)

    return {"precision": precision, "recall": recall, "f1": f1}


def compute_hter(y_true, y_pred):
    """
    Half Total Error Rate = (FAR + FRR) / 2
    FAR: spoof accepted as real  (False Acceptance Rate)
    FRR: real rejected as spoof  (False Rejection Rate)
    Labels: 1 = Real, 0 = Spoof
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    spoof_mask = (y_true == 0)
    real_mask  = (y_true == 1)

    FAR = np.sum((y_pred == 1) & spoof_mask) / (np.sum(spoof_mask) + 1e-8)
    FRR = np.sum((y_pred == 0) & real_mask)  / (np.sum(real_mask)  + 1e-8)

    return {"FAR": FAR, "FRR": FRR, "HTER": (FAR + FRR) / 2}


# ─── Visualization ────────────────────────────────────────────────────────────

def draw_prediction(frame, bbox, label, confidence):
    """
    Draw bounding box + label on frame.
    bbox: [x1, y1, x2, y2]
    label: 'Real' or 'Spoof'
    """
    color = (0, 200, 0) if label == "Real" else (0, 0, 220)
    x1, y1, x2, y2 = [int(v) for v in bbox]

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    text = f"{label}: {confidence:.2f}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
    cv2.putText(frame, text, (x1 + 3, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return frame