from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TriageResult:
    urgency_category: str
    priority_score: float
    recommended_review_minutes: int
    rationale: str

    def to_dict(self) -> dict:
        return {
            "urgency_category": self.urgency_category,
            "priority_score": round(self.priority_score, 3),
            "recommended_review_minutes": self.recommended_review_minutes,
            "rationale": self.rationale,
        }


class TriageEngine:
    """Reusable triage scoring engine for radiology AI workflows."""

    _disease_to_level = {
        "pneumothorax": "CRITICAL",
        "tension pneumothorax": "CRITICAL",
        "pleural effusion": "HIGH",
        "pneumonia": "MODERATE",
        "pulmonary edema": "HIGH",
        "pulmonary embolism": "CRITICAL",
        "intracranial hemorrhage": "CRITICAL",
        "stroke": "CRITICAL",
        "fracture": "MODERATE",
        "normal": "LOW",
        "no acute findings": "LOW",
    }

    _level_to_score = {
        "LOW": 0.2,
        "MODERATE": 0.5,
        "HIGH": 0.7,
        "CRITICAL": 0.9,
    }

    _level_to_review_minutes = {
        "LOW": 72 * 60,
        "MODERATE": 24 * 60,
        "HIGH": 2 * 60,
        "CRITICAL": 15,
    }

    _escalation_terms = {
        "tension",
        "massive",
        "hemorrhage",
        "hemothorax",
        "aortic",
        "rupture",
        "acute",
        "perforation",
    }

    def compute(
        self,
        findings: Iterable[str],
        disease: str,
        confidence: float,
    ) -> TriageResult:
        disease_key = disease.strip().lower()
        base_level = self._disease_to_level.get(disease_key, "MODERATE")
        base_score = self._level_to_score[base_level]

        findings_text = " ".join([f.lower() for f in findings])
        escalation_hit = any(term in findings_text for term in self._escalation_terms)
        if escalation_hit and base_level in {"LOW", "MODERATE"}:
            base_level = "HIGH"
            base_score = self._level_to_score[base_level]

        if confidence >= 0.85:
            base_score += 0.05
        elif confidence < 0.5:
            base_score -= 0.1

        base_score = max(0.0, min(1.0, base_score))

        # Recompute level from score if needed for consistency
        if base_score >= 0.85:
            urgency = "CRITICAL"
        elif base_score >= 0.65:
            urgency = "HIGH"
        elif base_score >= 0.4:
            urgency = "MODERATE"
        else:
            urgency = "LOW"

        review_minutes = self._level_to_review_minutes[urgency]
        rationale = (
            f"Triage based on disease='{disease}', confidence={confidence:.2f}, "
            f"findings={list(findings)}."
        )

        return TriageResult(
            urgency_category=urgency,
            priority_score=base_score,
            recommended_review_minutes=review_minutes,
            rationale=rationale,
        )


def triage_to_json(findings: Iterable[str], disease: str, confidence: float) -> dict:
    engine = TriageEngine()
    return engine.compute(findings=findings, disease=disease, confidence=confidence).to_dict()


if __name__ == "__main__":
    example = triage_to_json(
        findings=["cardiomegaly", "pleural effusion"],
        disease="Pleural Effusion",
        confidence=0.91,
    )
    print(example)
