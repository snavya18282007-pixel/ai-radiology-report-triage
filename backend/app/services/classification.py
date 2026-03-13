from __future__ import annotations

from app.schemas.report import ClassificationResponse
from app.services.ai_model_service import AIModelService


class DiseaseClassificationService:
    def __init__(self, model_service: AIModelService) -> None:
        self.model_service = model_service
        self.labels = [
            "lung nodule",
            "pneumonia",
            "pleural effusion",
            "fracture",
            "normal",
        ]

    def classify(self, text: str) -> ClassificationResponse:
        scores = self.model_service.classify_disease(text, self.labels)
        disease = max(scores, key=scores.get)
        confidence = float(scores[disease])
        return ClassificationResponse(disease=disease, confidence=confidence, probabilities=scores)
