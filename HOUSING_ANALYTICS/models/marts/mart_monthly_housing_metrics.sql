{{
    config(
        materialized='table',
        description='Master monthly time series spine. One row per calendar month. '
                    'Columns span four geographic levels — national, Nashville Metro, '
                    'Davidson County, and ZIP-aggregate — and must never be compared '
                    'directly across levels without explicit documentation.'
    )
}}

with

-- Monthly spine: 2015-01-01 through current month (~300 months covers to 2040)
spine as (
    select
        dateadd('month', n, '2015-01-01'::date)::date as observation_date
    from (
        select row_number() over (order by seq4()) - 1 as n
        from table(generator(rowcount => 300))
    )
    where dateadd('month', n, '2015-01-01'::date) <= date_trunc('month', current_date())
),

fred_cpi as (
    select observation_date, cpi_index
    from {{ ref('stg_fred_cpi') }}
),

fred_permits as (
    select observation_date, permit_count
    from {{ ref('stg_fred_permits') }}
),

bls_pivot as (
    select
        observation_date,
        max(case when metric_name = 'unemployment_rate'   then metric_value end) as unemployment_rate,
        max(case when metric_name = 'unemployment_count'  then metric_value end) as unemployment_count,
        max(case when metric_name = 'labor_force'         then metric_value end) as labor_force_count
    from {{ ref('stg_bls_laus') }}
    group by observation_date
),

acs_pivot as (
    select
        observation_date,
        max(case when metric_name = 'median_household_income'   then metric_value end) as median_household_income,
        max(case when metric_name = 'median_gross_rent'         then metric_value end) as median_gross_rent,
        max(case when metric_name = 'gross_rent_pct_of_income'  then metric_value end) as gross_rent_pct_of_income,
        max(is_forward_filled) as acs_is_forward_filled
    from {{ ref('stg_acs_estimates') }}
    group by observation_date
),

zillow_agg as (
    select
        date_trunc('month', observation_date)::date as observation_date,
        median(asking_rent_usd) as median_asking_rent_usd,
        count(distinct zip_code) as zip_count
    from {{ ref('stg_zillow_zori') }}
    group by date_trunc('month', observation_date)::date
),

redfin_pivot as (
    select
        observation_date,
        max(case when metric_name = 'median_sale_price' then metric_value end) as median_sale_price,
        max(case when metric_name = 'median_list_price' then metric_value end) as median_list_price,
        max(case when metric_name = 'homes_sold'        then metric_value end) as homes_sold,
        max(case when metric_name = 'inventory'         then metric_value end) as inventory,
        max(case when metric_name = 'median_dom'        then metric_value end) as median_days_on_market,
        max(case when metric_name = 'avg_sale_to_list'  then metric_value end) as avg_sale_to_list_ratio
    from {{ ref('stg_redfin') }}
    group by observation_date
)

select
    s.observation_date,

    -- National (FRED CPI benchmark — not comparable to local metrics)
    c.cpi_index                     as national_cpi_index,

    -- Nashville Metro (FRED Permits + Redfin)
    p.permit_count                  as metro_permit_count,
    r.median_sale_price             as metro_median_sale_price,
    r.median_list_price             as metro_median_list_price,
    r.homes_sold                    as metro_homes_sold,
    r.inventory                     as metro_inventory,
    r.median_days_on_market         as metro_median_days_on_market,
    r.avg_sale_to_list_ratio        as metro_avg_sale_to_list_ratio,

    -- Davidson County (BLS LAUS)
    b.unemployment_rate             as county_unemployment_rate,
    b.unemployment_count            as county_unemployment_count,
    b.labor_force_count             as county_labor_force_count,

    -- Davidson County (ACS 5-Year — annual, forward-filled to monthly)
    a.median_household_income       as county_median_household_income,
    a.median_gross_rent             as county_median_gross_rent,
    a.gross_rent_pct_of_income      as county_gross_rent_pct_of_income,
    a.acs_is_forward_filled         as county_acs_is_forward_filled,

    -- ZIP-code aggregate (Zillow ZORI — median across Nashville ZIPs)
    z.median_asking_rent_usd        as zip_median_asking_rent_usd,
    z.zip_count

from spine s
left join fred_cpi    c on c.observation_date = s.observation_date
left join fred_permits p on p.observation_date = s.observation_date
left join bls_pivot   b on b.observation_date = s.observation_date
left join acs_pivot   a on a.observation_date = s.observation_date
left join zillow_agg  z on z.observation_date = s.observation_date
left join redfin_pivot r on r.observation_date = s.observation_date