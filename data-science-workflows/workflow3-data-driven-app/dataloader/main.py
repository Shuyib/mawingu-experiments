import numpy as np
import pandas as pd
import time
from datetime import datetime
import os
import glob as glob
import great_expectations as ge
from mylib.dataloader import upload_data_spaces
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_env_vars():
    """Validate required environment variables are set
    
    Returns
    -------
    Boolean True/False
    True if all required environment variables are set.
    False if any required environment variables are missing.
    
    """
    required_vars = ['ENDPOINT_URL', 'SECRET_KEY', 'SPACES_ID', 'SPACES_NAME']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    return True


# make the data directory if it doesn't exist
if not os.path.exists("data/"):
    os.makedirs("data/")

# Save original working directory for context preservation
original_cwd = os.getcwd()
# fix the working directory remove this and it won't work
os.chdir("data/")

# find out the day today
today = datetime.today().strftime("%Y-%m-%d")
today_day_time = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")


# define streaming dataset
# based on https://stackoverflow.com/questions/13293269/how-would-i-stop-a-while-loop-after-n-amount-of-time
# documentation was made with pyment e.g pyment -w -o numpydoc create_dataframe.py
def create_dataframe(timer_interval=60):
    """make a streaming dataset that makes a random column called y sampled from a normal distribution and store it data folder and
    call the index column x. Change the interval at which data is stored by specifying time_interval argument based on time.time python method.

    Parameters
    ----------
    timer_interval :
    This is the time you'd want to wait for something to happen in this case. Wait for data to be loaded.
    Default specification is in seconds. For example: time_interval=1 means that the data will be updated every second.

    Returns
    -------
    Pandas.DataFrame stored as data.csv in the data directory.

    Example
    -------
    create_dataframe(time_interval=1) # data is stored every second try using random to make it more realistic
    """
    timeout = time.time() + timer_interval * 1  # 1 minutes from now
    headers = ["y"]
    df = pd.DataFrame(columns=headers)
    while True:
        test = 0
        y = np.random.randn()
        datastream = {"y": y}
        df = pd.concat([df, pd.DataFrame([datastream])], ignore_index=True)
        df.to_csv("data.csv", index_label="x")
        print(df)
        if test == 1 or time.time() > timeout:
            break
        test = test - 1


def test_df_expectations():
    """Check if the dataframe has two columns and catch instances of that not happening"""
    df = ge.read_csv("data.csv")
    x_expect = df.expect_column_to_exist(
        column="x", result_format="BOOLEAN_ONLY", catch_exceptions=True
    )
    y_expect = df.expect_column_to_exist(
        column="y", result_format="BOOLEAN_ONLY", catch_exceptions=True
    )
    return ["Looking dataframe columns", x_expect, "*" * 100, y_expect, "*" * 100]


def write_test_expectations():
    """After checking the expectations write the results to a file"""
    path_df_expect = "expectation_dataframe_at_columns_{}".format(today_day_time)
    with open(path_df_expect, "w+", encoding="UTF-8") as f:
        f.write(str(test_df_expectations()))


if __name__ == "__main__":
    temp_files = []
    try:
        # Validate environment variables at startup
        validate_env_vars()
        
        logger.info("Starting data creation process")
        create_dataframe(timer_interval=60)
        time.sleep(62)
        
        # Validate file exists before upload
        data_file = "data.csv"
        if not os.path.isfile(data_file):
            raise FileNotFoundError(f"Data file '{data_file}' not found")
        
        logger.info(f"Uploading {data_file} to object storage")
        upload_result = upload_data_spaces(data_file)
        if not upload_result:
            raise RuntimeError(f"Failed to upload {data_file} to object storage")
        callback_string1 = f"Uploaded data to object storage {upload_result}"
        print(callback_string1)
        
        logger.info("Checking great data expectations for project")
        print("Checking great data expectations for project")
        write_test_expectations()
        
        # Fix fragile glob pattern with proper error handling
        expectation_files = glob.glob("expectation*")
        if not expectation_files:
            raise FileNotFoundError("No expectation files found matching pattern 'expectation*'")
        path_run_df_expectations = expectation_files[0]
        temp_files.append(path_run_df_expectations)
        
        logger.info(f"Uploading {path_run_df_expectations} to object storage")
        upload_result2 = upload_data_spaces(path_run_df_expectations)
        if not upload_result2:
            raise RuntimeError(f"Failed to upload {path_run_df_expectations} to object storage")
        callback_string2 = f"Uploaded data expectations to object storage {upload_result2}"
        print(callback_string2)
        
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
        
        # Restore original working directory
        try:
            os.chdir(original_cwd)
        except Exception as e:
            logger.warning(f"Failed to restore original working directory: {e}")
