-- ============================================================
-- (a) ORDER TOTALS
-- Calculate total number of orders, total revenue,
-- and average order value.
-- NULL discount_pct is treated as 0%.
-- ============================================================

-- Output:
-- total_orders | total_revenue | avg_order_value
-- 180          | 99860.2       | 554.78

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS total_revenue,
    ROUND(AVG(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS avg_order_value
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;

-- ============================================================
-- (b) COUNT(*) VS COUNT(column)
-- COUNT(*) counts all orders, while COUNT(rating)
-- counts only orders where rating is NOT NULL.
-- ============================================================

-- Output:
-- total_orders | orders_with_rating | orders_without_rating
-- 180          | 165                | 15

SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS orders_with_rating,
    COUNT(*) - COUNT(rating) AS orders_without_rating
FROM orders;

-- ============================================================
-- (c) CUSTOMERS WITH ZERO ORDERS - LEFT JOIN
-- LEFT JOIN keeps every customer, including customers
-- who have no matching order.
-- ============================================================

-- Output:
-- customer_id | name
-- C045        | Vihaan

SELECT
    c.customer_id,
    c.name
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.name
HAVING COUNT(o.order_id) = 0;

-- Independent verification using NOT IN.

-- Output:
-- customer_id | name
-- C045        | Vihaan

SELECT
    customer_id,
    name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
);

-- ============================================================
-- (d) CITY RETURN RATES - GROUP BY + HAVING
-- Calculate the return rate for each city and keep only
-- cities with a return rate greater than 20%.
-- ============================================================

-- Output:
-- city      | total_orders | returned_orders | return_rate_pct
-- Jaipur    | 19           | 8               | 42.1
-- Lucknow   | 49           | 15              | 30.6
-- Bangalore | 33           | 8               | 24.2

SELECT
    c.city,
    COUNT(*) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(
        100.0 * SUM(o.returned) / COUNT(*),
        1
    ) AS return_rate_pct


FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

-- ============================================================
-- (e) TOP CUSTOMERS BY TOTAL SPEND - ORDER BY + LIMIT
-- Rank customers by their total spend and return the top 5.
-- customer_id ASC provides deterministic ordering when spend ties.
-- ============================================================

-- Output:
-- customer_id | name    | total_spend
-- C043        | Reyansh | 12920.0
-- C026        | Isha    | 8371.6
-- C008        | Meera   | 4564.6
-- C011        | Arjun   | 4111.0
-- C042        | Sanya   | 3785.0

SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS total_spend
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.name
ORDER BY
    total_spend DESC,
    c.customer_id ASC
LIMIT 5;


-- Report (e) verification: ranks 3-5 using LIMIT and OFFSET.
-- OFFSET 2 skips ranks 1 and 2; LIMIT 3 returns the next 3 rows.

-- Output:
-- customer_id | name  | total_spend
-- C008        | Meera | 4564.6
-- C011        | Arjun | 4111.0
-- C042        | Sanya | 3785.0

SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS total_spend
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.name
ORDER BY
    total_spend DESC,
    c.customer_id ASC
LIMIT 3 OFFSET 2;


-- ============================================================
-- (f) CATEGORY REVENUE - THREE-TABLE JOIN + GROUP BY
-- Join orders, products, and customers; calculate order count
-- and revenue for each product category.
-- ============================================================

-- Output:
-- category     | order_count | category_revenue
-- Haircare     | 54          | 44956.1
-- Skincare     | 60          | 27346.0
-- Babycare     | 30          | 16805.0
-- PersonalCare | 36          | 10753.1

SELECT
    p.category,
    COUNT(*) AS order_count,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)
    ), 2) AS category_revenue
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- ============================================================
-- (g) LIKE PATTERN MATCH
-- Find customers whose name starts with the letter 'A'.
-- ============================================================
-- Output:
-- customer_id | name
-- C001        | Aarav
-- C003        | Aditi
-- C004        | Ananya
-- C011        | Arjun
-- C021        | Aryan
-- C030        | Anika
-- C031        | Aditya
-- C036        | Aisha
-- C041        | Ayaan
-- C044        | Aria

SELECT
    customer_id,
    name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;

-- ============================================================
-- (h) DISTINCT ACQUISITION SOURCES
-- Show each unique acquisition source used by customers.
-- ============================================================

-- Output:
-- acquisition_source
-- Ad
-- Organic
-- Referral
-- Social

SELECT DISTINCT
    acquisition_source
FROM customers
ORDER BY acquisition_source;

-- ============================================================
-- (i) ALTER TABLE + UPDATE WITH CASE
-- Add a loyalty tier and assign Gold or Silver based on city tier.
-- ============================================================

-- Output:
-- loyalty_tier | customer_count
-- Gold         | 28
-- Silver       | 17

ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier = CASE
    WHEN city_tier = 1 THEN 'Gold'
    ELSE 'Silver'
END;

SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;