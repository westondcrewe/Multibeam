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
import re
import matplotlib.ticker as ticker
import time
import glob
import scipy
### HELPER FUNCTIONS ###
def read_arc_data(arc_filename):
    # READ-IN CLEAN ARC COUNTS DATAFRAME
    arc_count_df = pd.read_csv(arc_filename, parse_dates=['Time']).fillna(0)  
    print(f"{arc_filename} : file read into a pandas dataframe.")
    # CONVERT TO NUMPY ARRAY
    arc_count_arr = arc_count_df.to_numpy()
    return arc_count_df, arc_count_arr
def read_pressure_data(pressure_filename):
    pressure_df = pd.read_csv(pressure_filename, parse_dates=['Time']).fillna(0)    
    print(f"{pressure_filename} : file read into a pandas dataframe.")
    pressure_df["Chamber Pressure"] = pressure_df["Chamber Pressure"].astype(np.float64)
    pressure_df["Column Pressure"] = pressure_df["Column Pressure"].astype(np.float64)
    # CONVERT PRESSURE DATA TO NUMPY ARRAY
    pressure_arr = pressure_df.to_numpy()
    return pressure_df, pressure_arr
def get_arc_times(col_hvps, arc_count_df, pressure_df):
    # GRAB TIMES OF ALL ARC COUNTS (FOR EACH COMPONENT)
    '''Given a column HVSP, find Time values of all arc events
        Argument
        col_idx:   type=int            index of the column HVSP of measure within arc_counts
        Return
        arc_times_df: type=np.array    numpy array arc_counts filtered to keep just arc events of column HVSP of measure
    '''
    arc_times = arc_count_df[arc_count_df[col_hvps] > 0]["Time"]
    if len(arc_times) > 0: 
        arc_idx = np.where(pressure_df["Time"].isin(arc_times))[0]
    else: arc_idx = []
    return arc_times, arc_idx
def pressure_at_arc_plot(col_hvps, arc, pressure, cham_max, cham_max_idx, cham_max_time, cham_local_mean, cham_delta, col_max, col_max_idx, col_max_time, col_local_mean, col_delta, local_mean_range):
    # INITIALIZE
    plt.figure(figsize=(12, 6))
    ax1 = plt.gca()
    ax1.axvline(x=arc, color='black', linewidth=0.75)
    # PLOT VARIABLES 
    time = pressure[:,0]
    cham_pres = pressure[:, 1]
    col_pres = pressure[:, 2]
    # CHAMBER PRESSURE
    sns.lineplot(x=time, y=cham_pres, ax=ax1, label='Chamber Pressure', color='b')
    ax1.set_ylabel('Chamber Pressure')
    ax1.set_xlabel('Time')
    ax1.hlines(xmin=pressure[cham_max_idx-local_mean_range, 0], xmax=cham_max_time, y=cham_local_mean, color='b', linestyle='--', linewidth=0.8, label=f'Mean Before Spike ({cham_local_mean:.2e})')
    ax1.vlines(x=cham_max_time, ymin=cham_local_mean, ymax=cham_max, color='b', linestyle='--', linewidth=0.8, label=f'Delta ({cham_delta:.2e})')
    ax1.scatter(x=cham_max_time, y=cham_max, color='b', s=100, label=f'Spike Value ({cham_max:.2e})')
    ax1.legend(loc='upper left', fontsize=8)
    # COLUMN PRESSURE
    ax2 = ax1.twinx()
    sns.lineplot(x=time, y=col_pres, ax=ax2, label='Column Pressure', color='r')
    ax2.set_ylabel('Column Pressure')
    ax2.set_xlabel('Time')
    ax2.hlines(xmin=pressure[col_max_idx-local_mean_range, 0], xmax=col_max_time, y=col_local_mean, color='r', linestyle='--', linewidth=0.8, label=f'Mean Before Spike ({col_local_mean:.2e})')
    ax2.vlines(x=col_max_time, ymin=col_local_mean, ymax=col_max, color='r', linestyle='--', linewidth=0.8, label=f'Delta ({col_delta:.2e})')
    ax2.scatter(x=col_max_time, y=col_max, color='r', s=100, label=f'Spike Value ({col_max:.2e})')
    ax2.legend(loc='upper right', fontsize=8)
    # CLEAN
    title = f'System Pressure at {arc} Arc Event on {col_hvps}'
    ax1.set_title(title)
    newpath = f'plots/pressure_at_arcs/{col_hvps}'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    print(f"Saving pressure plots to {newpath}")
    plt.savefig(f"{newpath}/{((str(arc).replace(" ", "__")).replace(":", "_")).replace("-", "_")}.pdf", format='pdf')
def pressure_window(col_hvps, arc_times, arc_time_idx, pressure_linegraphs, time_range=15, spike_range=5, local_mean_range=10):
    # FILTER PRESSURE DATA
    pressure = []
    num_rows = pressure_df.shape[0]
    arc_times_list = []
    arc_component_list = []
    chamber_delta_list = []
    column_delta_list = []
    for arc, idx in enumerate(arc_time_idx):
        #print(i)
        #print(f"{row_idx=}, {num_rows=}")
        if idx < time_range:
            pressure = pressure_arr[:idx+time_range+1]
        elif idx + time_range > num_rows:
            pressure = pressure_arr[idx-time_range:]
        else:
            pressure = pressure_arr[idx-time_range:idx+time_range+1]
        if pressure.size > 0:
            cham_max_idx = np.argmax(pressure[time_range-spike_range:time_range+spike_range+1, 1]) + (time_range-spike_range)
            cham_max = pressure[cham_max_idx, 1]
            cham_max_time = pressure[cham_max_idx, 0]
            cham_local_mean = np.mean(pressure[cham_max_idx-local_mean_range:cham_max_idx, 1])
            cham_delta = cham_max-cham_local_mean
            col_max_idx = np.argmax(pressure[time_range-spike_range:time_range+spike_range+1, 2]) + (time_range-spike_range)
            col_max = pressure[col_max_idx, 2]
            col_max_time = pressure[col_max_idx, 0]
            col_local_mean = np.mean(pressure[col_max_idx-local_mean_range:col_max_idx, 2])
            col_delta = col_max-col_local_mean
            if pressure_linegraphs: 
                pressure_at_arc_plot(col_hvps, arc_times.iloc[arc], pressure, cham_max, cham_max_idx, cham_max_time, cham_local_mean, cham_delta, col_max, col_max_idx, col_max_time, col_local_mean, col_delta ,local_mean_range)
            arc_times_list.append(str(arc_times.iloc[arc]))
            arc_component_list.append(col_hvps)
            chamber_delta_list.append(cham_delta)
            column_delta_list.append(col_delta)
    return pressure, arc_times_list, arc_component_list, chamber_delta_list, column_delta_list
def pressure_delta_dist_plot(chamber_pressure_delta_df, column_pressure_delta_df, n_bins):
    dfl = [chamber_pressure_delta_df, column_pressure_delta_df]
    for i, pres_type in enumerate(["Chamber", "Column"]):
        pressure_delta_df = dfl[i]
        plt.figure(figsize=(13, 6))
        pressure_delta_data = pressure_delta_df[pres_type + " Pressure Delta"]
        min_delta = pressure_delta_data.min()
        max_delta = pressure_delta_data.max()
        delta_range = max_delta - min_delta
        bin_width = delta_range/n_bins
        sns.histplot(pressure_delta_data, bins=n_bins, binrange=(min_delta, max_delta), color='skyblue')
        ax = plt.gca()
        ax.set_xticks(np.arange(min_delta - bin_width, max_delta + bin_width, bin_width))
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=bin_width * 2, offset=min_delta)) 
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=bin_width, offset=min_delta))
        plt.xticks(rotation=45)
        plt.xlim(0,1.1*max_delta)
        plt.xlabel(f'{pres_type} Pressure Delta')
        plt.ylabel('Count')
        plt.title(f'Histogram of {pres_type} Pressure Delta Distribution')
        output_dir = 'plots/pressure_delta_histograms/'
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nSaving pressure delta histogram to {output_dir}\n")
        plt.savefig(f"{output_dir}{str.lower(pres_type)}_pressure_delta_histogram_{n_bins}_bins.pdf", format='pdf')
### MAIN FUNCTION ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arc_filename',required=True)
    parser.add_argument('--pressure_filename', required=True)
    parser.add_argument('--pressure_linegraphs', required=False, default=False)
    parser.add_argument('--delta_histograms', required=False, default=False)
    parser.add_argument('--n_bins', required=False, default=75)
    args = parser.parse_args()

    arc_filename = args.arc_filename
    pressure_filename = args.pressure_filename
    pressure_linegraphs = args.pressure_linegraphs
    delta_histograms = args.delta_histograms
    n_bins = args.n_bins

    arc_count_df, arc_count_arr = read_arc_data(arc_filename)
    pressure_df, pressure_arr = read_pressure_data(pressure_filename)

    pd.options.display.float_format = '{:.2e}'.format
    col_hvps_list = list(arc_count_df.columns[1:])                                      # list of all Column HVPS to be looped through
    times = arc_count_df["Time"]                                                            # get all Time values
    pressure_delta_dict = {"Arc Time": [],
            "Arc Component": [],
            "Chamber Pressure Delta": [],
            "Column Pressure Delta": []
    }
    for col_idx, col_hvps in enumerate(col_hvps_list):
        # TERMINAL OUTPUT READABILITY
        lenght_symbol = (74-len(col_hvps))//2
        print(f"{'+'*lenght_symbol}{col_hvps}{'+'*lenght_symbol}")
        ## strung out: initial dataset had several thousand C3 Suppressor arcs, so script would take way too long
        #'''
        if col_hvps == 'C3 Suppressor':
            continue
        #'''
        # GET ARC TIMES
        arc_times, arc_time_idx = get_arc_times(col_hvps, arc_count_df, pressure_df)                                        # col_idx from enumerate will be offset by 1 from proper index in arc_counts
        # FILTER PRESSURE DATA BASED ON ARC TIMES
        pressure, arc_times_list, arc_component_list, chamber_delta_list, column_delta_list = pressure_window(col_hvps, arc_times, arc_time_idx, pressure_linegraphs)
        pressure_delta_dict["Arc Time"].extend(arc_times_list)
        pressure_delta_dict["Arc Component"].extend(arc_component_list)
        pressure_delta_dict["Chamber Pressure Delta"].extend(chamber_delta_list)
        pressure_delta_dict["Column Pressure Delta"].extend(column_delta_list)
    chamber_pressure_delta_df = pd.DataFrame({col: pressure_delta_dict[col] for col in ['Arc Time', 'Arc Component', 'Chamber Pressure Delta']}).sort_values("Chamber Pressure Delta", ascending=False)
    column_pressure_delta_df = pd.DataFrame({col: pressure_delta_dict[col] for col in ['Arc Time', 'Arc Component', 'Column Pressure Delta']}).sort_values("Column Pressure Delta", ascending=False)
    output_dir = 'data/results/'
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nSaving all components data to {output_dir}\n")
    print(f"\nSaving pressure delta data to {output_dir}\n")
    chamber_pressure_delta_df.to_csv(f'{output_dir}chamber_pressure_deltas_at_arcs.csv', index=False)
    column_pressure_delta_df.to_csv(f'{output_dir}column_pressure_deltas_at_arcs.csv', index=False)
    if delta_histograms:
        pressure_delta_dist_plot(chamber_pressure_delta_df, column_pressure_delta_df, n_bins)