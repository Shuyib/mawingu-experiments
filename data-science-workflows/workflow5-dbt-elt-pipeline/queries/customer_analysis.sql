-- Customer Analysis Queries
-- Run these queries against the DuckDB warehouse after dbt transformations

-- 1. Top 10 customers by lifetime value
SELECT 
    customer_id,
    first_name || ' ' || last_name as customer_name,
    email,
    lifetime_value,
    total_orders,
    customer_segment,
    activity_status
FROM mart_customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10;

-- 2. Customer segmentation distribution
SELECT 
    customer_segment,
    COUNT(*) as customer_count,
    ROUND(SUM(lifetime_value), 2) as total_ltv,
    ROUND(AVG(lifetime_value), 2) as avg_ltv,
    ROUND(AVG(total_orders), 2) as avg_orders
FROM mart_customer_metrics
GROUP BY customer_segment
ORDER BY total_ltv DESC;

-- 3. Customer activity status
SELECT 
    activity_status,
    COUNT(*) as customer_count,
    ROUND(SUM(lifetime_value), 2) as total_ltv,
    ROUND(AVG(days_since_last_order), 0) as avg_days_since_order
FROM mart_customer_metrics
GROUP BY activity_status
ORDER BY 
    CASE activity_status
        WHEN 'Active' THEN 1
        WHEN 'At Risk' THEN 2
        WHEN 'Dormant' THEN 3
        WHEN 'Churned' THEN 4
    END;

-- 4. Geographic distribution of high-value customers
SELECT 
    state,
    COUNT(*) as customer_count,
    ROUND(SUM(lifetime_value), 2) as total_ltv,
    ROUND(AVG(lifetime_value), 2) as avg_ltv
FROM mart_customer_metrics
WHERE customer_segment IN ('VIP', 'High Value')
GROUP BY state
ORDER BY total_ltv DESC
LIMIT 15;

-- 5. Customer cohort analysis by signup month
SELECT 
    strftime(customer_since, '%Y-%m') as cohort_month,
    COUNT(*) as customers,
    ROUND(SUM(lifetime_value), 2) as cohort_ltv,
    ROUND(AVG(lifetime_value), 2) as avg_ltv_per_customer,
    ROUND(AVG(total_orders), 2) as avg_orders_per_customer
FROM mart_customer_metrics
GROUP BY cohort_month
ORDER BY cohort_month DESC
LIMIT 12;

-- 6. At-risk customers (for retention campaigns)
SELECT 
    customer_id,
    first_name || ' ' || last_name as customer_name,
    email,
    lifetime_value,
    last_order_date,
    days_since_last_order
FROM mart_customer_metrics
WHERE activity_status = 'At Risk'
    AND customer_segment IN ('VIP', 'High Value')
ORDER BY lifetime_value DESC
LIMIT 20;
