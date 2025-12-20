{{
    config(
        materialized='view'
    )
}}

-- Intermediate model that aggregates customer order history
-- This provides a customer-centric view of order metrics

with order_items as (
    select * from {{ ref('int_order_items') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

customer_orders as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.city,
        c.state,
        c.created_at as customer_since,
        -- Order metrics
        count(distinct o.order_id) as total_orders,
        sum(o.quantity) as total_items_purchased,
        cast(sum(o.revenue) as decimal(10,2)) as lifetime_value,
        cast(avg(o.revenue) as decimal(10,2)) as avg_order_value,
        min(o.order_date) as first_order_date,
        max(o.order_date) as last_order_date,
        -- Calculate days since last order
        cast(julianday('now') - julianday(max(o.order_date)) as integer) as days_since_last_order
    from customers c
    left join order_items o on c.customer_id = o.customer_id
    group by 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.city,
        c.state,
        c.created_at
)

select * from customer_orders
