from fastapi import APIRouter, Depends

from capstone_test.api.deps import get_db
from capstone_test.api.queries import get_summary
from capstone_test.api.schemas.responses import SummaryResponse

router = APIRouter(prefix="/api/v1", tags=["summary"])


@router.get("/summary", response_model=SummaryResponse)
def summary(conn=Depends(get_db)):
    return get_summary(conn)
