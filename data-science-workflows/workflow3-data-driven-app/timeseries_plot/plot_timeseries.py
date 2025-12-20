import matplotlib.pyplot as plt
import pandas as pd
import os
import time
from mylib.dataloader import upload_data_spaces
from mylib.database import init_database, load_s3_to_database, query_timeseries_data


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
    assert 'x' in df.columns and 'y' in df.columns, "DataFrame must have 'x' and 'y' columns"
    plt.plot(df.x, df.y)
    plt.title("Data sampled from a normal distribution mean = 0 and std = 1")
    return plt.savefig("lineplot.png")


if __name__ == "__main__":
    db_path = "timeseries_data.db"
    init_database(db_path)
    print("initialized database")
    load_s3_to_database("data.csv", db_path)
    print("loaded data from S3 into database")
    time.sleep(30)
    df = query_timeseries_data(db_path)
    print("queried data from database")
    plot_data_from_dataframe(df)
    print("made plot saved it in directory for now")
    time.sleep(5)
    callback_string = "Uploaded data to object storage {}".format(
        upload_data_spaces("lineplot.png")
    )
    print(callback_string)
    os.remove("lineplot.png")
