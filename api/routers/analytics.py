from typing import List

from fastapi import APIRouter, Depends, Query

from api.core.database import get_db
from api.core.security import get_current_user
from api.repositories.analytics import AnalyticsRepository
from api.schemas.analytics import (
    AverageAmountResponse,
    CategoryStats,
    P95AmountResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_repo(
    conn=Depends(get_db),
) -> AnalyticsRepository:
    return AnalyticsRepository(conn)


@router.get(
    "/average_amount",
    response_model=AverageAmountResponse,
    summary="Средняя сумма транзакции",
)
def average_amount(
    repo: AnalyticsRepository = Depends(get_analytics_repo),
    username: str = Depends(get_current_user),
):
    avg = repo.get_average_amount()
    return AverageAmountResponse(average_amount=avg)


@router.get(
    "/top_categories",
    response_model=List[CategoryStats],
    summary="Топ категорий по объёму транзакций",
)
def top_categories(
    limit: int = Query(
        5, ge=1, le=100, description="Максимальное число категорий"
    ),
    repo: AnalyticsRepository = Depends(get_analytics_repo),
):
    return repo.get_top_categories(limit)


@router.get(
    "/p95_amount",
    response_model=P95AmountResponse,
    summary="95-й перцентиль суммы транзакций",
)
def p95_amount(
    repo: AnalyticsRepository = Depends(get_analytics_repo),
):
    p95 = repo.get_p95_amount()
    return P95AmountResponse(p95_amount=p95)
