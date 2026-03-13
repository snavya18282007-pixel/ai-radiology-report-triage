from __future__ import annotations

from app.services.ai_model_service import AIModelService
from app.schemas.report import FindingItem, FindingsResponse


class NLPExtractionService:
    def __init__(self, model_service: AIModelService) -> None:
        self.model_service = model_service

    def extract(self, text: str) -> FindingsResponse:
        findings = self.model_service.extract_findings(text)
        items = [FindingItem(label=f.label, confidence=f.confidence, evidence=f.evidence) for f in findings]
        summary = "; ".join({item.label for item in items})
        return FindingsResponse(entities=items, summary=summary)
