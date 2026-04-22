# Advanced SQL — Patterns, Optimization & Data Modeling
## v3 — Data Analyst Agent Learning Document

---

## 1. WINDOW FUNCTIONS — DEEP DIVE

### 1.1 Core Syntax
```sql
window_function() OVER (
    [PARTITION BY col1, col2, ...]  -- grouping
    [ORDER BY col1 {ASC|DESC}, col2 ...]  -- ordering
    [ROWS | RANGE BETWEEN frame_start AND frame_end]  -- frame
) AS alias
```

### 1.2 Ranking Windows
```sql
-- Row number (unique, no gaps)
SELECT name, salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rn
FROM employees;

-- Rank (gaps when tied)
SELECT name, salary,
    RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- Dense rank (no gaps)
SELECT name, salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;

-- Percent rank
SELECT name, salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS pct
FROM employees;
```

### 1.3 Aggregate Windows
```sql
SELECT
    order_id,
    customer_id,
    revenue,
    -- Running total
    SUM(revenue) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total,
    -- Expanding average (cumulative to date)
    AVG(revenue) OVER (PARTITION BY customer_id ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS avg_to_date,
    -- Moving average (3-period)
    AVG(revenue) OVER (ORDER BY order_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS ma_3,
    -- Total for comparison
    SUM(revenue) OVER (PARTITION BY customer_id) AS customer_total,
    -- Percent of group total
    ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY customer_id), 2) AS pct_of_total
FROM orders;
```

### 1.4 Navigation Windows (Lag / Lead)
```sql
SELECT
    order_date,
    revenue,
    -- Previous period
    LAG(revenue, 1) OVER (ORDER BY order_date) AS prev_revenue,
    -- 7 days ago
    LAG(revenue, 7) OVER (ORDER BY order_date) AS prev_week_rev,
    -- Next period
    LEAD(revenue, 1) OVER (ORDER BY order_date) AS next_revenue,
    -- Period-over-period change
    revenue - LAG(revenue, 1) OVER (ORDER BY order_date) AS revenue_delta,
    -- % change
    ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY order_date))
        / NULLIF(LAG(revenue, 1) OVER (ORDER BY order_date), 0), 2) AS revenue_pct_chg
FROM daily_sales
ORDER BY order_date;
```

### 1.5 First / Last Values Within Window
```sql
SELECT
    employee_id,
    department,
    salary,
    -- First salary in department (ordered by hire date)
    FIRST_VALUE(salary) OVER (PARTITION BY department ORDER BY hire_date) AS dept_first_salary,
    -- Last (most recent) salary change
    LAST_VALUE(salary) OVER (PARTITION BY department
        ORDER BY hire_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS dept_last_salary,
    -- Nth value
    NTH_VALUE(salary, 2) OVER (PARTITION BY department ORDER BY salary DESC) AS dept_2nd_salary
FROM employees;
```

### 1.6 Frame Specs —ROWS vs RANGE
```sql
ROWS BETWEEN frame_start AND frame_end:
  - CURRENT ROW
  - n PRECEDING / n FOLLOWING
  - UNBOUNDED PRECEDING / UNBOUNDED FOLLOWING

RANGE BETWEEN uses logical offset — use ROWS for discrete data (rows don't repeat)

-- All rows in partition (for FIRST_VALUE/LAST_VALUE)
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
```

---

## 2. COMMON TABLE EXPRESSIONS (CTEs)

### 2.1 Basic CTE
```sql
WITH regional_sales AS (
    SELECT
        region,
        DATE_TRUNC('month', order_date) AS month,
        SUM(revenue) AS total_revenue,
        COUNT(*) AS order_count
    FROM orders
    WHERE order_date >= '2023-01-01'
    GROUP BY region, DATE_TRUNC('month', order_date)
)
SELECT * FROM regional_sales WHERE order_count > 50;
```

### 2.2 Chained CTEs
```sql
WITH
    -- Step 1: Raw regional totals
    base AS (
        SELECT region, SUM(revenue) AS total, COUNT(*) AS cnt
        FROM orders GROUP BY region
    ),
    -- Step 2: Compute averages
    stats AS (
        SELECT AVG(total) AS avg_revenue, AVG(cnt) AS avg_orders FROM base
    ),
    -- Step 3: Flag outliers
    flagged AS (
        SELECT b.*, s.avg_revenue,
            CASE WHEN b.total > s.avg_revenue * 2 THEN 'outlier' ELSE 'normal' END AS status
        FROM base b CROSS JOIN stats s
    )
SELECT * FROM flagged;
```

### 2.3 Recursive CTE
```sql
-- Organizational chart traversal
WITH RECURSIVE org_tree AS (
    -- Base case: top-level managers
    SELECT id, name, manager_id, 1 AS depth
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: subordinates
    SELECT e.id, e.name, e.manager_id, t.depth + 1
    FROM employees e
    JOIN org_tree t ON e.manager_id = t.id
    WHERE t.depth < 10  -- Prevent infinite loops
)
SELECT * FROM org_tree ORDER BY depth, name;
```

### 2.4 LATERAL JOIN (Subqueries That Can Reference Outer Rows)
```sql
SELECT p.name, p.price, s.best_seller
FROM products p
LEFT JOIN LATERAL (
    SELECT p.name AS best_seller
    FROM sales sl
    WHERE sl.product_id = p.id
    ORDER BY sl.quantity DESC
    LIMIT 1
) s ON true;
```

---

## 3. QUERY OPTIMIZATION

### 3.1 Execution Order (Know This)
```
FROM → ON/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```
**Write filters as early as possible** — WHERE before JOIN when possible.

### 3.2 Index Strategy
```sql
-- Single column
CREATE INDEX idx_orders_date ON orders(order_date);

-- Composite (leftmost prefix matters for range queries)
CREATE INDEX idx_orders_region_date ON orders(region, order_date);

-- Partial index (only rows matching filter)
CREATE INDEX idx_orders_active ON orders(order_date)
    WHERE status = 'active';

-- Covering index (includes all needed columns — no table lookup)
CREATE INDEX idx_orders_covering ON orders(customer_id, order_date)
    INCLUDE (revenue, status);

-- Pattern for window functions
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

### 3.3 EXPLAIN / EXPLAIN ANALYZE
```sql
EXPLAIN (FORMAT JSON)  -- DuckDB, Postgres
EXPLAIN ANALYZE
SELECT ...
-- Look for: Seq Scan (full table), Hash Join, Sort nodes
-- Optimize: add indexes, rewrite correlated subqueries as JOINs
```

### 3.4 Common Performance Mistakes
```sql
-- BAD: Correlated subquery (runs per row)
SELECT name, (SELECT SUM(revenue) FROM orders WHERE customer_id = c.id)
FROM customers c;

-- GOOD: JOIN (runs once)
SELECT c.name, SUM(o.revenue) AS total
FROM customers c LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;

-- BAD: Functions on indexed columns (index cannot be used)
WHERE YEAR(order_date) = 2024
WHERE LOWER(email) = 'john@example.com'  -- Unless you index the function

-- GOOD: Range on raw column
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'
WHERE email = 'john@example.com'  -- case-sensitive comparison
```

### 3.5 Partitioning Strategy
```sql
-- For large fact tables, partition by date or region
-- PostgreSQL:
CREATE TABLE orders (...) PARTITION BY RANGE (order_date);
CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- DuckDB auto-partitions for large Parquet datasets
-- Query engine reads only partitions needed (predicate pushdown)
```

### 3.6 Statistics & Autovacuum (Postgres)
```sql
ANALYZE orders;  -- Update statistics so planner picks good plans
VACUUM ANALYZE orders;  -- reclaim space + update stats
```

---

## 4. DATA MODELING — DIMENSIONAL & beyond

### 4.1 Star Schema Fundamentals
```
┌─────────────┐     ┌─────────────┐
│  dim_date   │     │  dim_product│
├─────────────┤     ├─────────────┤
│ date_pk     │     │ product_pk  │
│ year        │     │ name        │
│ month       │     │ category    │
│ quarter     │     │ brand       │
│ week        │     └─────────────┘
│ is_holiday  │
└──────┬──────┘
       │ 1:N
       ▼
┌─────────────────────────────────────────┐
│           fact_sales                    │
├─────────────────────────────────────────┤
│ order_id (PK)                           │
│ date_fk (FK → dim_date.date_pk)        │
│ product_fk (FK → dim_product.product_pk│
│ customer_fk (FK → dim_customer.id)     │
│ revenue                                 │
│ quantity                                │
│ discount                                │
└─────────────────────────────────────────┘
```

### 4.2 Slowly Changing Dimensions (SCD)
```sql
-- Type 2 SCD: keep full history with effective dates
ALTER TABLE dim_customer ADD COLUMN
    effective_from DATE DEFAULT CURRENT_DATE,
    effective_to DATE DEFAULT '9999-12-31';

-- When customer changes, close old row and insert new
WITH updated AS (
    SELECT *, CURRENT_DATE AS new_effective_from
    FROM dim_customer
    WHERE customer_key = :new_customer_key
)
UPDATE dim_customer SET effective_to = CURRENT_DATE
WHERE customer_key = :new_customer_key AND effective_to = '9999-12-31';
-- Then INSERT the new row with new_effective_from
```

### 4.3 Type 1 SCD (Overwrite)
```sql
-- Just update in place — no history
UPDATE dim_product SET brand = 'NewCo' WHERE product_id = 42;
```

### 4.4 Bridge Tables (Multi-Valued Dimensions)
```sql
-- A customer can belong to multiple segments
CREATE TABLE fact_orders (
    order_id INT PRIMARY KEY,
    order_date DATE,
    customer_fk INT REFERENCES dim_customer(customer_key)
    -- No direct segment FK — use bridge
);

CREATE TABLE bridge_customer_segment (
    customer_fk INT REFERENCES dim_customer(customer_key),
    segment_key INT REFERENCES dim_segment(segment_key),
    PRIMARY KEY (customer_fk, segment_key)
);

-- Query: all orders per segment (cross-segment attribution)
SELECT s.segment_name, SUM(f.revenue)
FROM fact_orders f
JOIN bridge_customer_segment b ON f.customer_fk = b.customer_fk
JOIN dim_segment s ON b.segment_key = s.segment_key
GROUP BY s.segment_name;
```

### 4.5 Accumulating Snapshot Fact Tables
```sql
-- For processes with defined stages (order fulfillment, loan approval)
CREATE TABLE fact_order_fulfillment (
    order_id INT,
    order_date DATE,
    ship_date DATE,
    delivery_date DATE,
    days_to_ship INT GENERATED ALWAYS AS (ship_date - order_date),
    days_to_deliver INT GENERATED ALWAYS AS (delivery_date - order_date)
);
-- Each row updated as process progresses
```

---

## 5. DBT FUNDAMENTALS

### 5.1 dbt Project Structure
```
models/
├── staging/
│   ├── stg_customers.sql      -- raw source cleaning
│   └── stg_orders.sql
├── intermediate/
│   └── int_customer_orders.sql
├── marts/
│   ├── dim_customer.sql       -- dimensional model
│   └── fact_orders.sql        -- fact table
└── macros/
    └── get_snapshot_date.sql
```

### 5.2 Staging Model
```sql
-- stg_orders.sql
{{ config(materialized='view') }}

SELECT
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['order_id']) }} AS order_key,
    -- Natural keys
    order_id AS order_id,
    customer_id AS customer_id,
    product_id AS product_id,
    -- Attributes
    order_date,
    status,
    -- Measures
    revenue,
    quantity
FROM {{ source('raw', 'orders') }}
WHERE order_date >= '2020-01-01'
```

### 5.3 Dimension Model
```sql
-- dim_customer.sql
{{ config(materialized='table') }}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
enriched AS (
    SELECT
        c.customer_key,
        c.customer_name,
        c.email,
        c.city,
        c.region,
        -- Current stats
        o.first_order_date,
        o.lifetime_value,
        o.order_count
    FROM customers c
    LEFT JOIN {{ ref('int_customer_stats') }} o ON c.customer_key = o.customer_key
)
SELECT * FROM enriched
```

### 5.4 dbt Tests
```sql
-- In schema.yml
models:
  - name: dim_customer
    description: "Customer dimension table"
    columns:
      - name: customer_key
        description: "Primary key"
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique

models:
  - name: fact_orders
    tests:
      - relationships:
          to: ref('dim_customer')
          column: customer_key
      - dbt_utils.recency:
          date: order_date
          interval: 2 days
          config:
            at_least: 1
```

### 5.5 dbt Macros
```sql
-- macros/pivot_periods.sql
{% macro pivot_revenue_by_quarter() %}
PIVOT revenue
ON quarter
USING sum(revenue) AS total_revenue
GROUP BY region
{% endmacro %}
```

### 5.6 Incremental Models
```sql
{{ config(materialized='incremental') }}

SELECT
    order_id,
    order_date,
    customer_id,
    revenue
FROM {{ source('raw', 'orders') }}
{% if is_incremental() %}
    WHERE order_date > (SELECT MAX(order_date) FROM this)
{% endif %}
```

### 5.7 Data Freshness
```sql
-- In dbt_project.yml
vars:
  dat_freshness:
    orders:
      fqn: raw.orders
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
```

---

## 6. ADVANCED ANALYTICAL QUERIES

### 6.1 Cohort Analysis
```sql
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', first_purchase_date) AS cohort_month,
        order_date,
        DATE_TRUNC('month', order_date) AS order_month,
        EXTRACT(MONTH FROM AGE(order_date, first_purchase_date)) + 1 AS months_since_signup
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_count
    FROM cohorts GROUP BY cohort_month
),
retention AS (
    SELECT
        cohort_month,
        months_since_signup,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM cohorts
    GROUP BY cohort_month, months_since_signup
)
SELECT
    r.cohort_month,
    r.months_since_signup,
    r.active_customers,
    cs.cohort_count,
    ROUND(100.0 * r.active_customers / cs.cohort_count, 1) AS retention_rate
FROM retention r
JOIN cohort_size cs ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.months_since_signup;
```

### 6.2 Gap Analysis (Sessionization)
```sql
-- Identify sessions by user (30-min gap = new session)
WITH sessions AS (
    SELECT
        user_id,
        event_time,
        event_type,
        SUM(new_session_flag) OVER (ORDER BY user_id, event_time) AS session_id
    FROM (
        SELECT *,
            CASE WHEN event_time - LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time)
                > INTERVAL '30 minutes' THEN 1 ELSE 0 END AS new_session_flag
        FROM events
    )
)
SELECT
    user_id, session_id,
    MIN(event_time) AS session_start,
    MAX(event_time) AS session_end,
    COUNT(*) AS event_count,
    EXTRACT(EPOCH FROM MAX(event_time) - MIN(event_time)) AS session_duration_sec
FROM sessions
GROUP BY user_id, session_id;
```

### 6.3 Funnel Analysis
```sql
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event = 'page_view' THEN 1 END) AS saw_page,
        MAX(CASE WHEN event = 'add_to_cart' THEN 1 END) AS added_cart,
        MAX(CASE WHEN event = 'checkout' THEN 1 END) AS checked_out,
        MAX(CASE WHEN event = 'purchase' THEN 1 END) AS purchased
    FROM events
    GROUP BY user_id
)
SELECT
    COUNT(*) AS total_users,
    COUNT(CASE WHEN saw_page = 1 THEN 1 END) AS step1_page,
    COUNT(CASE WHEN added_cart = 1 THEN 1 END) AS step2_cart,
    COUNT(CASE WHEN checked_out = 1 THEN 1 END) AS step3_checkout,
    COUNT(CASE WHEN purchased = 1 THEN 1 END) AS step4_purchase,
    ROUND(100.0 * COUNT(CASE WHEN purchased = 1 THEN 1 END) / COUNT(*), 2) AS overall_cv_rate
FROM funnel;
```

### 6.4 Time-Weighted Metrics (Running Average)
```sql
-- Weighted average revenue per day, with decay
SELECT
    date,
    revenue,
    -- Equal-weight 7-day moving average
    AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7,
    -- Exponential moving average (alpha=0.3)
    AVG(revenue) OVER (ORDER BY date) AS ema_approx
FROM daily_metrics
ORDER BY date;
```

---

## 7. QUALITY & GOVERNANCE

### 7.1 Zero-Null Guarantee in Critical Columns
```sql
ALTER TABLE dim_customer
ALTER COLUMN customer_key SET NOT NULL;
```

### 7.2 Constraints
```sql
ALTER TABLE fact_orders ADD CONSTRAINT chk_revenue_positive
    CHECK (revenue >= 0);
ALTER TABLE dim_customer ADD CONSTRAINT chk_valid_region
    CHECK (region IN ('Northeast', 'Southeast', 'Midwest', 'Southwest', 'West'));
```

### 7.3 Testing with Great Expectations / dbt Tests
```sql
-- dbt_utils expression tests
models:
  - name: fact_orders
    columns:
      - name: revenue
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min: 0
              max: 1000000
```

---

## 8. BEST PRACTICES

1. **Always use aliases** on tables — clarity and self-documenting
2. **Use CTEs over subqueries** — CTEs are readable, reusable, and composable
3. **Prefer window functions over correlated subqueries** — single-pass vs multi-pass
4. **Date truncate at ingestion** — avoid repeated DATE_TRUNC in queries
5. **Materialize intermediate models** in dbt — don't recompute every run
6. **Document your grain** — each table should have one row per X (e.g., order_id)
7. **Test upstream sources** — null %, distinct counts, freshness
8. **Use PARTITION BY wisely** — partitioning groups your window; use for cohort comparisons
9. **QUALIFY is underrated** — FILTER or QUALIFY cleans up ranked subqueries
10. **Index on access patterns** — queries that filter on (date, region) should have composite index on both

---

*Last updated: 2026-04-22 | Agent: Data-Analyst | Context: SQL, dbt, data modeling*
