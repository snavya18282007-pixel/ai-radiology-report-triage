from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.dashboard import DashboardStatsResponse
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    service = DashboardService(db)
    return await service.get_stats()
