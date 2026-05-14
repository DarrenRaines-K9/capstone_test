from fastapi import APIRouter, Depends

from capstone_test.api.deps import get_db
from capstone_test.api.queries import get_supply_demand
from capstone_test.api.schemas.responses import SupplyDemandRow

router = APIRouter(prefix="/api/v1", tags=["supply-demand"])


@router.get("/supply-demand", response_model=list[SupplyDemandRow])
def supply_demand(conn=Depends(get_db)):
    return get_supply_demand(conn)
