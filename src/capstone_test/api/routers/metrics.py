from fastapi import APIRouter, Depends

from capstone_test.api.deps import get_db
from capstone_test.api.queries import get_monthly_metrics
from capstone_test.api.schemas.responses import MonthlyMetricsRow

router = APIRouter(prefix="/api/v1", tags=["metrics"])


@router.get("/metrics", response_model=list[MonthlyMetricsRow])
def metrics(conn=Depends(get_db)):
    return get_monthly_metrics(conn)
