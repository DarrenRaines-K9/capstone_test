with source as (
    select * from {{ source('raw', 'BLS_LAUS_RAW') }}
),

renamed as (
    select
        observation_date::date          as observation_date,
        series_id,
        unit                            as metric_name,
        value::float                    as metric_value,
        geography,
        is_seasonally_adjusted::boolean as is_seasonally_adjusted,
        loaded_at
    from source
)

select * from renamed