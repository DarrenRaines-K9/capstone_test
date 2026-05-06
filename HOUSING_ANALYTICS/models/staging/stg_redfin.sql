with source as (
    select * from {{ source('raw', 'REDFIN_RAW') }}
),

renamed as (
    select
        observation_date::date          as observation_date,
        region_id,
        metric_name,
        value::float                    as metric_value,
        unit,
        geography,
        is_seasonally_adjusted::boolean as is_seasonally_adjusted,
        loaded_at
    from source
)

select * from renamed