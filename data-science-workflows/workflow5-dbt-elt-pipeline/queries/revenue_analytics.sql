-- Revenue Analytics Queries
-- Track revenue trends and patterns over time
-- Note: Mart tables are in the main_marts schema

-- 1. Last 30 days revenue trend
SELECT 
    date,
    daily_revenue,
    revenue_7day_ma,
    order_count,
    avg_order_value
FROM main_marts.mart_daily_revenue
ORDER BY date DESC
LIMIT 30;

-- 2. Monthly revenue summary
SELECT 
    order_month,
    COUNT(DISTINCT date) as days_in_month,
    SUM(order_count) as total_orders,
    ROUND(SUM(daily_revenue), 2) as monthly_revenue,
    ROUND(SUM(daily_profit), 2) as monthly_profit,
    ROUND(AVG(daily_revenue), 2) as avg_daily_revenue
FROM main_marts.mart_daily_revenue
GROUP BY order_month
ORDER BY order_month DESC;

-- 3. Year-over-year comparison
SELECT 
    strftime(date, '%m') as month,
    order_year,
    ROUND(SUM(daily_revenue), 2) as revenue
FROM main_marts.mart_daily_revenue
GROUP BY month, order_year
ORDER BY month, order_year;

-- 4. Best performing days of the week
SELECT 
    strftime(date, '%w') as day_of_week,
    CASE strftime(date, '%w')
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END as day_name,
    COUNT(*) as occurrences,
    ROUND(AVG(daily_revenue), 2) as avg_revenue,
    ROUND(AVG(order_count), 2) as avg_orders
FROM main_marts.mart_daily_revenue
GROUP BY day_of_week, day_name
ORDER BY day_of_week;

-- 5. Revenue growth rate (month-over-month)
WITH monthly_revenue AS (
    SELECT 
        order_month,
        SUM(daily_revenue) as revenue
    FROM main_marts.mart_daily_revenue
    GROUP BY order_month
)
SELECT 
    order_month,
    revenue,
    LAG(revenue) OVER (ORDER BY order_month) as prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY order_month)) / 
        NULLIF(LAG(revenue) OVER (ORDER BY order_month), 0) * 100, 
        2
    ) as growth_rate_pct
FROM monthly_revenue
ORDER BY order_month DESC
LIMIT 12;

-- 6. Peak sales days
SELECT 
    date,
    daily_revenue,
    order_count,
    avg_order_value,
    unique_customers
FROM main_marts.mart_daily_revenue
ORDER BY daily_revenue DESC
LIMIT 10;

-- 7. Revenue by product category over time
SELECT 
    r.order_month,
    p.category,
    ROUND(SUM(p.revenue), 2) as category_revenue
FROM main_intermediate.int_order_items p
JOIN main_marts.mart_daily_revenue r ON p.order_date_only = r.date
GROUP BY r.order_month, p.category
ORDER BY r.order_month DESC, category_revenue DESC;
