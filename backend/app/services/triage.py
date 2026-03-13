from __future__ import annotations

from app.schemas.report import TriageResponse


class TriageService:
    def score(self, disease: str, findings_summary: str) -> TriageResponse:
        disease_lower = disease.lower()
        base = 0.2
        if "fracture" in disease_lower:
            base = 0.8
        elif "pneumonia" in disease_lower:
            base = 0.7
        elif "effusion" in disease_lower:
            base = 0.6
        elif "nodule" in disease_lower:
            base = 0.5
        urgency_label = "routine"
        if base >= 0.75:
            urgency_label = "emergent"
        elif base >= 0.6:
            urgency_label = "urgent"
        elif base >= 0.4:
            urgency_label = "semi-urgent"
        rationale = f"Triage based on {disease} and findings: {findings_summary}."
        return TriageResponse(urgency_score=base, urgency_label=urgency_label, rationale=rationale)
