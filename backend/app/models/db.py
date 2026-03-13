from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(20))
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ReportResult(Base):
    __tablename__ = "report_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    findings: Mapped[dict] = mapped_column(JSONB)
    classification: Mapped[dict] = mapped_column(JSONB)
    triage: Mapped[dict] = mapped_column(JSONB)
    explainability: Mapped[dict] = mapped_column(JSONB)
    inconsistencies: Mapped[dict] = mapped_column(JSONB)
    lifestyle: Mapped[dict] = mapped_column(JSONB)
    follow_up: Mapped[dict] = mapped_column(JSONB)
    notification: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
