from __future__ import annotations

from app.schemas.report import ExplainabilityResponse
from app.services.ai_model_service import AIModelService


class ExplainabilityService:
    def __init__(self, model_service: AIModelService) -> None:
        self.model_service = model_service

    def build(self, text: str, evidence: list[str]) -> ExplainabilityResponse:
        model_insights = self.model_service.explain(text)
        return ExplainabilityResponse(evidence=evidence, model_insights=model_insights)
