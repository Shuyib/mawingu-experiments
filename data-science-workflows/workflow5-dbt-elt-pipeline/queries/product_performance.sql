-- Product Performance Queries
-- Analyze product sales, profitability, and trends
-- Note: Mart tables are in the main_marts schema

-- 1. Top 10 products by revenue
SELECT 
    product_id,
    product_name,
    category,
    units_sold,
    total_revenue,
    total_profit,
    profit_margin_pct,
    overall_rank
FROM main_marts.mart_product_performance
ORDER BY total_revenue DESC
LIMIT 10;

-- 2. Product performance by category
SELECT 
    category,
    COUNT(*) as product_count,
    SUM(units_sold) as total_units_sold,
    ROUND(SUM(total_revenue), 2) as category_revenue,
    ROUND(SUM(total_profit), 2) as category_profit,
    ROUND(AVG(profit_margin_pct), 2) as avg_profit_margin
FROM main_marts.mart_product_performance
GROUP BY category
ORDER BY category_revenue DESC;

-- 3. Top 3 products per category
WITH ranked_products AS (
    SELECT 
        category,
        product_name,
        total_revenue,
        category_rank
    FROM main_marts.mart_product_performance
)
SELECT 
    category,
    product_name,
    total_revenue,
    category_rank
FROM ranked_products
WHERE category_rank <= 3
ORDER BY category, category_rank;

-- 4. Low-performing products (candidates for promotion or discontinuation)
SELECT 
    product_id,
    product_name,
    category,
    units_sold,
    total_revenue,
    profit_margin_pct,
    overall_rank
FROM main_marts.mart_product_performance
WHERE units_sold < 50
ORDER BY total_revenue ASC
LIMIT 20;

-- 5. High-margin products
SELECT 
    product_id,
    product_name,
    category,
    units_sold,
    total_revenue,
    total_profit,
    profit_margin_pct
FROM main_marts.mart_product_performance
WHERE profit_margin_pct >= 50
ORDER BY total_profit DESC
LIMIT 15;

-- 6. Product diversity by customer
SELECT 
    p.category,
    COUNT(DISTINCT p.customer_id) as unique_customers,
    COUNT(*) as total_orders,
    ROUND(AVG(p.total_revenue), 2) as avg_revenue_per_customer
FROM (
    SELECT 
        customer_id,
        category,
        SUM(revenue) as total_revenue
    FROM main_intermediate.int_order_items
    GROUP BY customer_id, category
) p
GROUP BY p.category
ORDER BY unique_customers DESC;

-- 7. Product sales velocity (recent vs historical)
SELECT 
    product_id,
    product_name,
    category,
    total_revenue,
    datediff('day', first_sold_date, last_sold_date) as days_on_sale,
    CASE
        WHEN datediff('day', first_sold_date, last_sold_date) = 0 THEN units_sold::DECIMAL
        ELSE ROUND(units_sold::DECIMAL / datediff('day', first_sold_date, last_sold_date), 2)
    END as units_per_day
FROM main_marts.mart_product_performance
WHERE datediff('day', first_sold_date, last_sold_date) >= 0
ORDER BY units_per_day DESC
LIMIT 20;
