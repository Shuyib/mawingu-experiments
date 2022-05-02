import time
import pandas as pd
import numpy as np


def create_dataframe():
    headers = ["y"]
    df = pd.DataFrame(columns=headers)
    while True:
        y = np.random.randn()
        datastream = {"y": y}
        time_interval = 1
        assert type(time_interval) is int
        time.sleep(
            time_interval
        )  # based on the time.sleep method, replace time interval with int
        df = df.append(datastream, ignore_index=True)
        df.to_csv("data/data.csv", index_label="x")
        assert df.shape[1] == 2
