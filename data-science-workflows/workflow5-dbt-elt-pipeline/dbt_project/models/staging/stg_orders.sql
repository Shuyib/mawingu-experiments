{{
    config(
        materialized='view'
    )
}}

-- Staging model for orders
-- This model cleans and standardizes raw order data

with source as (
    select * from raw_orders
),

renamed as (
    select
        order_id,
        customer_id,
        product_id,
        quantity,
        cast(order_date as timestamp) as order_date,
        status,
        -- Extract date components for analysis
        cast(strftime(cast(order_date as timestamp), '%Y-%m-%d') as date) as order_date_only,
        cast(strftime(cast(order_date as timestamp), '%Y-%m') as varchar) as order_month,
        cast(strftime(cast(order_date as timestamp), '%Y') as integer) as order_year
    from source
)

select * from renamed
