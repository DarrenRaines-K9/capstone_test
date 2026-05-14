from datetime import date
from typing import Optional

from pydantic import BaseModel


class MonthlyMetricsRow(BaseModel):
    observation_date: date
    national_cpi_index: Optional[float] = None
    metro_permit_count: Optional[float] = None
    metro_median_sale_price: Optional[float] = None
    metro_median_list_price: Optional[float] = None
    metro_homes_sold: Optional[float] = None
    metro_inventory: Optional[float] = None
    metro_median_days_on_market: Optional[float] = None
    metro_avg_sale_to_list_ratio: Optional[float] = None
    county_unemployment_rate: Optional[float] = None
    county_unemployment_count: Optional[float] = None
    county_labor_force_count: Optional[float] = None
    county_median_household_income: Optional[float] = None
    county_median_gross_rent: Optional[float] = None
    county_gross_rent_pct_of_income: Optional[float] = None
    county_acs_is_forward_filled: Optional[bool] = None
    zip_median_asking_rent_usd: Optional[float] = None
    zip_count: Optional[int] = None


class RentBurdenRow(BaseModel):
    observation_date: date
    zip_median_asking_rent_usd: Optional[float] = None
    county_median_household_income: Optional[float] = None
    income_is_forward_filled: Optional[bool] = None
    rent_burden_pct: Optional[float] = None
    is_above_30_pct_threshold: Optional[bool] = None


class SupplyDemandRow(BaseModel):
    observation_date: date
    metro_permit_count: Optional[float] = None
    county_unemployment_rate: Optional[float] = None
    county_labor_force_count: Optional[float] = None
    zip_median_asking_rent_usd: Optional[float] = None
    rent_growth_3m_pct: Optional[float] = None
    labor_force_growth_3m_pct: Optional[float] = None
    permit_growth_3m_pct: Optional[float] = None
    rent_growth_lag_3m: Optional[float] = None
    employment_growth_lag_3m: Optional[float] = None
    permit_growth_lag_3m: Optional[float] = None


class AffordabilityRow(BaseModel):
    observation_date: date
    rent_burden_pct: Optional[float] = None
    cpi_yoy_growth_pct: Optional[float] = None
    income_growth_yoy_pct: Optional[float] = None
    supply_response_rate: Optional[float] = None
    income_is_forward_filled: Optional[bool] = None
    affordability_index: Optional[float] = None


class SummaryResponse(BaseModel):
    # Each mart may have a different latest observation date
    metrics_as_of: Optional[date] = None
    national_cpi_index: Optional[float] = None
    zip_median_asking_rent_usd: Optional[float] = None
    county_unemployment_rate: Optional[float] = None
    county_median_household_income: Optional[float] = None

    rent_burden_as_of: Optional[date] = None
    rent_burden_pct: Optional[float] = None
    is_above_30_pct_threshold: Optional[bool] = None

    supply_demand_as_of: Optional[date] = None
    rent_growth_3m_pct: Optional[float] = None
    labor_force_growth_3m_pct: Optional[float] = None
    permit_growth_3m_pct: Optional[float] = None

    affordability_as_of: Optional[date] = None
    affordability_index: Optional[float] = None
