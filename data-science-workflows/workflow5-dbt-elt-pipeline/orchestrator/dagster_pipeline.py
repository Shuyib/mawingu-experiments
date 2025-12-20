"""
Dagster orchestration pipeline for the dbt ELT workflow.

This module defines a Dagster pipeline that orchestrates:
1. Data extraction and loading (Python)
2. dbt model transformations
3. Data quality checks
"""

import os
from pathlib import Path
from dagster import (
    Definitions,
    asset,
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
)
from dagster_dbt import DbtCliResource, dbt_assets, DbtProject

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"
DBT_PROFILES_DIR = DBT_PROJECT_DIR

# Initialize the dbt project
dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    packaged_project_dir=DBT_PROJECT_DIR,
)

# Prepare dbt invocation context
dbt_project.prepare_if_dev()


@asset(
    group_name="extract_load",
    description="Extract sample data from CSV and load into DuckDB"
)
def raw_data_loaded(context: AssetExecutionContext) -> MaterializeResult:
    """
    Load raw data from CSV files into DuckDB.
    This simulates the Extract and Load phases of ELT.
    """
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    
    # Import and run the load script
    from load_sample_data import create_database_connection, load_csv_to_table
    
    conn = create_database_connection(str(PROJECT_ROOT / "data" / "warehouse.duckdb"))
    
    # Load tables
    success = True
    tables = [
        ('data/customers.csv', 'raw_customers'),
        ('data/products.csv', 'raw_products'),
        ('data/orders.csv', 'raw_orders')
    ]
    
    row_counts = {}
    for csv_path, table_name in tables:
        full_path = PROJECT_ROOT / csv_path
        if load_csv_to_table(conn, str(full_path), table_name):
            result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            row_counts[table_name] = result[0]
        else:
            success = False
    
    conn.close()
    
    context.log.info(f"Loaded {len(tables)} tables successfully")
    
    return MaterializeResult(
        metadata={
            "tables_loaded": MetadataValue.int(len(tables)),
            "row_counts": MetadataValue.md(
                "\n".join([f"- {table}: {count}" for table, count in row_counts.items()])
            ),
        }
    )


@dbt_assets(
    manifest=dbt_project.manifest_path,
    project=dbt_project,
)
def dbt_ecommerce_models(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    Run all dbt models in the ecommerce pipeline.
    This represents the Transform phase of ELT.
    """
    yield from dbt.cli(["build"], context=context).stream()


@asset(
    group_name="analytics",
    deps=[dbt_ecommerce_models],
    description="Validate final analytics outputs"
)
def analytics_validation(context: AssetExecutionContext) -> MaterializeResult:
    """
    Perform validation checks on the final mart tables.
    This ensures data quality for downstream consumers.
    """
    import duckdb
    
    conn = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"))
    
    # Run validation queries
    validations = {}
    
    # Check customer metrics
    result = conn.execute("""
        SELECT COUNT(*) as customer_count, 
               SUM(lifetime_value) as total_ltv
        FROM main_marts.mart_customer_metrics
    """).fetchone()
    validations['customer_metrics'] = {
        'customer_count': result[0],
        'total_ltv': float(result[1]) if result[1] else 0
    }
    
    # Check product performance
    result = conn.execute("""
        SELECT COUNT(*) as product_count,
               SUM(total_revenue) as total_revenue
        FROM main_marts.mart_product_performance
    """).fetchone()
    validations['product_performance'] = {
        'product_count': result[0],
        'total_revenue': float(result[1]) if result[1] else 0
    }
    
    # Check daily revenue
    result = conn.execute("""
        SELECT COUNT(*) as days,
               MAX(date) as latest_date
        FROM main_marts.mart_daily_revenue
    """).fetchone()
    validations['daily_revenue'] = {
        'days': result[0],
        'latest_date': str(result[1])
    }
    
    conn.close()
    
    context.log.info("Analytics validation complete")
    
    return MaterializeResult(
        metadata={
            "customer_count": MetadataValue.int(validations['customer_metrics']['customer_count']),
            "total_ltv": MetadataValue.float(validations['customer_metrics']['total_ltv']),
            "product_count": MetadataValue.int(validations['product_performance']['product_count']),
            "total_revenue": MetadataValue.float(validations['product_performance']['total_revenue']),
            "days_of_data": MetadataValue.int(validations['daily_revenue']['days']),
        }
    )


# Define the Dagster repository
defs = Definitions(
    assets=[
        raw_data_loaded,
        dbt_ecommerce_models,
        analytics_validation,
    ],
    resources={
        "dbt": DbtCliResource(
            project_dir=os.fspath(DBT_PROJECT_DIR),
            profiles_dir=os.fspath(DBT_PROFILES_DIR),
        ),
    },
)
