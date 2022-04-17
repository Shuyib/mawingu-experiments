import numpy as np
import pandas as pd
import time

# define dataset column
def create_dataframe(timer_interval):
    '''
    make a streaming dataset that makes a random column called y sampled from a normal distribution and store it data folder and 
    call the index column y. Change the interval by specifying time_interval argument based on time.sleep python method
    '''
    headers = ['y']
    df = pd.DataFrame(columns=headers)
    while True:
        y = np.random.randn()
        datastream = {'y':y}
        time.sleep(timer_interval)
        df = df.append(datastream, ignore_index=True)
        df.to_csv("data/data.csv", index_label="x") 
        print(df)

if __name__== "main":
    create_dataframe(1)
