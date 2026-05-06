{{ config(materialized='table') }}

with spine as (
    select
        observation_date,
        national_cpi_index,
        metro_permit_count,
        county_labor_force_count,
        county_median_household_income,
        county_acs_is_forward_filled,
        zip_median_asking_rent_usd
    from {{ ref('mart_monthly_housing_metrics') }}
),

rent_burden as (
    select observation_date, rent_burden_pct, income_is_forward_filled
    from {{ ref('mart_rent_burden') }}
),

combined as (
    select
        s.observation_date,
        rb.rent_burden_pct,
        rb.income_is_forward_filled,

        -- CPI YoY growth (national inflation benchmark)
        round(
            (s.national_cpi_index
                - lag(s.national_cpi_index, 12) over (order by s.observation_date))
            / nullif(lag(s.national_cpi_index, 12) over (order by s.observation_date), 0) * 100,
            2
        ) as cpi_yoy_growth_pct,

        -- Income YoY growth (higher = more affordable, will be inverted in score)
        round(
            (s.county_median_household_income
                - lag(s.county_median_household_income, 12) over (order by s.observation_date))
            / nullif(lag(s.county_median_household_income, 12) over (order by s.observation_date), 0) * 100,
            2
        ) as income_growth_yoy_pct,

        -- Supply response rate: permits per 1k labor force (higher = more supply = more affordable, inverted)
        round(
            s.metro_permit_count / nullif(s.county_labor_force_count, 0) * 1000,
            4
        ) as supply_response_rate

    from spine s
    left join rent_burden rb on rb.observation_date = s.observation_date
    where rb.rent_burden_pct is not null
),

-- Min-max normalize each component across all months in the dataset
normalized as (
    select
        *,
        -- Rent burden: higher = less affordable → higher score
        (rent_burden_pct - min(rent_burden_pct) over ())
            / nullif(max(rent_burden_pct) over () - min(rent_burden_pct) over (), 0)
            * 100                                               as rent_burden_score,

        -- CPI growth: higher inflation = less affordable → higher score
        (coalesce(cpi_yoy_growth_pct, 0) - min(coalesce(cpi_yoy_growth_pct, 0)) over ())
            / nullif(
                max(coalesce(cpi_yoy_growth_pct, 0)) over ()
                - min(coalesce(cpi_yoy_growth_pct, 0)) over (), 0)
            * 100                                               as cpi_growth_score,

        -- Income growth: higher = more affordable → inverted
        100 - (coalesce(income_growth_yoy_pct, 0) - min(coalesce(income_growth_yoy_pct, 0)) over ())
            / nullif(
                max(coalesce(income_growth_yoy_pct, 0)) over ()
                - min(coalesce(income_growth_yoy_pct, 0)) over (), 0)
            * 100                                               as income_growth_score,

        -- Supply response: more permits per worker = more affordable → inverted
        100 - (coalesce(supply_response_rate, 0) - min(coalesce(supply_response_rate, 0)) over ())
            / nullif(
                max(coalesce(supply_response_rate, 0)) over ()
                - min(coalesce(supply_response_rate, 0)) over (), 0)
            * 100                                               as supply_response_score

    from combined
)

select
    observation_date,
    rent_burden_pct,
    cpi_yoy_growth_pct,
    income_growth_yoy_pct,
    supply_response_rate,
    income_is_forward_filled,

    -- Weighted composite: 50% rent burden, 25% CPI, 15% income growth, 10% supply response
    round(
          rent_burden_score   * 0.50
        + cpi_growth_score    * 0.25
        + income_growth_score * 0.15
        + supply_response_score * 0.10,
        1
    )                                   as affordability_index

from normalized