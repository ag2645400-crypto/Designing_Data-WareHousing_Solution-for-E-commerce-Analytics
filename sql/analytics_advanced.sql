USE ecommerce_dw;

-- =====================================================
-- PART 1: VIEWS (reusable building blocks for reports and Power BI)
-- =====================================================

-- All sales joined with their dimensions.
CREATE OR REPLACE VIEW vw_sales_detail AS
SELECT f.order_id, f.quantity, f.unit_price, f.discount,
       f.gross_sales, f.net_sales,
       d.full_date, d.month_number, d.month_name,
       d.quarter_number, d.year_number,
       c.customer_id, c.customer_name, c.city,
       p.product_name, p.category,
       o.payment_method, o.order_status
FROM fact_sales f
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_product  p ON p.product_key  = f.product_key
JOIN dim_date     d ON d.date_key     = f.date_key
JOIN dim_order    o ON o.order_key    = f.order_key;

-- Same data without cancelled orders (used for sales analysis).
CREATE OR REPLACE VIEW vw_net_sales AS
SELECT * FROM vw_sales_detail
WHERE LOWER(order_status) <> 'cancelled';

-- =====================================================
-- PART 2: BUSINESS QUERIES
-- =====================================================

-- Q1. Monthly net sales with month-over-month growth.
WITH m AS (
    SELECT year_number, month_number, month_name,
           ROUND(SUM(net_sales), 2) AS net_sales
    FROM vw_net_sales
    GROUP BY year_number, month_number, month_name
)
SELECT year_number, month_number, month_name, net_sales,
       ROUND((net_sales - LAG(net_sales) OVER (ORDER BY year_number, month_number))
             / LAG(net_sales) OVER (ORDER BY year_number, month_number) * 100, 1)
             AS mom_growth_pct
FROM m
ORDER BY year_number, month_number;

-- Q2. Quarterly performance.
SELECT year_number, quarter_number,
       COUNT(DISTINCT order_id) AS total_orders,
       ROUND(SUM(net_sales), 2) AS net_sales
FROM vw_net_sales
GROUP BY year_number, quarter_number
ORDER BY year_number, quarter_number;

-- Q3. Year-over-year comparison by month (2025 vs 2026).
SELECT month_number, month_name,
       ROUND(SUM(CASE WHEN year_number = 2025 THEN net_sales END), 2) AS sales_2025,
       ROUND(SUM(CASE WHEN year_number = 2026 THEN net_sales END), 2) AS sales_2026
FROM vw_net_sales
GROUP BY month_number, month_name
ORDER BY month_number;

-- Q4. Top 10 customers by net sales.
SELECT customer_id, customer_name, city,
       COUNT(DISTINCT order_id) AS total_orders,
       ROUND(SUM(net_sales), 2) AS net_sales
FROM vw_net_sales
GROUP BY customer_id, customer_name, city
ORDER BY net_sales DESC
LIMIT 10;

-- Q5. Repeat customer rate.
SELECT COUNT(*) AS total_customers,
       SUM(order_count > 1) AS repeat_customers,
       ROUND(SUM(order_count > 1) / COUNT(*) * 100, 1) AS repeat_rate_pct
FROM (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM vw_net_sales
    GROUP BY customer_id
) t;

-- Q6. Average order value by city.
SELECT city,
       COUNT(DISTINCT order_id) AS total_orders,
       ROUND(SUM(net_sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM vw_net_sales
GROUP BY city
ORDER BY avg_order_value DESC;

-- Q7. City sales ranking.
SELECT city,
       COUNT(DISTINCT order_id) AS total_orders,
       ROUND(SUM(net_sales), 2) AS net_sales,
       RANK() OVER (ORDER BY SUM(net_sales) DESC) AS sales_rank
FROM vw_net_sales
GROUP BY city
ORDER BY sales_rank;

-- Q8. Category share of total net sales.
SELECT category,
       ROUND(SUM(net_sales), 2) AS net_sales,
       ROUND(SUM(net_sales) / SUM(SUM(net_sales)) OVER () * 100, 1) AS share_pct
FROM vw_net_sales
GROUP BY category
ORDER BY net_sales DESC;

-- Q9. Top 3 products in every category.
SELECT category, product_name, net_sales, rank_in_category
FROM (
    SELECT category, product_name,
           ROUND(SUM(net_sales), 2) AS net_sales,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY SUM(net_sales) DESC)
               AS rank_in_category
    FROM vw_net_sales
    GROUP BY category, product_name
) t
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- Q10. Cancellation rate by payment method.
SELECT payment_method,
       COUNT(DISTINCT order_id) AS total_orders,
       COUNT(DISTINCT CASE WHEN LOWER(order_status) = 'cancelled' THEN order_id END)
           AS cancelled_orders,
       ROUND(COUNT(DISTINCT CASE WHEN LOWER(order_status) = 'cancelled' THEN order_id END)
             / COUNT(DISTINCT order_id) * 100, 1) AS cancel_rate_pct
FROM vw_sales_detail
GROUP BY payment_method
ORDER BY cancel_rate_pct DESC;

-- Q11. Weekday vs weekend sales.
SELECT CASE WHEN DAYOFWEEK(full_date) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END
           AS day_type,
       COUNT(DISTINCT order_id) AS total_orders,
       ROUND(SUM(net_sales), 2) AS net_sales,
       ROUND(SUM(net_sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM vw_net_sales
GROUP BY day_type;

-- Q12. Discount impact by category.
SELECT category,
       ROUND(SUM(gross_sales), 2) AS gross_sales,
       ROUND(SUM(discount), 2) AS total_discount,
       ROUND(SUM(discount) / SUM(gross_sales) * 100, 1) AS discount_pct
FROM vw_net_sales
GROUP BY category
ORDER BY discount_pct DESC;

-- Q13. Order status distribution with percentage.
SELECT order_status,
       COUNT(DISTINCT order_id) AS total_orders,
       ROUND(COUNT(DISTINCT order_id)
             / SUM(COUNT(DISTINCT order_id)) OVER () * 100, 1) AS pct_of_orders
FROM vw_sales_detail
GROUP BY order_status
ORDER BY total_orders DESC;