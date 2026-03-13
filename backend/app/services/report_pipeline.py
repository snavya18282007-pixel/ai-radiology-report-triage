from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.schemas.report import ReportProcessResponse
from app.services.ai_model_service import get_model_service
from app.services.classification import DiseaseClassificationService
from app.services.explainability import ExplainabilityService
from app.services.followup import FollowUpService
from app.services.inconsistency import InconsistencyService
from app.services.lifestyle import LifestyleService
from app.services.nlp_extraction import NLPExtractionService
from app.services.notification import NotificationService
from app.services.triage import TriageService


class ReportPipelineService:
    def __init__(self) -> None:
        model_service = get_model_service()
        self.extractor = NLPExtractionService(model_service)
        self.classifier = DiseaseClassificationService(model_service)
        self.triage = TriageService()
        self.explainability = ExplainabilityService(model_service)
        self.inconsistency = InconsistencyService()
        self.lifestyle = LifestyleService()
        self.followup = FollowUpService()
        self.notification = NotificationService()

    def process(self, report_id, text: str) -> ReportProcessResponse:
        logger = logging.getLogger(__name__)
        try:
            findings = self.extractor.extract(text)
            classification = self.classifier.classify(text)
            triage = self.triage.score(classification.disease, findings.summary)
            evidence = [item.evidence for item in findings.entities if item.evidence]
            explainability = self.explainability.build(text, evidence)
            inconsistencies = self.inconsistency.detect(text)
            lifestyle = self.lifestyle.recommend(classification.disease)
            follow_up = self.followup.recommend(classification.disease)
            notification = self.notification.trigger(triage)
        except Exception as exc:
            logger.exception("Report pipeline failed", exc_info=exc)
            raise RuntimeError("Report analysis failed") from exc

        return ReportProcessResponse(
            report_id=report_id,
            findings=findings,
            classification=classification,
            triage=triage,
            explainability=explainability,
            inconsistencies=inconsistencies,
            lifestyle=lifestyle,
            follow_up=follow_up,
            notification=notification,
            processed_at=datetime.now(timezone.utc),
        )
