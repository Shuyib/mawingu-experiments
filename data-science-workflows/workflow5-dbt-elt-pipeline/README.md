# Workflow 5: dbt-based ELT Pipeline

This workflow demonstrates a modern data engineering pipeline using dbt (data build tool) for transformations, DuckDB as the data warehouse, and Dagster for orchestration.

## Architecture Overview

```
Raw Data Sources (CSV) 
    ↓
Extract & Load (Python)
    ↓
DuckDB (Data Warehouse)
    ↓
dbt Transformations (Staging → Intermediate → Mart)
    ↓
Analysis-Ready Datasets
    ↓
Visualization & Queries
```

### Pipeline Layers:

1. **Staging Layer**: Raw data ingestion with minimal transformations
2. **Intermediate Layer**: Business logic and data cleaning
3. **Mart Layer**: Aggregated, analysis-ready datasets for analytics

## What This Demonstrates

- **Modern Data Stack**: dbt + DuckDB + Python orchestration
- **Data Quality**: Built-in tests and expectations
- **Scalability**: Modular design for production workloads
- **Best Practices**: Documentation, version control, testing
- **ELT Pattern**: Extract-Load-Transform approach

## Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- kubectl (optional, for Kubernetes deployment)

## Setup

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using pipenv
pipenv install
pipenv shell
```

### 2. Initialize the Data Warehouse

```bash
# Load sample data into DuckDB
python scripts/load_sample_data.py
```

### 3. Run dbt Models

```bash
# Navigate to dbt project
cd dbt_project

# Install dbt dependencies
dbt deps

# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

### 4. Run with Dagster Orchestration

```bash
# Start Dagster UI
dagster dev -f orchestrator/dagster_pipeline.py

# Open browser to http://localhost:3000
# Materialize the pipeline from the UI
```

## Project Structure

```
workflow5-dbt-elt-pipeline/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── Pipfile                        # Pipenv dependencies
├── Makefile                       # Common commands
├── Dockerfile                     # Container definition
├── deployments.yaml               # Kubernetes manifest
├── data/                          # Sample raw data
│   ├── customers.csv
│   ├── orders.csv
│   └── products.csv
├── scripts/                       # ETL scripts
│   ├── load_sample_data.py       # Load data to DuckDB
│   └── generate_sample_data.py   # Generate sample datasets
├── dbt_project/                   # dbt project
│   ├── dbt_project.yml           # dbt configuration
│   ├── profiles.yml              # Database connection
│   ├── models/                   # dbt models
│   │   ├── staging/             # Raw data models
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_orders.sql
│   │   │   └── stg_products.sql
│   │   ├── intermediate/        # Business logic
│   │   │   ├── int_order_items.sql
│   │   │   └── int_customer_orders.sql
│   │   └── marts/              # Analytics-ready
│   │       ├── mart_customer_metrics.sql
│   │       ├── mart_product_performance.sql
│   │       └── mart_daily_revenue.sql
│   ├── tests/                   # Custom tests
│   └── macros/                  # Reusable SQL
├── orchestrator/                 # Dagster orchestration
│   ├── dagster_pipeline.py      # Pipeline definition
│   └── __init__.py
├── queries/                      # Example analytical queries
│   ├── customer_analysis.sql
│   └── product_performance.sql
└── notebooks/                    # Visualization examples
    └── visualization_demo.ipynb
```

## Key Concepts

### dbt Models

**Staging Models** (`stg_*`):
- One-to-one with source tables
- Minimal transformations (type casting, renaming)
- Source of truth for downstream models

**Intermediate Models** (`int_*`):
- Complex business logic
- Join multiple staging models
- Not exposed to end users

**Mart Models** (`mart_*`):
- Aggregated, denormalized
- Optimized for specific analytics use cases
- What analysts/dashboards query

### Data Quality

dbt provides several testing mechanisms:
- **Schema tests**: uniqueness, not_null, accepted_values, relationships
- **Custom tests**: Complex business logic validation
- **Data quality checks**: Row counts, freshness, distribution

### Orchestration with Dagster

Dagster provides:
- **Asset-based orchestration**: Models as data assets
- **Dependency management**: Automatic DAG creation
- **Observability**: Logs, metrics, lineage
- **Scheduling**: Run pipelines on schedule or event

## Usage Examples

### Run Specific Models

```bash
# Run only staging models
dbt run --select staging

# Run one model and its dependencies
dbt run --select +mart_customer_metrics

# Run models that changed
dbt run --select state:modified+
```

### Test Data Quality

```bash
# Run all tests
dbt test

# Test specific model
dbt test --select stg_orders

# Test specific criteria
dbt test --select test_type:unique
```

### Query Analysis

```bash
# Connect to DuckDB
python -c "import duckdb; conn = duckdb.connect('data/warehouse.duckdb'); print(conn.execute('SELECT * FROM mart_customer_metrics LIMIT 5').fetchdf())"
```

## Visualization Setup

The pipeline outputs can be visualized using:
- **Jupyter notebooks**: See `notebooks/visualization_demo.ipynb`
- **BI Tools**: Connect DuckDB to Metabase, Superset, etc.
- **Custom dashboards**: Flask/Streamlit apps

## Docker Deployment

```bash
# Build image
make build

# Run container
make run

# Or manually
docker build -t workflow5-dbt-elt .
docker run -p 3000:3000 workflow5-dbt-elt
```

## Kubernetes Deployment

```bash
# Deploy to cluster
kubectl apply -f deployments.yaml

# Check status
kubectl get pods -l app=dbt-pipeline

# View logs
kubectl logs -f <pod-name>
```

## Production Considerations

1. **Data Warehouse**: Switch from DuckDB to Snowflake/BigQuery/Redshift
2. **Secrets Management**: Use environment variables or secret managers
3. **CI/CD**: Add GitHub Actions for dbt testing
4. **Monitoring**: Add data observability tools
5. **Incremental Models**: Use `incremental` materialization for large datasets
6. **Documentation**: Keep dbt docs up-to-date

## Extending This Workflow

- Add more data sources (APIs, databases, cloud storage)
- Implement incremental loading strategies
- Add data quality monitoring with Great Expectations
- Integrate with ML pipelines (feature engineering)
- Add real-time streaming with Kafka/Flink

## Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [Dagster Documentation](https://docs.dagster.io/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Analytics Engineering Guide](https://www.getdbt.com/analytics-engineering/)

## Comparison with Other Workflows

- **workflow3**: Focuses on data generation and real-time plotting
- **workflow4**: API-based ML inference
- **workflow5**: Complete ELT pipeline with orchestration and testing

This workflow demonstrates enterprise-grade data engineering practices suitable for production environments.
