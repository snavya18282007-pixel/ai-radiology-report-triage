from __future__ import annotations

import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Report, ReportResult

logger = logging.getLogger(__name__)


class ReportRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_report(self, source_type: str, raw_text: str) -> Report:
        try:
            report = Report(source_type=source_type, raw_text=raw_text)
            self.db.add(report)
            await self.db.commit()
            await self.db.refresh(report)
            return report
        except Exception as exc:
            await self.db.rollback()
            logger.exception("Failed to create report", exc_info=exc)
            raise

    async def get_report(self, report_id: uuid.UUID) -> Report | None:
        try:
            result = await self.db.execute(select(Report).where(Report.id == report_id))
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.exception("Failed to fetch report", exc_info=exc)
            raise

    async def create_result(self, report_id: uuid.UUID, payload: dict) -> ReportResult:
        try:
            result = ReportResult(report_id=report_id, **payload)
            self.db.add(result)
            await self.db.commit()
            await self.db.refresh(result)
            return result
        except Exception as exc:
            await self.db.rollback()
            logger.exception("Failed to create report result", exc_info=exc)
            raise

    async def get_result(self, report_id: uuid.UUID) -> ReportResult | None:
        try:
            result = await self.db.execute(select(ReportResult).where(ReportResult.report_id == report_id))
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.exception("Failed to fetch report result", exc_info=exc)
            raise
