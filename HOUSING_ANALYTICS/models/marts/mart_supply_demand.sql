{{ config(materialized='table') }}

with base as (
    select
        observation_date,
        metro_permit_count,
        county_unemployment_rate,
        county_labor_force_count,
        zip_median_asking_rent_usd
    from {{ ref('mart_monthly_housing_metrics') }}
    where metro_permit_count is not null
       or county_labor_force_count is not null
       or zip_median_asking_rent_usd is not null
),

with_growth as (
    select
        observation_date,
        metro_permit_count,
        county_unemployment_rate,
        county_labor_force_count,
        zip_median_asking_rent_usd,

        -- 3-month trailing growth rates
        round(
            (zip_median_asking_rent_usd - lag(zip_median_asking_rent_usd, 3) over (order by observation_date))
            / nullif(lag(zip_median_asking_rent_usd, 3) over (order by observation_date), 0) * 100,
            2
        ) as rent_growth_3m_pct,

        round(
            (county_labor_force_count - lag(county_labor_force_count, 3) over (order by observation_date))
            / nullif(lag(county_labor_force_count, 3) over (order by observation_date), 0) * 100,
            2
        ) as labor_force_growth_3m_pct,

        round(
            (metro_permit_count - lag(metro_permit_count, 3) over (order by observation_date))
            / nullif(lag(metro_permit_count, 3) over (order by observation_date), 0) * 100,
            2
        ) as permit_growth_3m_pct

    from base
)

select
    observation_date,
    metro_permit_count,
    county_unemployment_rate,
    county_labor_force_count,
    zip_median_asking_rent_usd,
    rent_growth_3m_pct,
    labor_force_growth_3m_pct,
    permit_growth_3m_pct,

    -- Lagged growth rates for lead/lag correlation analysis
    lag(rent_growth_3m_pct, 3)         over (order by observation_date) as rent_growth_lag_3m,
    lag(labor_force_growth_3m_pct, 3)  over (order by observation_date) as employment_growth_lag_3m,
    lag(permit_growth_3m_pct, 3)       over (order by observation_date) as permit_growth_lag_3m

from with_growth