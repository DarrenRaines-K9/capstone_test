with source as (
    select * from {{ source('raw', 'ACS_ESTIMATES_RAW') }}
),

-- Generate month offsets 0–11 to expand each annual row into 12 monthly rows
month_offsets as (
    select (row_number() over (order by seq4()) - 1) as month_offset
    from table(generator(rowcount => 12))
),

expanded as (
    select
        dateadd(
            'month',
            m.month_offset,
            date_trunc('year', s.observation_date::date)
        )::date                         as observation_date,
        s.survey_year::integer          as survey_year,
        s.geography,
        s.variable_code,
        s.variable_name                 as metric_name,
        s.value::float                  as metric_value,
        s.unit,
        s.is_seasonally_adjusted::boolean as is_seasonally_adjusted,
        (m.month_offset > 0)            as is_forward_filled,
        s.loaded_at
    from source s
    cross join month_offsets m
)

select * from expanded