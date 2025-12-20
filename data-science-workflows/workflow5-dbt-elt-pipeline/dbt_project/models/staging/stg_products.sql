{{
    config(
        materialized='view'
    )
}}

-- Staging model for products
-- This model cleans and standardizes raw product data

with source as (
    select * from raw_products
),

renamed as (
    select
        product_id,
        product_name,
        category,
        cast(price as decimal(10,2)) as price,
        cast(cost as decimal(10,2)) as cost,
        -- Calculate profit margin
        round((price - cost) / price * 100, 2) as profit_margin_pct,
        cast(created_at as timestamp) as created_at
    from source
)

select * from renamed
