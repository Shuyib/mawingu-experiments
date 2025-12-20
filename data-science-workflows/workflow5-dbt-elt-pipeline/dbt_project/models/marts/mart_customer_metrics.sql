{{
    config(
        materialized='table'
    )
}}

-- Mart model for customer analytics
-- This provides a comprehensive view of customer metrics for analysis

with customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

customer_metrics as (
    select
        customer_id,
        first_name,
        last_name,
        email,
        city,
        state,
        customer_since,
        total_orders,
        total_items_purchased,
        lifetime_value,
        avg_order_value,
        first_order_date,
        last_order_date,
        days_since_last_order,
        -- Customer segmentation
        case 
            when lifetime_value >= 1000 then 'VIP'
            when lifetime_value >= 500 then 'High Value'
            when lifetime_value >= 100 then 'Medium Value'
            else 'Low Value'
        end as customer_segment,
        -- Activity status
        case 
            when days_since_last_order <= 30 then 'Active'
            when days_since_last_order <= 90 then 'At Risk'
            when days_since_last_order <= 180 then 'Dormant'
            else 'Churned'
        end as activity_status,
        -- Purchase frequency (orders per month)
        case
            when first_order_date is not null and total_orders > 0 then
                case
                    when datediff('day', first_order_date, last_order_date) = 0 then total_orders
                    else round(
                        cast(total_orders as decimal) / 
                        (cast(datediff('day', first_order_date, last_order_date) as decimal) / 30.0),
                        2
                    )
                end
            else 0
        end as orders_per_month
    from customer_orders
)

select * from customer_metrics
order by lifetime_value desc
