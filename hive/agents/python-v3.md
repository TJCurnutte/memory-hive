# Python Data Analysis — Advanced Patterns & Workflows
## v3 — Data Analyst Agent Learning Document

---

## 1. PANDAS ADVANCED PATTERNS

### 1.1 Method Chaining with Pipe
```python
import pandas as pd
import numpy as np

# Clean pipeline — no intermediate variables
df = (pd.read_csv("sales.csv")
      .pipe(lambda d: d.assign(date=pd.to_datetime(d['date'])))
      .assign(year=lambda d: d['date'].dt.year)
      .query('revenue > 0')
      .dropna(subset=['customer_id'])
      .groupby(['year', 'region'])
      .agg(revenue=('amount', 'sum'),
           orders=('id', 'count'))
      .reset_index()
      .sort_values('revenue', ascending=False))
```

### 1.2 Advanced GroupBy with Named Aggregation
```python
summary = df.groupby('department').agg(
    avg_salary=('salary', 'mean'),
    headcount=('employee_id', 'count'),
    max_salary=('salary', 'max'),
    min_seniority=('years', 'min')
).round(2)
```

### 1.3 Transform vs. Aggregate — When to Use Each
```python
# AGGREGATE: one row per group
grouped = df.groupby('region')['revenue'].sum()

# TRANSFORM: same row count, group stat broadcast back
df['region_avg'] = df.groupby('region')['revenue'].transform('mean')
df['pct_of_region'] = df['revenue'] / df.groupby('region')['revenue'].transform('sum')

# Ranking within groups
df['rank_in_region'] = df.groupby('region')['revenue'].rank(ascending=False, method='dense')
```

### 1.4 Rolling & Expanding Windows
```python
df = df.sort_values('date')
df['revenue_7d'] = df.groupby('store')['revenue'].transform(
    lambda x: x.rolling(window=7, min_periods=1).mean()
)
df['revenue_30d'] = df.groupby('store')['revenue'].transform(
    lambda x: x.rolling(window='30D', min_periods=1, on='date').mean()
)
# Expanding (cumulative to date)
df['cumulative_revenue'] = df.groupby('store')['revenue'].transform('expanding').mean()
```

### 1.5 MultiIndex Operations
```python
# Set hierarchical index
df = df.set_index(['region', 'product_category', 'date']).sort_index()

# Partial slice on multi-index
slice_ = df.loc['Northeast':'Southwest', 'Electronics']
# Cross-section
xs = df.xs('2024', level='date', drop_level=False)

# Unstack for wide format
pivot = df.unstack(fill_value=0)
# Stack back to long
long = pivot.stack()
```

---

## 2. POLARS — THE MODERN ALTERNATIVE

### 2.1 Why Polars Over Pandas
- **30x+ faster** on large datasets (benchmarked against TPC-H)
- **Lazy evaluation** — query optimizer plans execution before running
- **Multi-threaded by default** — no GIL bottlenecks
- **Apache Arrow** native — zero-copy interop with the data ecosystem
- **Out-of-core** processing for datasets larger than RAM

### 2.2 Core API Patterns
```python
import polars as pl

df = pl.read_csv("sales.csv")
df = pl.scan_csv("sales.csv")  # Lazy — just plans the query

# Eager operations
result = (df
    .filter(pl.col('revenue') > 0)
    .with_columns([
        pl.col('date').str.to_date(),
        pl.col('revenue').round(2)
    ])
    .group_by(['year', 'region'])
    .agg([
        pl.col('revenue').sum().alias('total_revenue'),
        pl.col('id').count().alias('order_count'),
        pl.col('revenue').mean().alias('avg_revenue')
    ])
    .sort('total_revenue', descending=True)
)
```

### 2.3 Lazy Mode — The Power Move
```python
lazy_df = pl.scan_csv("huge_file.csv")  # No data loaded yet

query = (lazy_df
    .filter(pl.col('status') == 'active')
    .join(pl.scan_csv("customers.csv"), on='customer_id', how='left')
    .group_by('segment')
    .agg(pl.col('amount').sum().alias('total'))
    .sort('total', descending=True)
)

# Explain shows the plan
print(query.explain())

# Execute only when needed
result = query.collect()  # Runs the plan
```

### 2.4 Polars Expressions — Deep Power
```python
# Conditional logic
.with_columns([
    pl.when(pl.col('score') >= 80).then('A')
      .when(pl.col('score') >= 60).then('B')
      .otherwise('C').alias('grade')
])

# String operations
.with_columns([
    pl.col('email').str.to_lowercase(),
    pl.col('phone').str.replace_all(r'\D', '').cast(pl.Int64),
    pl.col('name').str.contains('Corp').alias('is_corporate')
])

# Date handling
.with_columns([
    pl.col('timestamp').dt.year().alias('year'),
    pl.col('timestamp').dt.truncate('1mo').alias('month_start'),
    pl.col('timestamp').dt.week().alias('week_num')
])

# Window functions over subsets
.with_columns([
    pl.col('revenue').mean().over('customer_id').alias('customer_avg'),
    pl.col('revenue').rank('desc').over('region').alias('rank_in_region')
])
```

### 2.5 Polars DataFrame → pandas / Arrow
```python
# To pandas
pandas_df = df.to_pandas()

# To Arrow (zero-copy)
arrow_table = df.to_arrow()

# From Arrow
pl_from_arrow = pl.from_arrow(arrow_table)

# To NumPy
np_array = df.to_numpy()
```

---

## 3. DUCKDB — SQL THE MODERN WAY

### 3.1 Why DuckDB
- **In-process OLAP** — no server, no setup, runs anywhere
- **Lakes-native** — query Parquet, JSON, CSV, S3, Iceberg directly
- **40+ native clients** — Python, R, Node.js, Go, Rust, Java, CLI
- **Postgres-compatible** — friendly SQL dialect with modern features
- **Spills to disk** — handles datasets larger than RAM

### 3.2 Core Operations
```sql
-- Read from remote files directly (no download needed)
SELECT * FROM 's3://my-bucket/data.parquet';
SELECT * FROM read_csv_auto('https://example.com/data.csv');

-- Read from multiple files at once
SELECT * FROM read_parquet(['file1.parquet', 'file2.parquet', 'file3.parquet']);

-- Register a table over a folder of files
CREATE TABLE sales AS SELECT * FROM 'data/sales/*.parquet';
```

### 3.3 Advanced SQL in DuckDB
```sql
-- PIVOT (recent DuckDB feature)
PIVOT sales_data
ON quarter
USING sum(revenue), count(*)
GROUP BY region
ORDER BY region;

-- AS OF join (time-series merge)
SELECT a.timestamp, a.price, b.volume
FROM prices a ASOF JOIN volumes b
ON a.timestamp >= b.timestamp
ORDER BY a.timestamp;

-- GROUP BY ALL
SELECT region, category, year, SUM(revenue) AS total
FROM sales GROUP BY ALL;

-- Conditional aggregation
SELECT
    region,
    SUM(revenue) FILTER (WHERE quarter = 'Q1') AS q1_rev,
    AVG(revenue) FILTER (WHERE quarter IN ('Q1', 'Q2')) AS h1_avg
FROM sales GROUP BY region;

-- QUALIFY (window function filter)
SELECT region, product, revenue,
    RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS rank
FROM sales
QUALIFY rank <= 3;  -- Top 3 per region

-- DISTINCT ON (first row per group)
SELECT DISTINCT ON (customer_id) *
FROM orders
ORDER BY customer_id, order_date DESC;
```

### 3.4 DuckDB + Python Integration
```python
import duckdb

con = duckdb.connect()
# Query pandas DataFrame directly with SQL
result = con.sql("""
    SELECT region, SUM(revenue) AS total
    FROM df
    WHERE year = 2024
    GROUP BY region
    ORDER BY total DESC
""").fetchdf()

# Register a DataFrame as a table
con.register("customers", pandas_df)

# DuckDB as a pandas accelerator
con.execute("INSTALL pandas; LOAD pandas;")
```

### 3.5 Performance Tips
- Use **Parquet** for large files (columnar, compressed)
- Use **列式存储** for aggregations; row-wise for small tables
- Enable **parallelism**: `SET threads=8`
- Use **projection pushdown** — DuckDB only reads needed columns
- Use **filter pushdown** — predicates applied at file scan time

---

## 4. DATETIME & TIME-SERIES HANDLING

### 4.1 Pandas Datetime
```python
# Parse dates at read time (avoid reprocessing)
df = pd.read_csv("data.csv", parse_dates=['date'], dayfirst=False)

# Time zone handling
df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert('America/New_York')

# Resampling (Pandas)
monthly = df.set_index('date').resample('ME')['revenue'].agg(['sum', 'mean', 'count'])

# Custom fiscal year
df['fiscal_year'] = df['date'].dt.where(
    df['date'].dt.month >= 7,
    df['date'].dt.year,
    df['date'].dt.year - 1
).astype(str) + '-' + df['date'].dt.where(
    df['date'].dt.month >= 7,
    (df['date'].dt.year + 1).astype(str).str[-2:],
    df['date'].dt.year.astype(str).str[-2:]
)
```

### 4.2 Polars Datetime
```python
df = df.with_columns([
    pl.col('timestamp').str.to_datetime("%Y-%m-%d %H:%M:%S"),
    pl.col('timestamp').dt.truncate('1w').alias('week_start'),
    pl.col('timestamp').dt.total_days().alias('days_since_epoch')
])
```

---

## 5. DATA CLEANING — PRODUCTION PATTERNS

### 5.1 Type Enforcement Pipeline
```python
dtypes = {
    'id': 'int64',
    'revenue': 'float64',
    'date': 'datetime64[ns]',
    'region': 'category',
    'is_active': 'bool'
}
df = df.astype(dtypes)
```

### 5.2 Robust Null Handling
```python
# Strategy by data type
df['revenue'] = df['revenue'].fillna(0)  # Numeric: zero or mean/median
df['notes'] = df['notes'].fillna('')       # String: empty
df['score'] = df['score'].fillna(df.groupby('category')['score'].transform('median'))

# Forward-fill for time series
df['price'] = df.sort_values('timestamp').groupby('instrument')['price'].ffill()

# Drop rows/cols with too many nulls
threshold = len(df) * 0.5
df = df.dropna(thresh=threshold, axis=1)
df = df.dropna(subset=['critical_col', 'another_critical'])
```

### 5.3 Outlier Detection
```python
def flag_outliers(series, method='iqr', n_std=3):
    if method == 'iqr':
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        return (series < q1 - 1.5*iqr) | (series > q3 + 1.5*iqr)
    elif method == 'zscore':
        z = (series - series.mean()) / series.std()
        return z.abs() > n_std

df['revenue_outlier'] = flag_outliers(df['revenue'])
```

### 5.4 Fuzzy Matching / Deduplication
```python
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Deduplicate with threshold
df = df.sort_values('updated_at', ascending=False).drop_duplicates(subset=['email'], keep='first')
```

---

## 6. JUPYTER WORKFLOWS & EXPLORATION

### 6.1 Quick EDA Snippet
```python
def eda(df):
    print(f"Shape: {df.shape}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\nNulls:\n{df.isnull().sum()}")
    print(f"\nNumeric stats:\n{df.describe()}")
    print(f"\nTop values:\n{df.describe(include='object').iloc[1]}")

# Correlation matrix
import seaborn as sns
import matplotlib.pyplot as plt

numeric_cols = df.select_dtypes(include='number').columns
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.tight_layout()
```

### 6.2 Pandas Profile Report
```python
# Install: pip install pandas-profiling
from pandas_profiling import ProfileReport

profile = ProfileReport(df, title="Sales Data EDA", explorative=True)
profile.to_file("sales_eda.html")
```

---

## 7. PERFORMANCE OPTIMIZATION

### 7.1 When to Use Each Tool
| Scenario | Tool |
|---|---|
| < 100K rows, ad-hoc analysis | Pandas |
| 100K–100M rows, ETL pipelines | Polars |
| > 100M rows, full DB with joins | DuckDB |
| Cloud lakehouse, S3 data | DuckDB |
| Interactive dashboard backend | Polars |
| ML preprocessing | Pandas / Polars |

### 7.2 Memory Optimization
```python
# Downcast numeric types
df = df.apply(pd.to_numeric, errors='coerce')
# Use nullable integers
df['col'] = df['col'].astype('Int64')  # Capital I = nullable

# Use category dtype for low-cardinality strings
df['region'] = df['region'].astype('category')

# Sparse columns
from scipy.sparse import csr_matrix
```

### 7.3 Chunked Processing (Large Files)
```python
# Polars — streaming mode
result = (pl.scan_csv("huge.csv")
    .group_by('region')
    .agg(pl.col('revenue').sum())
    .collect(streaming=True))  # Memory-efficient

# Pandas — chunked
chunks = pd.read_csv("huge.csv", chunksize=100_000)
results = []
for chunk in chunks:
    processed = chunk.groupby('region')['revenue'].sum()
    results.append(processed)
final = pd.concat(results).groupby(level=0).sum()
```

---

## 8. INTEGRATION PATTERNS

### 8.1 Polars + Streamlit
```python
import streamlit as st
import polars as pl

@st.cache_data
def load_data():
    return pl.read_csv("sales.csv")

st.title("Sales Dashboard")
df = load_data()

# Interactive filter
regions = st.multiselect("Select regions", df['region'].unique().to_list())
filtered = df.filter(pl.col('region').is_in(regions))

st.dataframe(filtered)
```

### 8.2 DuckDB + dbt
```python
# Use DuckDB as a local development target for dbt
# profiles.yml:
profiles:
  local:
    outputs:
      dev:
        type: duckdb
        path: ./dev.duckdb
        schema: analytics
```

### 8.3 Apache Arrow Ecosystem
```python
import pyarrow as pa
import pyarrow.parquet as pq

# Write Parquet with Arrow
table = pa.Table.from_pandas(df)
pq.write_to_dataset(table, root_path='s3://bucket/data/', partition_cols=['year', 'month'])
```

---

## 9. BEST PRACTICES

1. **Choose the right tool for the scale** — Pandas for exploration, Polars for production pipelines, DuckDB for analytical queries on large data
2. **Prefer lazy evaluation** in Polars — it catches errors before execution and optimizes the plan
3. **Use GROUP BY ALL** — DuckDB and modern SQL dialects support it; reduces boilerplate
4. **Normalize dates at ingestion** — store as datetime64, never as strings
5. **Partition large datasets** — by date or region, for selective queries
6. **Prefer Parquet over CSV** — 10x smaller, columnar, type-preserving
7. **Cache expensive operations** — `st.cache_data`, DuckDB materialized views, Polars lazy plans
8. **Test transformations** — compare before/after row counts, null counts, value ranges

---

*Last updated: 2026-04-22 | Agent: Data-Analyst | Context: Python ecosystem, Polars, DuckDB*
