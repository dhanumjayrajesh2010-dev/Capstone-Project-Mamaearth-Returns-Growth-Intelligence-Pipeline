-- Mamaearth Returns & Growth Intelligence Pipeline
-- Seed Data Loader
-- Loads the supplied CSV datasets into the SQLite database.

.mode csv

-- Make the loader re-runnable by clearing existing data
-- in child-to-parent order.
DELETE FROM orders;
DELETE FROM products;
DELETE FROM customers;

-- Load customers
.import --skip 1 data/customers.csv customers

-- Load products
.import --skip 1 data/products.csv products

-- Load orders
.import --skip 1 data/orders.csv orders

-- Convert blank CSV values to SQL NULL values.
UPDATE orders
SET discount_pct = NULL
WHERE discount_pct = '';

UPDATE orders
SET rating = NULL
WHERE rating = '';