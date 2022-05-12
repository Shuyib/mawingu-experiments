import numpy as np
import pandas as pd
import time
import os
from mylib.dataloader import upload_data_spaces

# define streaming dataset
# based on https://stackoverflow.com/questions/13293269/how-would-i-stop-a-while-loop-after-n-amount-of-time
# documentation was made with pyment e.g pyment -w -o numpydoc create_dataframe.py
def create_dataframe(timer_interval):
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
    create_dataframe(time_interval=1) # data is stored every second
    """
    timeout = time.time() + 60 * 1  # 1 minutes from now
    headers = ["y"]
    df = pd.DataFrame(columns=headers)
    while True:
        test = 0
        y = np.random.randn()
        datastream = {"y": y}
        df = df.append(datastream, ignore_index=True)
        df.to_csv("data/data.csv", index_label="x")
        print(df)
        if test == 1 or time.time() > timeout:
            break
        test = test - 1


if __name__ == "__main__":
    create_dataframe(timer_interval=60)
    time.sleep(62)
    callback_string = "Uploaded data to object storage {}".format(
        upload_data_spaces("data.csv")
    )
    print(callback_string)
    os.remove("data/data.csv")
