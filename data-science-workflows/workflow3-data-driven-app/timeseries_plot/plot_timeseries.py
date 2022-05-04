import matplotlib.pyplot as plt
import pandas as pd
import os
import time
from mylib.dataloader import download_file_s3, upload_data_spaces


def plot_data(data_set_path):
    """draws a plot and saves it in the working directory

    Parameters
    ----------
    dataset_path : where the file is located. It is supposed to be in the working directory. It will be taken by the
    read_csv which expects a file on CSV from object storage.


    Returns
    -------
    A PNG file in the working directory

    """
    assert os.path.isfile(data_set_path), '"{}" is not a valid path'.format(
        data_set_path
    )
    df = pd.read_csv(data_set_path)
    plt.plot(df.x, df.y)
    plt.title("Data sampled from a normal distribution mean = 0 and std = 1")
    return plt.savefig("lineplot.png")


if __name__ == "__main__":
    download_file_s3("", "data.csv")
    print("loaded data into working directory for now")
    time.sleep(30)
    plot_data("data.csv")
    print("made plot saved it in directory for now")
    time.sleep(5)
    callback_string = "Uploaded data to object storage {}".format(
        upload_data_spaces("lineplot.png", "")
    )
    print(callback_string)
    os.remove("data.csv")
    os.remove("lineplot.png")
