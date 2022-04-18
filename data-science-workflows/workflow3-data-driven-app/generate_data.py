import numpy as np
import pandas as pd
import time

# define streaming dataset
# documentation was made with pyment e.g pyment -w -o numpydoc create_dataframe.py
def create_dataframe(timer_interval):
    """make a streaming dataset that makes a random column called y sampled from a normal distribution and store it data folder and
    call the index column y. Change the interval by specifying time_interval argument based on time.sleep python method

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
    create_dataframe(time_interval=1) # data is stored every second

    """
    headers = ["y"]
    df = pd.DataFrame(columns=headers)
    while True:
        y = np.random.randn()
        datastream = {"y": y}
        time.sleep(timer_interval)
        df = df.append(datastream, ignore_index=True)
        df.to_csv("data/data.csv", index_label="x")
        print(df)


if __name__ == "main":
    create_dataframe(1)
