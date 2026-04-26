from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.modules.analytics.schemas import (
    CategoryBreakdownOut,
    TopPropertyOut,
    TotalSalesOut,
)
from app.modules.analytics.service import AnalyticsService

router = APIRouter()


@router.get(
    "/total-sales",
    response_model=TotalSalesOut,
    summary="Get total revenue and transaction count",
)
async def total_sales(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_user),
):
    return await AnalyticsService.get_total_sales(db, start_date, end_date)


@router.get(
    "/top-properties",
    response_model=list[TopPropertyOut],
    summary="Get top 3 properties by revenue",
)
async def top_properties(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_user),
):
    return await AnalyticsService.get_top_properties(db, start_date, end_date)


@router.get(
    "/category-breakdown",
    response_model=list[CategoryBreakdownOut],
    summary="Get revenue breakdown by category",
)
async def category_breakdown(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_user),
):
    return await AnalyticsService.get_category_breakdown(db, start_date, end_date)