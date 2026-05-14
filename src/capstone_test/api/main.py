from contextlib import asynccontextmanager

from fastapi import FastAPI

from capstone_test.api.routers.affordability import router as affordability_router
from capstone_test.api.routers.metrics import router as metrics_router
from capstone_test.api.routers.rent_burden import router as rent_burden_router
from capstone_test.api.routers.summary import router as summary_router
from capstone_test.api.routers.supply_demand import router as supply_demand_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Nashville Housing Analytics API",
    docs_url="/docs",
    lifespan=lifespan,
)

app.include_router(metrics_router)
app.include_router(rent_burden_router)
app.include_router(supply_demand_router)
app.include_router(affordability_router)
app.include_router(summary_router)
