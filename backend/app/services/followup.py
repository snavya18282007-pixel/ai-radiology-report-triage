from __future__ import annotations

from app.schemas.report import FollowUpRecommendation


class FollowUpService:
    def recommend(self, disease: str) -> FollowUpRecommendation:
        disease_lower = disease.lower()
        if "fracture" in disease_lower:
            return FollowUpRecommendation(
                recommendations=["Orthopedics consultation", "Repeat imaging in 7-14 days"],
                timeframe_days=14,
            )
        if "pneumonia" in disease_lower:
            return FollowUpRecommendation(
                recommendations=["Clinical reassessment", "Repeat chest X-ray"],
                timeframe_days=30,
            )
        if "nodule" in disease_lower:
            return FollowUpRecommendation(
                recommendations=["Pulmonology referral", "Repeat chest CT"],
                timeframe_days=90,
            )
        return FollowUpRecommendation(recommendations=["Routine follow-up"], timeframe_days=180)
