-- Day 10-11: SQL analytics on Gold / Silver Delta tables
-- Run in Databricks SQL / notebook. Replace paths with your storage account.
-- Tip: register tables once:
--   CREATE TABLE gold_fact_sales USING DELTA LOCATION 'abfss://gold@<storage>.dfs.core.windows.net/fact_sales';

-- 1. Total revenue (excluding cancelled / returned)
SELECT ROUND(SUM(amount), 2) AS total_revenue
FROM gold_fact_sales
WHERE status NOT IN ('Cancelled', 'Returned');

-- 2. Month-over-month revenue growth (window function: LAG)
WITH m AS (
  SELECT year, month, SUM(amount) AS revenue
  FROM gold_fact_sales
  WHERE status NOT IN ('Cancelled', 'Returned')
  GROUP BY year, month
)
SELECT year, month, ROUND(revenue, 2) AS revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY year, month))
             / LAG(revenue) OVER (ORDER BY year, month) * 100, 2) AS mom_growth_pct
FROM m
ORDER BY year, month;

-- 3. Top 3 products in each category (RANK)
SELECT * FROM (
  SELECT category, product_name, SUM(amount) AS revenue,
         RANK() OVER (PARTITION BY category ORDER BY SUM(amount) DESC) AS rnk
  FROM gold_fact_sales
  GROUP BY category, product_name
) WHERE rnk <= 3;

-- 4. Customers with more than 1 order (repeat customers)
SELECT customer_id, name, COUNT(DISTINCT order_id) AS orders
FROM gold_fact_sales
GROUP BY customer_id, name
HAVING COUNT(DISTINCT order_id) > 1
ORDER BY orders DESC;

-- 5. Running total of revenue by day
SELECT order_date,
       ROUND(SUM(amount), 2) AS daily_revenue,
       ROUND(SUM(SUM(amount)) OVER (ORDER BY order_date), 2) AS running_total
FROM gold_fact_sales
GROUP BY order_date
ORDER BY order_date;

-- 6. Average order value (AOV)
SELECT ROUND(SUM(amount) / COUNT(DISTINCT order_id), 2) AS aov
FROM gold_fact_sales;

-- 7. Cancellation rate
SELECT ROUND(100.0 * SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancel_pct
FROM silver_orders;

-- 8. Customer segmentation by lifetime value (CASE)
SELECT customer_id, name, lifetime_value,
       CASE WHEN lifetime_value >= 100000 THEN 'Gold'
            WHEN lifetime_value >= 40000  THEN 'Silver'
            ELSE 'Bronze' END AS segment
FROM gold_customer_ltv;

-- 9. Detect duplicates (data quality check)
SELECT customer_id, COUNT(*) AS cnt
FROM bronze_customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- 10. SCD2: customer history
SELECT customer_id, city, effective_from, effective_to, is_current
FROM gold_dim_customer_scd2
WHERE customer_id IN (SELECT customer_id FROM gold_dim_customer_scd2 GROUP BY customer_id HAVING COUNT(*) > 1)
ORDER BY customer_id, effective_from;
