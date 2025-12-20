"""
Load sample data from CSV files into DuckDB data warehouse.

This script creates tables in DuckDB and loads the sample data,
simulating the Extract and Load phases of an ELT pipeline.
"""

import duckdb
import os


def create_database_connection(db_path='data/warehouse.duckdb'):
    """Create connection to DuckDB database."""
    conn = duckdb.connect(db_path)
    print(f"Connected to database: {db_path}")
    return conn


def load_csv_to_table(conn, csv_path, table_name):
    """Load CSV file into DuckDB table."""
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run generate_sample_data.py first.")
        return False
    
    try:
        # DuckDB can directly read CSV files
        conn.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{csv_path}')
        """)
        
        # Get row count
        result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        row_count = result[0]
        
        print(f"Loaded {row_count} rows into {table_name}")
        return True
    except Exception as e:
        print(f"Error loading {csv_path}: {str(e)}")
        return False


def create_schema(conn):
    """Create raw schema for source data."""
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
    print("Created 'raw' schema")


def verify_data(conn):
    """Verify loaded data with sample queries."""
    print("\n=== Data Verification ===")
    
    # Customer count
    result = conn.execute("SELECT COUNT(*) as customer_count FROM raw_customers").fetchone()
    print(f"Total customers: {result[0]}")
    
    # Product count by category
    print("\nProducts by category:")
    results = conn.execute("""
        SELECT category, COUNT(*) as count 
        FROM raw_products 
        GROUP BY category 
        ORDER BY count DESC
    """).fetchall()
    for row in results:
        print(f"  {row[0]}: {row[1]}")
    
    # Order statistics
    result = conn.execute("""
        SELECT 
            COUNT(*) as total_orders,
            COUNT(DISTINCT customer_id) as unique_customers,
            MIN(order_date) as earliest_order,
            MAX(order_date) as latest_order
        FROM raw_orders
    """).fetchone()
    print(f"\nOrder statistics:")
    print(f"  Total orders: {result[0]}")
    print(f"  Unique customers: {result[1]}")
    print(f"  Date range: {result[2]} to {result[3]}")


def main():
    """Main function to load all data."""
    print("Loading sample data into DuckDB...")
    
    # Create connection
    conn = create_database_connection()
    
    # Create schema
    create_schema(conn)
    
    # Load data
    success = True
    success &= load_csv_to_table(conn, 'data/customers.csv', 'raw_customers')
    success &= load_csv_to_table(conn, 'data/products.csv', 'raw_products')
    success &= load_csv_to_table(conn, 'data/orders.csv', 'raw_orders')
    
    if success:
        # Verify data
        verify_data(conn)
        print("\n✓ Data loading complete!")
    else:
        print("\n✗ Data loading failed. Please check the errors above.")
    
    # Close connection
    conn.close()


if __name__ == '__main__':
    main()
