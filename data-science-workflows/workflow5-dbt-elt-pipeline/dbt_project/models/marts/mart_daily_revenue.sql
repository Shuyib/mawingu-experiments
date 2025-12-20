{{
    config(
        materialized='table'
    )
}}

-- Mart model for daily revenue analytics
-- This provides time-series data for revenue tracking and forecasting

with order_items as (
    select * from {{ ref('int_order_items') }}
),

daily_metrics as (
    select
        order_date_only as date,
        order_month,
        order_year,
        -- Transaction metrics
        count(distinct order_id) as order_count,
        count(distinct customer_id) as unique_customers,
        sum(quantity) as items_sold,
        -- Financial metrics
        cast(sum(revenue) as decimal(10,2)) as daily_revenue,
        cast(sum(cost_of_goods) as decimal(10,2)) as daily_cost,
        cast(sum(profit) as decimal(10,2)) as daily_profit,
        cast(avg(revenue) as decimal(10,2)) as avg_order_value,
        -- Product mix
        count(distinct product_id) as unique_products_sold
    from order_items
    group by 
        order_date_only,
        order_month,
        order_year
),

with_moving_averages as (
    select
        *,
        -- 7-day moving average
        round(
            avg(daily_revenue) over (
                order by date 
                rows between 6 preceding and current row
            ),
            2
        ) as revenue_7day_ma,
        -- Month-to-date cumulative
        sum(daily_revenue) over (
            partition by order_month 
            order by date
        ) as mtd_revenue
    from daily_metrics
)

select * from with_moving_averages
order by date desc
