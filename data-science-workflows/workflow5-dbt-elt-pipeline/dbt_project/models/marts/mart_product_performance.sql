{{
    config(
        materialized='table'
    )
}}

-- Mart model for product performance analytics
-- This provides product-level metrics for inventory and marketing decisions

with order_items as (
    select * from {{ ref('int_order_items') }}
),

product_performance as (
    select
        product_id,
        product_name,
        category,
        -- Sales metrics
        count(distinct order_id) as total_orders,
        sum(quantity) as units_sold,
        cast(sum(revenue) as decimal(10,2)) as total_revenue,
        cast(sum(cost_of_goods) as decimal(10,2)) as total_cost,
        cast(sum(profit) as decimal(10,2)) as total_profit,
        cast(avg(revenue) as decimal(10,2)) as avg_revenue_per_order,
        -- Profitability
        case 
            when sum(revenue) > 0 then
                round(cast(sum(profit) as decimal) / cast(sum(revenue) as decimal) * 100, 2)
            else 0
        end as profit_margin_pct,
        -- Time metrics
        min(order_date) as first_sold_date,
        max(order_date) as last_sold_date,
        count(distinct customer_id) as unique_customers
    from order_items
    group by 
        product_id,
        product_name,
        category
),

ranked_products as (
    select
        *,
        -- Rank products within category by revenue
        row_number() over (partition by category order by total_revenue desc) as category_rank,
        -- Overall rank by revenue
        row_number() over (order by total_revenue desc) as overall_rank
    from product_performance
)

select * from ranked_products
order by total_revenue desc
