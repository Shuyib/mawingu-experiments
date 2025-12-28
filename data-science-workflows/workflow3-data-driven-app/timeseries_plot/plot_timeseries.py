import matplotlib.pyplot as plt
import pandas as pd
import os
import time
import logging
from mylib.dataloader import upload_data_spaces
from mylib.database import init_database, load_s3_to_database, query_timeseries_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def plot_data_from_dataframe(df):
    """draws a plot from a pandas DataFrame and saves it in the working directory

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing x and y columns to plot


    Returns
    -------
    A PNG file in the working directory

    """
    assert isinstance(df, pd.DataFrame), "Input must be a pandas DataFrame"
    assert (
        "x" in df.columns and "y" in df.columns
    ), "DataFrame must have 'x' and 'y' columns"
    
    # Validate DataFrame is not empty
    if df.empty:
        raise ValueError("DataFrame is empty, cannot create plot")
    
    plt.plot(df.x, df.y)
    plt.title("Data sampled from a normal distribution mean = 0 and std = 1")
    return plt.savefig("lineplot.png")


if __name__ == "__main__":
    temp_files = []
    db_path = "timeseries_data.db"
    plot_file = "lineplot.png"
    
    try:
        # Initialize database with validation
        logger.info("Initializing database")
        init_result = init_database(db_path)
        if not init_result:
            raise RuntimeError("Failed to initialize database")
        print("initialized database")
        
        # Load data from S3 with validation
        logger.info("Loading data from S3 into database")
        load_result = load_s3_to_database("data.csv", db_path)
        if not load_result:
            raise RuntimeError("Failed to load data from S3 into database")
        print("loaded data from S3 into database")
        
        time.sleep(30)
        
        # Query data with validation
        logger.info("Querying data from database")
        df = query_timeseries_data(db_path)
        if df is None or df.empty:
            raise ValueError("No data returned from database query")
        print("queried data from database")
        
        # Create plot with validation
        logger.info("Creating plot")
        plot_data_from_dataframe(df)
        temp_files.append(plot_file)
        print("made plot saved it in directory for now")
        
        time.sleep(5)
        
        # Upload plot with validation
        if not os.path.isfile(plot_file):
            raise FileNotFoundError(f"Plot file '{plot_file}' not found")
        
        logger.info(f"Uploading {plot_file} to object storage")
        upload_result = upload_data_spaces(plot_file)
        if not upload_result:
            raise RuntimeError(f"Failed to upload {plot_file} to object storage")
        callback_string = f"Uploaded data to object storage {upload_result}"
        print(callback_string)
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_file}: {e}")
