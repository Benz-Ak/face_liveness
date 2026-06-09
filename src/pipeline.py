# src/pipeline.py
import time
import cv2
import numpy as np
from src.detector import FaceDetector
from src.preprocessor import FacePreprocessor
from src.classifier import LivenessClassifier
from src.utils import draw_prediction


class LivenessPipeline:

    def __init__(self, weights_path=None, threshold=0.5, device=None):
        self.detector     = FaceDetector(device=device)
        self.preprocessor = FacePreprocessor(training=False)
        self.classifier   = LivenessClassifier(
            weights_path=weights_path,
            threshold=threshold,
            device=device
        )

    def run(self, frame):
        """
        Pipeline complet sur un seul frame.
        Input : np.ndarray BGR (H, W, 3)
        Output: dict {results, annotated_frame, latency}
        """
        latency = {}

        # Stage 1 — Detection
        t0 = time.perf_counter()
        detections = self.detector.detect(frame)
        latency["detection_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        results = []
        annotated = frame.copy()

        for det in detections:
            bbox = det["bbox"]

            # Stage 2 — Preprocessing
            t1 = time.perf_counter()
            tensor = self.preprocessor.process(frame, bbox)
            latency["preprocess_ms"] = round((time.perf_counter() - t1) * 1000, 2)

            if tensor is None:
                continue

            # Stage 3 — Classification
            t2 = time.perf_counter()
            prediction = self.classifier.predict(tensor)
            latency["classification_ms"] = round((time.perf_counter() - t2) * 1000, 2)

            result = {
                "bbox":       bbox,
                "label":      prediction["label"],
                "confidence": prediction["confidence"],
                "raw_scores": prediction["raw_scores"],
            }
            results.append(result)

            # Stage 4 — Annotation
            annotated = draw_prediction(
                annotated,
                bbox,
                prediction["label"],
                prediction["confidence"]
            )

        latency["total_ms"] = round(sum(latency.values()), 2)

        return {
            "results":        results,
            "annotated_frame": annotated,
            "latency":        latency,
        }

    def run_image(self, image_path):
        """
        Input : chemin vers une image
        Output: dict pipeline complet
        """
        frame = cv2.imread(image_path)
        if frame is None:
            raise FileNotFoundError(f"Image non trouvée : {image_path}")
        return self.run(frame)

    def run_video(self, source=0):
        """
        source=0        : webcam
        source="path"   : fichier vidéo
        Génère les résultats frame par frame (generator).
        """
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"Impossible d'ouvrir la source vidéo : {source}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                yield self.run(frame)
        finally:
            cap.release()

    def benchmark(self, n=50):
        """
        Mesure les latences moyennes sur n frames synthétiques.
        """
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        timings = []

        for _ in range(n):
            output = self.run(blank)
            timings.append(output["latency"])

        keys = ["detection_ms", "total_ms"]
        print(f"\n{'─'*35}")
        print(f"  Benchmark ({n} frames)")
        print(f"{'─'*35}")
        for k in keys:
            vals = [t[k] for t in timings if k in t]
            if vals:
                print(f"  {k:<22} avg={np.mean(vals):.1f}ms  p95={np.percentile(vals,95):.1f}ms")
        print(f"{'─'*35}\n")