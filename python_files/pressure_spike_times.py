#!/usr/bin/python3
### IMPORTS ###
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import json
import statistics as stat
from collections import deque
import argparse
import os
import errno
### HELPER FUNCTIONS ###
def read_data(filename):
    '''read in necessary data as pd Dataframes and np arrays
        Arguments:
        filename:  string  path of pressure data file
        Returns:
        pressure_arr:  numpy 2D array  time series pressure data for both vacuums
    '''
    # READ IN PRESSURE DATA AS PANDAS DATAFRAME
    #filename = 'data/MEBL3/MEBL3_Pressure-data-2024-06-28 09_40_08.csv'
    pressure_df = pd.read_csv(filename, parse_dates=['Time']).fillna(0)    
    print(f"{filename} : file read into a pandas dataframe.")
    print()
    # NP ARRAY
    pressure_arr = pressure_df.to_numpy()
    return pressure_arr
def identify_spikes(pressure_arr, time_range=5):
    '''use a deque to identify the timestamps of all pressure spikes in both the chamber and column vacuums
        spike defined as pressure exceeding 2x the mean value of the previous t seocnds
        Arguments:
        pressure_arr:  numpy 2D array  time series pressure data for both vacuums
        t:  int  number of seconds before each timestamp to base spike threshold calculation upon
        Returns:
        Two JSON files containing spike times for each vacuum
    '''
    output_dir = "pressure_spike_times/"
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        if e.errno == errno.EACCES:
            print(f"Permission denied: Unable to create directory {output_dir}")
            print("Attempting to change permissions...")
            try:
                # Attempt to change permissions if directory exists but is not writable
                os.chmod(output_dir, 0o755)
                print(f"Permissions changed successfully. Retrying directory creation...")
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                print(f"Failed to change permissions or create directory: {e}")
                return
        else:
            raise
    for type_idx, type in enumerate(["chamber", "column"]):
        spike_times = []
        pressure_deque = deque(maxlen=time_range) # time_range seconds previous to curr pressure val
        sum_pressure = 0
        for row_idx in range(len(pressure_arr)-1): # each loop looks to next value to see if it is a spike
            #print(f"{row_idx=}")
            pressure_value = pressure_arr[row_idx][type_idx + 1]
            #print(f"    {pressure_deque=}")
            #print(f"    {pressure_value=}")
            queue_len = len(pressure_deque)
            if queue_len < time_range:
                sum_pressure += pressure_value
                pressure_deque.append(pressure_value)
                #print(f"    {pressure_deque=}")
                continue
            elif queue_len == time_range:
                local_mean = sum_pressure / time_range
                #print(f"    {local_mean=}")
            if pressure_value > 2 * local_mean:
                spike_time = str(pressure_arr[row_idx][0])
                print(f"{spike_time=} : {pressure_deque=}")
                print(f"    {pressure_value=}, {local_mean=}")
                print()
                spike_times.append(spike_time)
            sum_pressure -= pressure_deque.popleft()
            sum_pressure += pressure_value
            pressure_deque.append(pressure_value)
        with open(f"{output_dir}{type}_spike_times_{time_range}_sec.json", "w") as outfile:
            json.dump(spike_times, outfile)
### MAIN FUNCTION ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pressure_filename',required=True)
    parser.add_argument('--time_range', required=False, type=int, default=5)
    args = parser.parse_args()
    pressure_filename = args.pressure_filename
    pressure_arr = read_data(pressure_filename)
    time_range = args.time_range
    identify_spikes(pressure_arr, time_range)