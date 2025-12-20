{{
    config(
        materialized='view'
    )
}}

-- Staging model for customers
-- This model cleans and standardizes raw customer data

with source as (
    select * from raw_customers
),

renamed as (
    select
        customer_id,
        first_name,
        last_name,
        -- Standardize email to lowercase
        lower(email) as email,
        phone,
        city,
        state,
        country,
        cast(created_at as timestamp) as created_at
    from source
)

select * from renamed
