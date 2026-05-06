with source as (
    select * from {{ source('raw', 'ZILLOW_ZORI_RAW') }}
),

renamed as (
    select
        observation_date::date          as observation_date,
        region_id,
        region_name                     as zip_code,
        value::float                    as asking_rent_usd,
        geography,
        unit,
        is_seasonally_adjusted::boolean as is_seasonally_adjusted,
        loaded_at
    from source
)

select * from renamed