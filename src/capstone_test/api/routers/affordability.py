from fastapi import APIRouter, Depends

from capstone_test.api.deps import get_db
from capstone_test.api.queries import get_affordability
from capstone_test.api.schemas.responses import AffordabilityRow

router = APIRouter(prefix="/api/v1", tags=["affordability"])


@router.get("/affordability", response_model=list[AffordabilityRow])
def affordability(conn=Depends(get_db)):
    return get_affordability(conn)
