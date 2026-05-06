{{ config(materialized='table') }}

with base as (
    select
        observation_date,
        zip_median_asking_rent_usd,
        county_median_household_income,
        county_acs_is_forward_filled
    from {{ ref('mart_monthly_housing_metrics') }}
    where zip_median_asking_rent_usd is not null
      and county_median_household_income is not null
),

calculated as (
    select
        observation_date,
        zip_median_asking_rent_usd,
        county_median_household_income,
        county_acs_is_forward_filled        as income_is_forward_filled,

        -- Annualized asking rent as % of household income
        round(
            (zip_median_asking_rent_usd * 12) / nullif(county_median_household_income, 0) * 100,
            2
        )                                   as rent_burden_pct,

        -- Standard housing affordability threshold
        (zip_median_asking_rent_usd * 12) / nullif(county_median_household_income, 0) > 0.30
                                            as is_above_30_pct_threshold
    from base
)

select * from calculated