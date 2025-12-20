{{
    config(
        materialized='view'
    )
}}

-- Intermediate model that enriches order items with product details
-- This joins orders with products to calculate revenue and profit

with orders as (
    select * from {{ ref('stg_orders') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

order_items as (
    select
        o.order_id,
        o.customer_id,
        o.product_id,
        o.quantity,
        o.order_date,
        o.order_date_only,
        o.order_month,
        o.order_year,
        o.status,
        p.product_name,
        p.category,
        p.price,
        p.cost,
        -- Calculate line item metrics
        cast(o.quantity * p.price as decimal(10,2)) as revenue,
        cast(o.quantity * p.cost as decimal(10,2)) as cost_of_goods,
        cast((o.quantity * p.price) - (o.quantity * p.cost) as decimal(10,2)) as profit
    from orders o
    inner join products p on o.product_id = p.product_id
    where o.status = 'completed'  -- Only include completed orders
)

select * from order_items
