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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeseries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                x REAL NOT NULL,
                y REAL NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logging.error(e)
        return False


def load_s3_to_database(filename, db_path):
    """Download data from S3 and insert into SQLite database
    
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
    and inserts data into database
    
    """
    try:
        # Download file from S3
        download_result = download_file_s3(filename)
        if not download_result:
            logging.error("Failed to download file from S3")
            return False
        
        # Read CSV file
        assert os.path.isfile(filename), '"{}" is not a valid path'.format(filename)
        df = pd.read_csv(filename)
        
        # Insert data into database
        conn = sqlite3.connect(db_path)
        df.to_sql('timeseries', conn, if_exists='append', index=False)
        conn.close()
        
        # Clean up CSV file after loading to database
        os.remove(filename)
        
        return True
    except (sqlite3.Error, pd.errors.EmptyDataError, AssertionError) as e:
        logging.error(e)
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
