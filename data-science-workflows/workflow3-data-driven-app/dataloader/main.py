import numpy as np
import pandas as pd
import time
from datetime import datetime
import os
import glob as glob
import great_expectations as ge
from mylib.dataloader import upload_data_spaces

# make the data directory if it doesn't exist
if not os.path.exists("data/"):
    os.makedirs("data/")

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
        df = df.append(datastream, ignore_index=True)
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
    create_dataframe(timer_interval=60)
    time.sleep(62)
    callback_string1 = "Uploaded data to object storage {}".format(
        upload_data_spaces("data.csv")
    )
    print(callback_string1)
    print("Checking great data expectations for project")
    write_test_expectations()
    path_run_df_expectations = glob.glob("expectation*")[0]
    callback_string2 = "Uploaded data expectations to object storage {}".format(
        upload_data_spaces(path_run_df_expectations)
    )
    print(callback_string2)
