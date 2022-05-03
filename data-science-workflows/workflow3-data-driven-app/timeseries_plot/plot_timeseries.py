# -*- coding: utf-8 -*-

"""Create live updating graph
"""

# standard library
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging

def plot_data():
    '''
    draws a plot and saves it in the working directory
    '''
    try:
        # retrieve from bucket
        df = pd.read_csv("")
    except TypeError as e:
        logging.error("File is missing")
    plt.plot(df.x,df.y)
    plt.title("Data sampled from a normal distribution mean = 0 and std = 1")
    return plt.savefig("lineplot.png")

if __name__ == "__main__":
    plot_data()
    print("do something")