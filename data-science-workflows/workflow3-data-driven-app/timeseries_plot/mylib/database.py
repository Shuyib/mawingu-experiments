import sqlite3
import logging
import pandas as pd
import os
from mylib.dataloader import download_file_s3


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
        conn = sqlite3.connect(db_path)
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
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logging.error(e)
        return False


def load_s3_to_database(filename, db_path):
    """Download data from S3 and insert only new data into SQLite database

    This function optimizes data loading by checking for existing records
    and only inserting new data points, preventing duplicates and speeding
    up the application when handling large datasets.

    Parameters
    ----------
    filename : str
        Name of the file to download from S3
    db_path : str
        Path to the SQLite database file


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
        download_result = download_file_s3(filename)
        if download_result is False or download_result is None:
            logging.error("Failed to download file from S3")
            return False

        # Read CSV file
        assert os.path.isfile(filename), '"{}" is not a valid path'.format(filename)
        df_new = pd.read_csv(filename)

        conn = sqlite3.connect(db_path)

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
                df_to_insert.to_sql("timeseries", conn, if_exists="append", index=False)
                logging.info(
                    "Inserted %d new records (skipped %d duplicates)",
                    len(df_to_insert),
                    len(df_new) - len(df_to_insert),
                )
            else:
                logging.info("No new records to insert, all data already exists")
        else:
            # No existing data, insert all records
            df_new.to_sql("timeseries", conn, if_exists="append", index=False)
            logging.info("Inserted %d records into empty database", len(df_new))

        conn.close()

        # Clean up CSV file after loading to database
        os.remove(filename)

        return True
    except AssertionError as e:
        logging.error("File validation error: %s", e)
        return False
    except pd.errors.EmptyDataError as e:
        logging.error("CSV file is empty: %s", e)
        return False
    except sqlite3.Error as e:
        logging.error("Database error: %s", e)
        return False
    except Exception as e:
        logging.error("Unexpected error loading data: %s", e)
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
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT x, y FROM timeseries", conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        logging.error(e)
        return pd.DataFrame()
