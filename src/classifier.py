# src/classifier.py
import torch
import torch.nn as nn
from torchvision import models


class LivenessClassifier:

    LABELS = {0: "Spoof", 1: "Real"}

    def __init__(self, weights_path=None, device=None, threshold=0.5):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = device
        self.threshold = threshold
        self.model = self._build_model().to(device)

        if weights_path:
            self.load_weights(weights_path)

        self.model.eval()

    def _build_model(self):
        """
        MobileNetV2 avec tête de classification custom.
        Phase 1 : backbone gelé, seule la tête est entraînée.
        Phase 2 : derniers 3 blocs dégelés (voir notebooks/02_train.ipynb).
        """
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

        # Gèle tout le backbone
        for param in model.parameters():
            param.requires_grad = False

        # Remplace la tête classifier
        in_features = model.classifier[1].in_features  # 1280
        model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 2)       # 2 classes : Real / Spoof
        )

        return model

    
    def predict(self, tensor):
        """
        Input : torch.FloatTensor [1, 3, 224, 224]
        Output: dict {label, confidence, raw_scores}
        """
        if tensor is None:
            return None

        tensor = tensor.to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)                     # [1, 2]
            probs  = torch.softmax(logits, dim=1)[0]        # [2]

        spoof_prob = probs[0].item()
        real_prob  = probs[1].item()

        # Choix de la classe dominante (0=Spoof, 1=Real)
        if real_prob >= self.threshold:
            label = "Real"
            confidence = real_prob
        else:
            label = "Spoof"
            confidence = spoof_prob

        return {
            "label":      label,
            "confidence": float(confidence),
            "raw_scores": [spoof_prob, real_prob]  # [P(spoof), P(real)]
        }


    def load_weights(self, path):
        state = torch.load(path, map_location=self.device)
        self.model.load_state_dict(state)
        print(f"Weights loaded from {path}")

    def save_weights(self, path):
        torch.save(self.model.state_dict(), path)
        print(f"Weights saved to {path}")

    def unfreeze_top_blocks(self, n=3):
        """
        Dégèle les n derniers InvertedResidual blocks du backbone.
        À appeler au début de la Phase 2 d'entraînement.
        """
        blocks = list(self.model.features.children())
        for block in blocks[-n:]:
            for param in block.parameters():
                param.requires_grad = True