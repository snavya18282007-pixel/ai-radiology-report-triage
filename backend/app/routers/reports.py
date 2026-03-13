from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.report_repo import ReportRepository
from app.schemas.report import (
    ReportDetailResponse,
    ReportProcessResponse,
    ReportUploadResponse,
)
from app.services.report_ingest import ingest_report
from app.services.report_pipeline import ReportPipelineService
from app.utils.errors import NotFoundError

router = APIRouter(prefix="/v1/reports", tags=["reports"])


@router.post("/upload", response_model=ReportUploadResponse)
async def upload_report(
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
):
    raw_text, source_type = await ingest_report(text, file)
    repo = ReportRepository(db)
    report = await repo.create_report(source_type=source_type, raw_text=raw_text)
    return ReportUploadResponse(report_id=report.id, source_type=report.source_type, created_at=report.created_at)


@router.post("/{report_id}/process", response_model=ReportProcessResponse)
async def process_report(report_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ReportRepository(db)
    report = await repo.get_report(report_id)
    if not report:
        raise NotFoundError("Report not found")

    pipeline = ReportPipelineService()
    response = pipeline.process(report_id, report.raw_text)

    payload = {
        "findings": response.findings.model_dump(),
        "classification": response.classification.model_dump(),
        "triage": response.triage.model_dump(),
        "explainability": response.explainability.model_dump(),
        "inconsistencies": response.inconsistencies.model_dump(),
        "lifestyle": response.lifestyle.model_dump(),
        "follow_up": response.follow_up.model_dump(),
        "notification": response.notification.model_dump(),
    }
    await repo.create_result(report_id, payload)
    return response


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report(report_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ReportRepository(db)
    report = await repo.get_report(report_id)
    if not report:
        raise NotFoundError("Report not found")
    result = await repo.get_result(report_id)
    return ReportDetailResponse(
        report_id=report.id,
        source_type=report.source_type,
        raw_text=report.raw_text,
        created_at=report.created_at,
        result=(
            ReportProcessResponse(
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
            )
            if result
            else None
        ),
    )
