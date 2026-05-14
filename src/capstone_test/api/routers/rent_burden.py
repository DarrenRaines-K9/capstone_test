from fastapi import APIRouter, Depends

from capstone_test.api.deps import get_db
from capstone_test.api.queries import get_rent_burden
from capstone_test.api.schemas.responses import RentBurdenRow

router = APIRouter(prefix="/api/v1", tags=["rent-burden"])


@router.get("/rent-burden", response_model=list[RentBurdenRow])
def rent_burden(conn=Depends(get_db)):
    return get_rent_burden(conn)
