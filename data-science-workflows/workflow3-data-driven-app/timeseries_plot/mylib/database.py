import sqlite3
import logging
import pandas as pd
import os
from contextlib import contextmanager
from mylib.dataloader import download_file_s3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@contextmanager
def database_connection(db_path, timeout=30):
    """Context manager for database connections with proper cleanup
    
    Parameters
    ----------
    db_path : str
        Path to the SQLite database file
    timeout : int
        Database lock timeout in seconds (default: 30)
    
    
    Yields
    ------
    sqlite3.Connection
        Database connection object
    
    
    Example
    -------
    with database_connection("timeseries_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM timeseries")
    
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=timeout)
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
            logger.error("Transaction rolled back due to error")
        raise
    finally:
        if conn:
            conn.close()


def init_database(db_path):
    """Initialize SQLite database with timeseries table

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file


    Returns
    -------
    Boolean True/False
    True if database initialized successfully.
    False if initialization failed with an error message.


    Example
    -------
    init_database("timeseries_data.db") creates a database with timeseries table

    """
    try:
        with database_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS timeseries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            # Create index for performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timeseries_x_y 
                ON timeseries(x, y)
            """
            )
            logger.info("Database initialized successfully with indexes")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        return False


def load_s3_to_database(filename, db_path, chunk_size=10000):
    """Download data from S3 and insert only new data into SQLite database

    This function optimizes data loading by checking for existing records
    and only inserting new data points, preventing duplicates and speeding
    up the application when handling large datasets. Uses chunked loading
    for memory efficiency with large files.

    Parameters
    ----------
    filename : str
        Name of the file to download from S3
    db_path : str
        Path to the SQLite database file
    chunk_size : int
        Number of rows to process at a time for large files (default: 10000)


    Returns
    -------
    Boolean True/False
    True if data loaded successfully into database.
    False if loading failed with an error message.

    NB: You need to have stored the endpointurl, region_name, aws_access_key_id,
    and aws_secret_access_key and spaces name from Digital ocean as environment
    variables e.g export SPACES_NAME=<nameofspace>


    Example
    -------
    load_s3_to_database("data.csv", "timeseries_data.db") downloads CSV from S3
    and inserts only new data into database

    """
    try:
        # Download file from S3
        logger.info(f"Downloading {filename} from S3")
        download_result = download_file_s3(filename)
        if download_result is False or download_result is None:
            logger.error("Failed to download file from S3")
            return False

        # Validate file exists after download
        if not os.path.isfile(filename):
            logger.error(f'File "{filename}" not found after download')
            return False

        # Read CSV file with validation
        try:
            df_new = pd.read_csv(filename)
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file {filename} is empty")
            return False
        except Exception as e:
            logger.error(f"Error reading CSV file {filename}: {e}")
            return False
        
        # Validate CSV has required columns
        if df_new.empty:
            logger.warning(f"CSV file {filename} contains no data rows")
            return True  # Not an error, just no data to insert
        
        if 'x' not in df_new.columns or 'y' not in df_new.columns:
            logger.error(f"CSV file {filename} missing required columns 'x' or 'y'")
            return False

        with database_connection(db_path) as conn:
            # Check if database has existing data
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM timeseries")
            existing_count = cursor.fetchone()[0]

            if existing_count > 0:
                # Load existing data to identify duplicates
                df_existing = pd.read_sql_query("SELECT x, y FROM timeseries", conn)

                # Find new records using merge (more efficient than apply+lambda)
                # Use indicator to mark records only in df_new (left_only)
                df_merged = df_new.merge(
                    df_existing, on=["x", "y"], how="left", indicator=True
                )
                df_to_insert = df_merged[df_merged["_merge"] == "left_only"][["x", "y"]]

                if len(df_to_insert) > 0:
                    # Use chunked insertion for large datasets
                    if len(df_to_insert) > chunk_size:
                        logger.info(f"Using chunked insertion for {len(df_to_insert)} records")
                        for i in range(0, len(df_to_insert), chunk_size):
                            chunk = df_to_insert.iloc[i:i+chunk_size]
                            chunk.to_sql("timeseries", conn, if_exists="append", index=False)
                            logger.info(f"Inserted chunk {i//chunk_size + 1} ({len(chunk)} records)")
                    else:
                        df_to_insert.to_sql("timeseries", conn, if_exists="append", index=False)
                    
                    logger.info(
                        f"Inserted {len(df_to_insert)} new records (skipped {len(df_new) - len(df_to_insert)} duplicates)"
                    )
                else:
                    logger.info("No new records to insert, all data already exists")
            else:
                # No existing data, insert all records with chunking if necessary
                if len(df_new) > chunk_size:
                    logger.info(f"Using chunked insertion for {len(df_new)} records")
                    for i in range(0, len(df_new), chunk_size):
                        chunk = df_new.iloc[i:i+chunk_size]
                        chunk[["x", "y"]].to_sql("timeseries", conn, if_exists="append", index=False)
                        logger.info(f"Inserted chunk {i//chunk_size + 1} ({len(chunk)} records)")
                else:
                    df_new[["x", "y"]].to_sql("timeseries", conn, if_exists="append", index=False)
                
                logger.info(f"Inserted {len(df_new)} records into empty database")

        # Clean up CSV file after loading to database
        try:
            os.remove(filename)
            logger.info(f"Cleaned up downloaded file: {filename}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {filename}: {e}")

        return True
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            logger.error(f"Database is locked. Another process may be using it: {e}")
        else:
            logger.error(f"Database operational error: {e}")
        return False
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        return False


def query_timeseries_data(db_path):
    """Query data from database and return as pandas DataFrame

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file


    Returns
    -------
    pandas.DataFrame
    DataFrame containing x and y columns from timeseries table.
    Returns empty DataFrame if query fails.


    Example
    -------
    df = query_timeseries_data("timeseries_data.db") returns DataFrame with
    timeseries data

    """
    try:
        with database_connection(db_path) as conn:
            df = pd.read_sql_query("SELECT x, y FROM timeseries", conn)
            logger.info(f"Successfully queried {len(df)} records from database")
            return df
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            logger.error(f"Database is locked. Another process may be using it: {e}")
        else:
            logger.error(f"Database operational error: {e}")
        return pd.DataFrame()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error querying data: {e}")
        return pd.DataFrame()
