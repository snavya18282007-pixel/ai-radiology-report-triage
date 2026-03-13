from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.db import Report, ReportResult
from app.repositories.report_repo import ReportRepository
from app.schemas.api import (
    AnalyzeReportRequest,
    AnalyzeReportResponse,
    DashboardStatsAPIResponse,
    NotifyPatientRequest,
    NotifyPatientResponse,
    TriageCaseItem,
    TriageQueueResponse,
    UploadReportResponse,
)
from app.schemas.report import ReportProcessResponse
from app.services.dashboard import DashboardService
from app.services.notification import NotificationService
from app.services.report_ingest import ingest_report
from app.services.report_pipeline import ReportPipelineService
from app.services.triage_engine import TriageEngine
from app.utils.errors import BadRequestError, NotFoundError

router = APIRouter(tags=["api"])


@router.post("/upload-report", response_model=UploadReportResponse)
async def upload_report(
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
):
    raw_text, source_type = await ingest_report(text, file)
    repo = ReportRepository(db)
    report = await repo.create_report(source_type=source_type, raw_text=raw_text)
    return UploadReportResponse(report_id=report.id, source_type=report.source_type, created_at=report.created_at)


@router.post("/analyze-report", response_model=AnalyzeReportResponse)
async def analyze_report(payload: AnalyzeReportRequest, db: AsyncSession = Depends(get_db)):
    if not payload.text and not payload.report_id:
        raise BadRequestError("Provide report_id or text to analyze.")

    repo = ReportRepository(db)
    if payload.report_id:
        report = await repo.get_report(payload.report_id)
        if not report:
            raise NotFoundError("Report not found")
        text = report.raw_text
        report_id = report.id
    else:
        raw_text = (payload.text or "").strip()
        if not raw_text:
            raise BadRequestError("Provided text is empty.")
        report = await repo.create_report(source_type="text", raw_text=raw_text)
        text = report.raw_text
        report_id = report.id

    pipeline = ReportPipelineService()
    analysis = pipeline.process(report_id, text)

    payload_result = {
        "findings": analysis.findings.model_dump(),
        "classification": analysis.classification.model_dump(),
        "triage": analysis.triage.model_dump(),
        "explainability": analysis.explainability.model_dump(),
        "inconsistencies": analysis.inconsistencies.model_dump(),
        "lifestyle": analysis.lifestyle.model_dump(),
        "follow_up": analysis.follow_up.model_dump(),
        "notification": analysis.notification.model_dump(),
    }
    await repo.create_result(report_id, payload_result)

    return AnalyzeReportResponse(report=analysis)


@router.get("/triage-cases", response_model=TriageQueueResponse)
async def triage_cases(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ReportResult, Report)
            .join(Report, ReportResult.report_id == Report.id)
            .order_by(ReportResult.created_at.desc())
        )
        rows = result.all()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load triage cases",
        ) from exc
    engine = TriageEngine()

    cases: list[TriageCaseItem] = []
    for report_result, report in rows:
        classification = report_result.classification
        findings = report_result.findings.get("entities", [])
        finding_labels = [f.get("label") for f in findings if isinstance(f, dict) and f.get("label")]
        triage = engine.compute(
            findings=finding_labels,
            disease=classification.get("disease", "unknown"),
            confidence=float(classification.get("confidence", 0.0)),
        )
        cases.append(
            TriageCaseItem(
                report_id=report.id,
                disease=classification.get("disease", "unknown"),
                confidence=float(classification.get("confidence", 0.0)),
                urgency_category=triage.urgency_category,
                priority_score=triage.priority_score,
                recommended_review_minutes=triage.recommended_review_minutes,
                created_at=report_result.created_at,
            )
        )

    cases.sort(key=lambda c: c.priority_score, reverse=True)
    return TriageQueueResponse(cases=cases)


@router.get("/dashboard-stats", response_model=DashboardStatsAPIResponse)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    stats = await DashboardService(db).get_stats()
    return DashboardStatsAPIResponse(stats=stats, generated_at=datetime.now(timezone.utc))


@router.post("/notify-patient", response_model=NotifyPatientResponse)
async def notify_patient(payload: NotifyPatientRequest, db: AsyncSession = Depends(get_db)):
    repo = ReportRepository(db)
    report = await repo.get_report(payload.report_id)
    if not report:
        raise NotFoundError("Report not found")

    result = await repo.get_result(payload.report_id)
    if not result:
        pipeline = ReportPipelineService()
        analysis = pipeline.process(report.id, report.raw_text)
        payload_result = {
            "findings": analysis.findings.model_dump(),
            "classification": analysis.classification.model_dump(),
            "triage": analysis.triage.model_dump(),
            "explainability": analysis.explainability.model_dump(),
            "inconsistencies": analysis.inconsistencies.model_dump(),
            "lifestyle": analysis.lifestyle.model_dump(),
            "follow_up": analysis.follow_up.model_dump(),
            "notification": analysis.notification.model_dump(),
        }
        await repo.create_result(report.id, payload_result)
        triage_data = analysis.triage
    else:
        triage_data = ReportProcessResponse(
            report_id=report.id,
            processed_at=result.created_at,
            findings=result.findings,
            classification=result.classification,
            triage=result.triage,
            explainability=result.explainability,
            inconsistencies=result.inconsistencies,
            lifestyle=result.lifestyle,
            follow_up=result.follow_up,
            notification=result.notification,
        ).triage

    notification_service = NotificationService()
    notification = notification_service.trigger(triage_data)

    if payload.channels:
        notification.channels = payload.channels

    return NotifyPatientResponse(report_id=report.id, notification=notification)
