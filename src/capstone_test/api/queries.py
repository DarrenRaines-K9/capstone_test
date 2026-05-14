from capstone_test.api.schemas.responses import (
    AffordabilityRow,
    MonthlyMetricsRow,
    RentBurdenRow,
    SupplyDemandRow,
    SummaryResponse,
)


def _row_dicts(cursor) -> list[dict]:
    """Return all rows as dicts with lowercase column names."""
    cols = [d[0].lower() for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _one_dict(cursor) -> dict | None:
    """Return a single row as a dict with lowercase column names, or None."""
    cols = [d[0].lower() for d in cursor.description]
    row = cursor.fetchone()
    return dict(zip(cols, row)) if row else None


def get_monthly_metrics(conn) -> list[MonthlyMetricsRow]:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM MARTS.MART_MONTHLY_HOUSING_METRICS ORDER BY OBSERVATION_DATE"
    )
    return [MonthlyMetricsRow(**row) for row in _row_dicts(cur)]


def get_rent_burden(conn) -> list[RentBurdenRow]:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM MARTS.MART_RENT_BURDEN ORDER BY OBSERVATION_DATE"
    )
    return [RentBurdenRow(**row) for row in _row_dicts(cur)]


def get_supply_demand(conn) -> list[SupplyDemandRow]:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM MARTS.MART_SUPPLY_DEMAND ORDER BY OBSERVATION_DATE"
    )
    return [SupplyDemandRow(**row) for row in _row_dicts(cur)]


def get_affordability(conn) -> list[AffordabilityRow]:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM MARTS.MART_AFFORDABILITY_INDEX ORDER BY OBSERVATION_DATE"
    )
    return [AffordabilityRow(**row) for row in _row_dicts(cur)]


def get_summary(conn) -> SummaryResponse:
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM MARTS.MART_MONTHLY_HOUSING_METRICS ORDER BY OBSERVATION_DATE DESC LIMIT 1"
    )
    m = _one_dict(cur) or {}

    cur.execute(
        "SELECT * FROM MARTS.MART_RENT_BURDEN ORDER BY OBSERVATION_DATE DESC LIMIT 1"
    )
    rb = _one_dict(cur) or {}

    cur.execute(
        "SELECT * FROM MARTS.MART_SUPPLY_DEMAND ORDER BY OBSERVATION_DATE DESC LIMIT 1"
    )
    sd = _one_dict(cur) or {}

    cur.execute(
        "SELECT * FROM MARTS.MART_AFFORDABILITY_INDEX ORDER BY OBSERVATION_DATE DESC LIMIT 1"
    )
    af = _one_dict(cur) or {}

    return SummaryResponse(
        metrics_as_of=m.get("observation_date"),
        national_cpi_index=m.get("national_cpi_index"),
        zip_median_asking_rent_usd=m.get("zip_median_asking_rent_usd"),
        county_unemployment_rate=m.get("county_unemployment_rate"),
        county_median_household_income=m.get("county_median_household_income"),
        rent_burden_as_of=rb.get("observation_date"),
        rent_burden_pct=rb.get("rent_burden_pct"),
        is_above_30_pct_threshold=rb.get("is_above_30_pct_threshold"),
        supply_demand_as_of=sd.get("observation_date"),
        rent_growth_3m_pct=sd.get("rent_growth_3m_pct"),
        labor_force_growth_3m_pct=sd.get("labor_force_growth_3m_pct"),
        permit_growth_3m_pct=sd.get("permit_growth_3m_pct"),
        affordability_as_of=af.get("observation_date"),
        affordability_index=af.get("affordability_index"),
    )
