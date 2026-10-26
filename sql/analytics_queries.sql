-- Example business questions for the e-commerce warehouse.
USE ecommerce_dw;

-- 1. Monthly net sales (cancelled orders excluded).
SELECT d.year_number, d.month_number, d.month_name,
       ROUND(SUM(f.net_sales), 2) AS net_sales
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_order o ON o.order_key = f.order_key
WHERE LOWER(o.order_status) <> 'cancelled'
GROUP BY d.year_number, d.month_number, d.month_name
ORDER BY d.year_number, d.month_number;

-- 2. Best-selling products by net sales.
SELECT p.product_name, p.category,
       SUM(f.quantity) AS units_sold,
       ROUND(SUM(f.net_sales), 2) AS net_sales
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_order o ON o.order_key = f.order_key
WHERE LOWER(o.order_status) <> 'cancelled'
GROUP BY p.product_key, p.product_name, p.category
ORDER BY net_sales DESC;

-- 3. Sales by customer city.
SELECT c.city, ROUND(SUM(f.net_sales), 2) AS net_sales,
       COUNT(DISTINCT f.order_id) AS order_count
FROM fact_sales f
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_order o ON o.order_key = f.order_key
WHERE LOWER(o.order_status) <> 'cancelled'
GROUP BY c.city
ORDER BY net_sales DESC;

-- 4. Order status distribution.
SELECT o.order_status, COUNT(DISTINCT o.order_id) AS total_orders
FROM dim_order o
GROUP BY o.order_status
ORDER BY total_orders DESC;

-- 5. Payment method performance.
SELECT o.payment_method,
       COUNT(DISTINCT o.order_id) AS total_orders,
       ROUND(SUM(f.net_sales), 2) AS net_sales
FROM fact_sales f
JOIN dim_order o ON o.order_key = f.order_key
WHERE LOWER(o.order_status) <> 'cancelled'
GROUP BY o.payment_method
ORDER BY net_sales DESC;
