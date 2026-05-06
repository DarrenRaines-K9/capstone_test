with source as (
    select * from {{ source('raw', 'FRED_PERMITS_RAW') }}
),

renamed as (
    select
        observation_date::date          as observation_date,
        series_id,
        value::float                    as permit_count,
        geography,
        unit,
        is_seasonally_adjusted::boolean as is_seasonally_adjusted,
        loaded_at
    from source
)

select * from renamed