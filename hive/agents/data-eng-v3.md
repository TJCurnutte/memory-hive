# Data Engineering (v3)

**Author:** Data-Analyst Agent  
**Date:** 2026-04-22  
**Topics:** ETL Pipelines, Apache Airflow, dbt, Data Warehousing, Lakehouse Architecture, Apache Kafka

---

## 1. ETL Pipelines

ETL (Extract, Transform, Load) is the foundational process for moving data from source systems into a data warehouse or data lake. It is a critical competency for any data engineer and the backbone of any analytics operation.

### 1.1 The Three Stages

**Extract:** Pulling data from source systems. Sources include:
- Relational databases (PostgreSQL, MySQL, Oracle)
- SaaS APIs (Salesforce, Stripe, HubSpot, Google Analytics)
- Event streams and message queues (Kafka, Kinesis)
- File-based systems (S3, GCS, local CSV/Parquet files)
- Third-party data providers

**Transform:** Cleaning and reshaping data to fit the target schema:
- Data type conversions
- Null handling and deduplication
- Business rule application (calculating derived fields)
- Aggregations and window functions
- Slowly Changing Dimensions (SCD) handling for historical data

**Load:** Writing the transformed data to the destination:
- Full load: Replace all data in destination tables
- Incremental load: Append or upsert only new/changed records
- Historical load: Backfill historical data before turning on incremental

### 1.2 Batch ETL vs. Streaming ETL

**Batch ETL:**
- Processes data in discrete chunks at scheduled intervals (hourly, daily, weekly)
- Suited for large volumes where near-real-time freshness isn't required
- Simpler to implement, debug, and monitor
- Examples: Airflow DAGs with daily schedules, Fivetran connectors, cron jobs

**Streaming ETL (Real-Time):**
- Processes data continuously as events arrive
- Latency measured in milliseconds to minutes
- Essential for real-time dashboards, fraud detection, real-time recommendation engines
- Examples: Kafka Streams, Apache Flink, Spark Structured Streaming, AWS Kinesis

**Hybrid Approach (Lambda Architecture):**
- Combine batch and streaming: batch layer for complete, accurate results; speed layer for real-time approximations
- More complex to maintain but necessary for use cases requiring both accuracy and speed

### 1.3 Modern ETL Tooling

**Airflow (Apache):** Python-based workflow orchestrator. The de facto standard for batch ETL orchestration. See Section 2 for deep dive.

**dbt (Data Build Tool):** Transforms data already in the warehouse using SQL. Declarative, version-controlled, testable. See Section 3 for deep dive.

**Fivetran:** Fully-managed ELT connector. Automatically syncs data from 200+ sources to data warehouses. Handles extraction and loading; you handle transformation with dbt. SaaS model — minimal engineering overhead.

**Stitch:** Similar to Fivetran, open-core alternative. Uses Singer open-source specification for connectors. Good for teams that want more control over connector logic.

**Meltano:** Open-source, developer-first data ingestion. Part of the GitLab data stack philosophy. Integrates with dbt, Airflow, and other tools.

**Apache NiFi:** Visual data flow programming. Good for teams that prefer GUI-based pipeline design. Strong for data provenance, security, and flow management.

**Apache Beam / Dataflow:** Unified programming model for both batch and streaming. Google Cloud Dataflow is the managed service. Portable across execution engines (Flink, Spark, Direct Runner).

---

## 2. Apache Airflow

Apache Airflow is an open-source workflow management platform for data engineering pipelines. Originally developed at Airbnb in October 2014, it became an Apache Incubator project in March 2016 and a top-level Apache Software Foundation project in January 2019. According to VentureBeat in 2025, Airflow is the de facto tool for data engineering and has been adopted by Fortune 500 companies.

### 2.1 Core Concepts

**DAG (Directed Acyclic Graph):** The core abstraction in Airflow. A DAG is a collection of tasks and their dependencies, organized as a directed acyclic graph. No cycles allowed — tasks flow in one direction only.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_etl_pipeline',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False
)
```

**Tasks:** The atomic units of work in a DAG. Each task is an instance of an Operator.

**Operators:** Predefined task templates. Airflow ships with many built-in operators:
- `BashOperator`: Execute a bash command
- `PythonOperator`: Execute a Python function
- `PostgresOperator` / `MySqlOperator`: Execute SQL queries
- `DockerOperator`: Run a Docker container
- `HttpOperator`: Make HTTP requests
- `SlackWebhookOperator`: Send Slack notifications
- `EmptyOperator`: No-op, used for structure

**Sensors:** Special operators that wait for an external condition:
- `FileSensor`: Wait for a file to appear
- `SqlSensor`: Wait for a query to return results
- `HttpSensor`: Wait for a URL to be reachable
- `S3KeySensor`: Wait for an S3 key to exist

### 2.2 Task Dependencies

Define execution order using bitshift operators (`>>` and `<<`):

```python
extract >> transform >> load >> quality_check
quality_check >> [notify_success, notify_failure]
```

The dependency graph ensures tasks run in the correct order when the DAG executes.

### 2.3 Scheduling and Timedelta

Airflow uses cron expressions and timedelta objects for scheduling:
- `schedule_interval='@daily'` — once per day at midnight
- `schedule_interval='@hourly'` — every hour
- `schedule_interval='0 2 * * *'` — at 2:00 AM daily
- `schedule_interval='*/15 * * * *'` — every 15 minutes

**catchup:** When a DAG is turned on after its start_date, Airflow can "catch up" by running all past scheduled runs. Set `catchup=False` to skip historical runs.

**backfill:** Manually trigger historical runs with `airflow dags backfill`.

### 2.4 XCom (Cross-Communication)

XCom allows tasks to pass small amounts of data between each other:

```python
from airflow.models import XCom

# In task 1
task_instance.xcom_push(key='customer_count', value=15000)

# In task 2
customer_count = task_instance.xcom_pull(task_ids='count_customers', key='customer_count')
```

Use XCom sparingly — it's not designed for large data transfers. For large data, use external storage (S3, GCS, database tables).

### 2.5 Variables and Connections

**Airflow Variables:** Key-value store accessible from DAGs. Used for configuration:

```python
from airflow.models import Variable
env = Variable.get('environment')  # 'prod', 'staging', etc.
```

**Connections:** Store credentials and connection information for external systems. Configure via the Airflow UI or as environment variables:
```python
postgres_conn = BaseHook.get_connection('postgres_warehouse')
```

### 2.6 Deployment Options

| Option | Provider | Description |
|---|---|---|
| **Astronomer** | SaaS | Fully managed Airflow, great developer experience |
| **Amazon MWAA** | AWS | Managed Workflows for Apache Airflow, integrates with AWS services |
| **Google Cloud Composer** | GCP | Managed Airflow integrated with BigQuery, GCS, etc. |
| **Azure Airflow** | Azure | Managed Airflow as part of Azure Data Factory / Microsoft Fabric |
| **Self-hosted** | N/A | Full control, requires infrastructure management |

**Choosing a Deployment:**
- Small teams / quick experiments: Local executor or Astronomer
- AWS-centric organizations: MWAA
- GCP-centric organizations: Cloud Composer
- Enterprise with multi-cloud: Self-hosted or Astronomer

---

## 3. dbt (Data Build Tool)

dbt (data build tool) is a transformation layer that lives in the data warehouse. It allows analytics engineers to transform data using SQL, with built-in testing, documentation, and version control. dbt is not an ETL tool — it assumes data is already in your warehouse and handles the transformation step.

### 3.1 The Analytics Engineering Workflow

dbt popularized the "analytics engineering" role — a hybrid between data engineering and data analysis. Analysts can now own the transformation layer using SQL, without needing to write Python ETL code.

**Core Workflow:**
1. Connect dbt to your data warehouse (BigQuery, Snowflake, Redshift, Databricks, Postgres)
2. Define sources (tables/views already in the warehouse)
3. Build models (SQL SELECT statements that transform sources into analytical tables)
4. Test models (assertions on data quality)
5. Document models (descriptions, lineage graphs)
6. Run and schedule via dbt Cloud or CI/CD pipeline

### 3.2 Models and the ref() Function

Models are SQL files that define transformations. The `ref()` function creates lineage and dependency management:

```sql
-- models/marts/fct_orders.sql
{{ config(materialized='table') }}

SELECT
    orders.order_id,
    orders.customer_id,
    orders.order_date,
    orders.total_amount,
    customers.customer_name,
    customers.segment
FROM {{ ref('stg_orders') }} AS orders
LEFT JOIN {{ ref('stg_customers') }} AS customers
    ON orders.customer_id = customers.customer_id
WHERE orders.status = 'completed'
```

**Materializations:** Controls how models are stored in the warehouse:
- `table`: Creates/replaces as a table. Best for large final tables queried frequently.
- `view`: Creates as a view. Always reflects source data. Best for intermediate models.
- `incremental`: Appends/merges new rows on each run. Essential for large fact tables.
- `ephemeral`: Temporary table, not stored directly. Used for common CTEs shared across models.

### 3.3 Sources

Sources define the raw tables coming from upstream ETL:

```yaml
# models/sources.yml
version: 2

sources:
  - name: stripe
    database: raw_data
    schema: stripe
    tables:
      - name: charges
        description: All Stripe payment charges
      - name: customers
        description: Stripe customer records
```

Use `source()` in models:
```sql
SELECT * FROM {{ source('stripe', 'charges') }}
```

### 3.4 Testing

dbt ships with built-in schema tests:

```yaml
# models/schema.yml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

Built-in tests: `unique`, `not_null`, `accepted_values`, `relationships`, `dbt_expectations` (for more advanced tests from the dbt-expectations package).

**Custom Tests:** Write Python-based data tests for complex assertions.

### 3.5 Macros

Macros are reusable SQL fragments defined as Jinja templates:

```jinja
{# macros/calculate_ltv.sql #}
{% macro calculate_ltv(revenue_table, customer_col) %}
    SELECT
        {{ customer_col }},
        SUM(revenue) AS lifetime_revenue,
        COUNT(*) AS total_transactions,
        AVG(revenue) AS avg_order_value
    FROM {{ revenue_table }}
    GROUP BY {{ customer_col }}
{% endmacro %}
```

Then use in any model: `{{ calculate_ltv(ref('stg_revenue'), 'customer_id') }}`

### 3.6 dbt Cloud vs. dbt Core

**dbt Core (Open Source):** The CLI tool that runs locally or on any CI/CD system. Free to use. Requires your own scheduling (Airflow, Prefect, cron).

**dbt Cloud (SaaS):** Fully managed service with:
- Web-based IDE
- Scheduler and job triggering
- dbt Cloud API
- Enhanced documentation site
- Team features (git integration, review flows, SLAs)
- Free tier for small projects

---

## 4. Data Warehousing

A data warehouse is a system used for reporting and data analysis, serving as a core component of business intelligence. Data warehouses are central repositories of data integrated from disparate sources, storing current and historical data organized for analysis, report generation, and insight development.

### 4.1 Architecture Overview

The environment for data warehouses includes:
- Source systems (operational databases, SaaS APIs, third-party data)
- Data integration technology (ETL/ELT)
- Storage architecture (columnar, partitioning, clustering)
- Tools and applications for end users
- Metadata, data quality, and governance processes

**Columnar Storage:** Data warehouses store data column-by-column rather than row-by-row (OLTP style). This dramatically improves analytical query performance because aggregations only read required columns.

**MPP (Massively Parallel Processing):** Modern cloud data warehouses distribute query execution across many nodes, enabling sub-second queries on billions of rows.

### 4.2 BigQuery (Google Cloud Platform)

**Architecture:**
- Serverless, fully managed — no infrastructure to manage
- Separation of storage and compute (you pay for each independently)
- Automatic scaling — no need to provision capacity
- Slot-based pricing (compute units) or flat-rate reservations

**Key Features:**
- **Partitioning:** Divide tables by date, ingestion time, or integer range. Reduces query costs by scanning only relevant partitions.
- **Clustering:** Sort data within a partition by specific columns. Optimizes queries filtering on those columns.
- **Streaming Inserts:** Write individual rows in real-time. Useful for event-driven architectures.
- **Time Travel:** Query historical data up to 7 days (configurable) without additional storage cost.

**Pricing Model:**
- On-demand: $5.00 per TB of data scanned
- Flat-rate: Reserved slots (100, 200, 1000+) for predictable costs
- Storage: ~$0.02/GB/month for active data

**Best For:**
- Organizations already on GCP
- Ad-hoc analysis and exploration
- Large-scale data exploration without infrastructure management
- Event/streaming data with Bigtable or Pub/Sub integration

### 4.3 Snowflake

**Architecture:**
- Multi-cluster, shared data architecture
- Separate compute (virtual warehouses) from storage
- Virtual warehouses auto-scale up/down based on workload
- Services layer handles optimization, security, metadata

**Key Features:**
- **Time Travel:** Query historical data for up to 90 days (configurable). Essential for recovery and auditing.
- **Zero-Copy Cloning:** Clone databases, schemas, or tables instantly without copying data.
- **Data Sharing:** Share data between Snowflake accounts without copying — read-only access.
- **Snowpipe:** Real-time data ingestion from S3 or Azure Blob.
- **Dynamic Tables:** Declarative pipelines — define what the final table should look like, Snowflake handles recomputation.
- **Hybrid Tables:** Row-based tables optimized for single-row lookups (blending warehouse and operational workloads).

**Editions:** Standard, Enterprise, Business Critical, Performance.

**Pricing Model:**
- Credit-based (consumed per second per warehouse)
- Storage: ~$23/TB/month
- Compute: varies by warehouse size

**Best For:**
- Enterprise organizations needing strong security and compliance
- Multi-cloud or hybrid cloud strategies
- Teams that want fine-grained control over warehouse sizing and scaling

### 4.4 Databricks (Lakehouse Platform)

**Architecture:**
- Built on Apache Spark with a Lakehouse architecture
- Combines data lake flexibility with data warehouse reliability
- Unity Catalog for unified governance
- Delta Lake as the underlying storage format

**Key Features:**
- **Lakehouse Architecture:** Store data in cheap object storage (S3, GCS, ADLS) with Delta Lake ACID transactions on top
- **Notebooks:** Collaborative Python/SQL/Scala notebooks for ETL, ML, and exploration
- **Delta Live Tables:** Declarative ETL pipelines with automatic data quality management
- **Photon Engine:** Vectorized query engine for fast SQL performance
- **MLflow Integration:** Experiment tracking, model registry, and deployment for ML workloads

**Pricing Model:**
- Unit-based (DBUs) consumed per second
- VPC or serverless compute options
- Storage: managed by the organization

**Best For:**
- Organizations running Apache Spark workloads
- Teams needing unified analytics and ML on the same platform
- Lakehouse architecture adoption (Delta Lake, Apache Iceberg)
- Large-scale ML workloads alongside analytics

### 4.5 Partitioning, Clustering, and Query Optimization

These are universal concepts across all modern warehouses:

**Partitioning:** Dividing a large table into smaller, physically separate chunks based on a key (typically a date/timestamp column). Queries that filter on the partition key scan only relevant partitions, dramatically reducing cost and latency.

**Clustering:** Sorting data within each partition by one or more columns. Similar to indexing. Optimizes queries with filter conditions on the clustered columns.

**Best Practices:**
- Always filter on partition keys in queries (prevents full table scans)
- Cluster on columns frequently used in JOINs and WHERE clauses
- Avoid high-cardinality partition keys (one partition per row defeats the purpose)
- Monitor query execution plans to identify full scans

---

## 5. Data Lakehouse Architecture

The data lakehouse is a relatively new architecture pattern that combines the best of data lakes (flexibility, low cost, support for all data types) and data warehouses (reliable data management, ACID transactions, BI support).

### 5.1 The Problem with Separate Data Lakes and Warehouses

**Data Lakes Problems:**
- No ACID transactions (data corruption possible)
- No schema enforcement (garbage in, garbage out)
- Difficult to delete/update (append-only)
- Poor performance for analytical queries
- Data quality is hard to maintain

**Data Warehouse Problems:**
- Locked into proprietary formats
- High cost at petabyte scale
- Only handles structured data well
- Doesn't support ML-friendly formats natively

### 5.2 Lakehouse Architecture

The Lakehouse brings warehouse-grade reliability to the data lake:

1. **Storage Layer:** Cheaper object storage (S3, GCS, ADLS, Azure Blob) rather than proprietary warehouse storage
2. **Transaction Layer:** ACID transactions on top of object storage (prevents read/write conflicts)
3. **Table Format:** Open standard for organizing data (Delta Lake, Apache Iceberg, Apache Hudi)
4. **Query Engine:** Spark, Trino, DuckDB, Databricks, Snowflake can all query the same data

**Benefits:**
- 10x lower storage costs at petabyte scale
- Single copy of data serves BI and ML use cases
- Open formats (not vendor-locked)
- ACID transactions for data reliability
- Time travel and rollback capabilities

### 5.3 Delta Lake

Delta Lake is an open-source storage layer that brings ACID transactions to data lakes. Developed by Databricks, it runs on top of existing storage (S3, ADLS, GCS) and is format-compatible with Apache Spark.

**Key Features:**
- **ACID Transactions:** Concurrent reads and writes without data corruption
- **Scalable Metadata:** Stored as Delta transaction logs, not limited by file system
- **Time Travel:** Query historical versions of tables. Syntax: `SELECT * FROM table VERSION AS OF 3`
- **Schema Enforcement:** Prevents bad data from being written
- **Schema Evolution:** Supports adding columns safely
- **UPSERT/MERGE:** Efficiently handle updates, inserts, and deletes (critical for CDC pipelines)
- **Data Skipping:** Statistically skips data that won't match query predicates

```python
# Write with Delta Lake
df.write.format("delta").mode("overwrite").partitionBy("date").saveAsTable("sales")

# Time travel query
spark.read.format("delta").option("versionAsOf", "3").load("/path/to/table")
```

### 5.4 Apache Iceberg

Apache Iceberg is an open table format developed by Netflix and Apple, now an Apache top-level project. Unlike Delta Lake (which is tied to Spark/Databricks), Iceberg is designed to be engine-agnostic.

**Key Features:**
- **Open Specification:** Not tied to any particular engine (Spark, Trino, Flink, Hive, Snowflake all support Iceberg)
- **Hidden Partitioning:** Partition column is hidden from users; Iceberg handles partition management automatically
- **Partition Evolution:** Change partition schemes without rewriting data
- **Time Travel & Rollback:** Same as Delta Lake
- **ACID Commits:** Via snapshot isolation
- **Schema Evolution:** Safe column additions, renames, and type promotions

**Iceberg vs. Delta Lake:**
| Feature | Delta Lake | Apache Iceberg |
|---|---|---|
| Primary Maintainer | Databricks | Apache (open governance) |
| Engine Support | Spark, Databricks | Spark, Flink, Trino, Hive, Snowflake, DuckDB, more |
| Hidden Partitioning | No | Yes |
| Community | Databricks-led | Apache open governance |
| Merge Operations | Yes | Yes |
| Time Travel | Yes | Yes |

### 5.5 Apache Hudi (Hoodie)

Apache Hudi (Hoodie — Upsert, Delete, Incrementally) is another open table format with a focus on incremental processing and record-level operations. Originally developed at Uber.

**Best suited for:**
- CDC (Change Data Capture) use cases with frequent upserts
- Streaming data ingestion alongside batch
- Large-scale log data with time-series characteristics

---

## 6. Streaming Data with Apache Kafka

Apache Kafka is a distributed event store and stream-processing platform developed by the Apache Software Foundation, written in Java and Scala. Originally developed at LinkedIn and open-sourced in 2011, Kafka was created to handle LinkedIn's massive real-time event data and has since become the standard for event streaming.

According to Wikipedia: "The project aims to provide a unified, high-throughput, low-latency platform for handling real-time data feeds."

### 6.1 Core Architecture

**Brokers:** Kafka runs as a cluster of one or more servers called brokers. Each broker is identified by an integer ID. A healthy Kafka cluster typically has 3-15 brokers for production.

**Topics:** Data in Kafka is organized into topics. A topic is a category/feed name to which records are published. Topics are append-only logs.

**Partitions:** Each topic is split into partitions. Each partition is an ordered, immutable sequence of records. Partitions allow Kafka to scale horizontally — different partitions can be stored on different brokers.

**Offset:** Each record in a partition has a sequential ID called an offset. Offsets uniquely identify records within a partition.

**Producers:** Applications that publish (write) records to Kafka topics. Producers automatically route records to the correct partition (based on a partition key or round-robin).

**Consumers:** Applications that subscribe to and read records from Kafka. Consumers track their position (offset) in each partition.

**Consumer Groups:** Multiple consumers can form a group to consume a topic in parallel. Each partition is assigned to exactly one consumer in the group. If a consumer fails, Kafka rebalances partitions to the remaining consumers.

### 6.2 Key Design Decisions

**Durability Over Speed:** Kafka writes are acknowledged after the data is written to the leader replica and optionally replicated to follower replicas. This guarantees durability.

**Retention:** Unlike traditional message queues (which delete messages after consumption), Kafka retains messages for a configurable period (hours, days, or indefinitely). Consumers can replay messages from any offset.

**Partition Ordering Guarantee:** Kafka guarantees ordering within a partition, but not across partitions. For ordering guarantees across all events, use a single partition with a single consumer.

**Partition Key:** Producers can specify a key to determine which partition a record goes to. Records with the same key always go to the same partition, ensuring ordering for related events (e.g., all events for a specific customer go to the same partition).

### 6.3 Kafka Connect

Kafka Connect is a framework for reliably connecting Kafka with external systems (databases, key-value stores, search indexes, file systems).

**Connectors:** Pre-built connectors for common systems:
- **JDBC Source Connector:** Pull data from databases via change data capture or polling
- **S3 Sink Connector:** Stream data to S3 in Parquet, JSON, or Avro format
- **Elasticsearch Sink Connector:** Index Kafka data in Elasticsearch
- **Debezium:** Open-source CDC connector for MySQL, PostgreSQL, MongoDB, SQL Server

**Modes:**
- **Full dump + incremental:** Initial snapshot then ongoing changes
- **Debezium CDC:** Real-time stream of database changes as they happen

### 6.4 Kafka Streams

Kafka Streams is a client library for building stream processing applications directly within your application (no separate cluster needed). It processes data in real-time with at-least-once or exactly-once semantics.

**Key Capabilities:**
- Stateful processing (joins, aggregations, windowed computations)
- Exactly-once processing guarantees
- Event-time processing with support for late arrivals
- Interactive queries (query local state stores from your application)

```java
// Kafka Streams Word Count Example (Java)
KStream<String, String> textLines = builder.stream("plaintext-input");
KTable<String, Long> wordCounts = textLines
    .flatMapValues(line -> Arrays.asList(line.toLowerCase().split("\\W+")))
    .groupBy((key, word) -> word)
    .count(Materialized.as("counts-store"));
wordCounts.toStream().to("wordcount-output");
```

### 6.5 ksqlDB (Streaming SQL)

ksqlDB (now Confluent's ksqlDB, previously just Kafka SQL) provides a SQL interface for building streaming applications on Kafka. It allows you to create materialized views, stream tables, and run continuous queries.

**Key Concepts:**
- **STREAM:** An append-only, infinite sequence of records
- **TABLE:** A continuously updated state (like a materialized view)
- **Push Queries:** Continuous queries that push results as data arrives
- **Pull Queries:** One-time queries that return current state

```sql
-- Create a stream from a Kafka topic
CREATE STREAM pageviews (user_id VARCHAR, page VARCHAR, ts BIGINT)
WITH (kafka_topic='pageviews', value_format='JSON');

-- Continuous query: pageviews per region in a tumbling 1-hour window
SELECT region, COUNT(*) AS pageview_count
FROM pageviews
WINDOW TUMBLING (SIZE 1 HOUR)
GROUP BY region;
```

### 6.6 Real-Time Pipeline Architecture Patterns

**Pattern 1: Event Sourcing**
- Every business event is published to Kafka
- Downstream consumers maintain projections/materialized views
- The "source of truth" is the event log, not the database
- Enables replay, audit trail, and multiple independent consumers

**Pattern 2: CQRS (Command Query Responsibility Segregation)**
- Commands (writes) go to one service; Queries (reads) go to another
- Kafka acts as the event bus between them
- Write side: capture user intent as events
- Read side: build optimized read models in a separate data store

**Pattern 3: Change Data Capture (CDC)**
- Capture database changes (INSERT, UPDATE, DELETE) in real-time
- Use Debezium or proprietary tools (AWS DMS, Fivetran, Striim)
- Publish changes to Kafka topics
- Downstream consumers update data warehouses, search indexes, caches

**Pattern 4: Lambda Architecture**
- Batch layer: complete, accurate data processed in batches
- Speed layer: real-time approximate results
- Serving layer: merge batch + speed results for queries
- Complex to maintain; use Kappa Architecture instead when possible

**Pattern 5: Kappa Architecture**
- Everything is a stream
- Single code path for batch and real-time processing
- Use a single streaming system (Kafka + Flink/Spark) for all workloads
- Requires a streaming system with good replay capabilities

---

## Summary: Key Takeaways

1. **ETL vs. ELT:** Modern data stacks increasingly use ELT (extract, load, transform) — load raw data first, then transform in the warehouse with dbt. This is faster to implement, more agile, and shifts transformation to SQL.

2. **Airflow as Orchestrator:** Airflow is the standard for workflow orchestration. It manages task scheduling, dependencies, retries, and alerting. Deploy on Astronomer, MWAA, or Cloud Composer depending on your cloud provider.

3. **dbt Transforms the Analytics Engineering Role:** dbt lets analysts own the transformation layer using SQL. Build models, tests, and documentation all in code. Use dbt Cloud for scheduling or Airflow for orchestration.

4. **Choose the Right Warehouse:** BigQuery (serverless, GCP), Snowflake (enterprise-grade, multi-cloud), or Databricks (lakehouse + ML). Evaluate based on your cloud provider, scale, security requirements, and team expertise.

5. **Lakehouse is the Future:** Delta Lake and Apache Iceberg bring ACID transactions and reliability to object storage. Open table formats prevent vendor lock-in and enable engine-agnostic querying. Adopt the lakehouse architecture for new data platform projects.

6. **Kafka for Real-Time:** Kafka is the backbone of modern real-time data architectures. Use Kafka Connect for ingestion and sinks, Kafka Streams or Flink for stream processing, ksqlDB for streaming SQL. Remember Kafka is an event log, not a queue — design for replay and durability.
