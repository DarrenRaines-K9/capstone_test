with source as (
    select * from {{ source('raw', 'FRED_CPI_RAW') }}
),

renamed as (
    select
        observation_date::date          as observation_date,
        series_id,
        value::float                    as cpi_index,
        geography,
        unit,
        is_seasonally_adjusted::boolean as is_seasonally_adjusted,
        loaded_at
    from source
)

select * from renamed