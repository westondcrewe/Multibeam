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
import pressure_window_plot as pwp
### HELPER FUNCTIONS ###
def read_arc_data(arc_filename):
    # READ-IN CLEAN ARC COUNTS DATAFRAME
    arc_count_df = pd.read_csv(arc_filename, parse_dates=['Time']).fillna(0)  
    print(f"{arc_filename} : file read into a pandas dataframe.")
    # CONVERT TO NUMPY ARRAY
    arc_count_arr = arc_count_df.to_numpy()
    return arc_count_arr, arc_count_df.columns[1:]
def read_pressure_data(pressure_filename):
    pressure_df = pd.read_csv(pressure_filename, parse_dates=['Time'])    
    print(f"{pressure_filename} : file read into a pandas dataframe.")
    return pressure_df
def read_pressure_spike_data(chamber_json, column_json):
    chamber_json = open(chamber_json)
    chamber_spikes = json.load(chamber_json)
    chamber_spikes = [pd.Timestamp(t) for t in chamber_spikes]
    column_json = open(column_json)
    column_spikes = json.load(column_json)
    column_spikes = [pd.Timestamp(t) for t in column_spikes]
    return chamber_spikes, column_spikes
def get_arcs_at_pressure_spikes(arc_count_arr, chamber_spikes, column_spikes):
    pressure_spike_mask = np.isin(arc_count_arr[:, 0], chamber_spikes + column_spikes)
    arcs_at_pressure_spikes = arc_count_arr[pressure_spike_mask]
    return arcs_at_pressure_spikes
def get_arcs_at_pressure_spikes_counts(arcs_at_pressure_spikes):
    arc_pressure_counts = []
    num_cols = len(arcs_at_pressure_spikes[0]) 
    for col_idx in range(1, num_cols):  # don't loop over Time variable
        arc_pressure_counts.append(np.sum(arcs_at_pressure_spikes[:, col_idx]))
    return arc_pressure_counts
def get_total_arc_counts(arc_count_arr):
    # GET TOTAL ARC COUNTS BY COLUMN HVPS
    total_arc_counts = []
    num_cols = len(arc_count_arr[0]) 
    for col_idx in range(1, num_cols):  # no Time
        total_arc_counts.append(np.sum(arc_count_arr[:, col_idx]))
    return total_arc_counts
def get_arcs_at_pressure_spikes_percents(arc_pressure_counts, total_arc_counts):
    arc_pressure_percent = []
    num_cols = len(arc_pressure_counts)
    for i in range(num_cols):
        total = total_arc_counts[i]
        if total == 0:
            arc_pressure_percent.append(0)
            continue
        arc_pressure_percent.append(100*arc_pressure_counts[i]/total)
    return arc_pressure_percent
def create_dataframe(column_HVPS, total_arc_counts, arc_pressure_counts, arc_pressure_percent):
    dataframe = {
    "Column HVPS": column_HVPS,
    "Total Arc Counts": total_arc_counts,
    "Count of Arcs Synchronous w/ Pressure Spikes": arc_pressure_counts,
    "Percent of Arcs Synchronous w/ Pressure Spikes": arc_pressure_percent
    }
    arc_pressure_df = pd.DataFrame(dataframe)
    arc_pressure_df.to_csv('data/arcs_at_pressure_spikes.csv', index = False)
    return arc_pressure_df
def make_plot_directory(output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        if e.errno == errno.EACCES:
            print(f"Permission denied: Unable to create directory {output_dir}")
            print("Attempting to change permissions...")
            try:
                os.chmod(output_dir, 0o755)
                print(f"Permissions changed successfully. Retrying directory creation...")
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                print(f"Failed to change permissions or create directory: {e}")
                return
        else:
            raise
def plot_counts(arc_pressure_df):
    counts_plot_df = arc_pressure_df[["Column HVPS", "Count of Arcs Synchronous w/ Pressure Spikes"]].sort_values(by="Count of Arcs Synchronous w/ Pressure Spikes", ascending=False)
    counts_plot_df = counts_plot_df[counts_plot_df["Count of Arcs Synchronous w/ Pressure Spikes"] > 0]
    plt.figure(figsize=(12,8))
    plot = sns.barplot(data = counts_plot_df, x = 'Count of Arcs Synchronous w/ Pressure Spikes', y = 'Column HVPS', fill = True, hue = 'Count of Arcs Synchronous w/ Pressure Spikes', legend=False)
    title = "Arcs Synchronous with Column Pressure Spikes Count"
    plot.set_title(title)
    output_dir = "plots/arcs_at_pressure_spikes/"
    make_plot_directory(output_dir)
    print(f"Saving counts plot to {output_dir}")
    plt.savefig(f"{output_dir}{title.replace(" ", "_")}.pdf", format = 'pdf')
def plot_percents(arc_pressure_df):
    percents_plot_df = arc_pressure_df[["Column HVPS", "Percent of Arcs Synchronous w/ Pressure Spikes"]].sort_values(by="Percent of Arcs Synchronous w/ Pressure Spikes", ascending=False)
    percents_plot_df = percents_plot_df[percents_plot_df["Percent of Arcs Synchronous w/ Pressure Spikes"] > 0] 
    plt.figure(figsize=(12,8))
    plot = sns.barplot(data = percents_plot_df, x = 'Percent of Arcs Synchronous w/ Pressure Spikes', y = 'Column HVPS', fill = True, hue = 'Percent of Arcs Synchronous w/ Pressure Spikes', legend=False)
    title = "Arcs Synchronous with Column Pressure Spikes Percent"
    plot.set_title(title)
    output_dir = "plots/"
    make_plot_directory(output_dir)
    print(f"Saving counts plot to {output_dir}")
    plt.savefig(f"{output_dir}{title.replace(" ", "_")}.pdf", format = 'pdf')
def plot_total_counts(arc_pressure_df):
    total_counts_plot_df = arc_pressure_df[["Column HVPS", "Total Arc Counts"]].sort_values(by="Total Arc Counts", ascending=False)
    total_counts_plot_df = total_counts_plot_df[total_counts_plot_df["Total Arc Counts"] > 0]   
    plt.figure(figsize=(12,8))
    plot = sns.barplot(data = total_counts_plot_df, x = 'Total Arc Counts', y = 'Column HVPS', fill = True, hue = 'Total Arc Counts', legend=False)
    title = "Total Arc Counts"
    plot.set_title(title)
    output_dir = "plots/arcs_at_pressure_spikes/"
    make_plot_directory(output_dir)
    print(f"Saving counts plot to {output_dir}")
    plt.savefig(f"{output_dir}{title.replace(" ", "_")}.pdf", format = 'pdf')

### MAIN FUNCTION ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arc_filename',required=True)
    parser.add_argument('--pressure_filename', required=True)
    parser.add_argument('--chamber_json', required=True)
    parser.add_argument('--column_json', required=True)
    args = parser.parse_args()

    arc_filename = args.arc_filename
    pressure_filename = args.pressure_filename
    chamber_json = args.chamber_json
    column_json = args.column_json

    arc_count_arr, column_HVPS = read_arc_data(arc_filename)
    chamber_spikes, column_spikes = read_pressure_spike_data(chamber_json, column_json)
    arcs_at_pressure_spikes = get_arcs_at_pressure_spikes(arc_count_arr, chamber_spikes, column_spikes)
    arc_pressure_counts = get_arcs_at_pressure_spikes_counts(arcs_at_pressure_spikes)
    total_arc_counts = get_total_arc_counts(arc_count_arr)
    arc_pressure_percent = get_arcs_at_pressure_spikes_percents(arc_pressure_counts, total_arc_counts)
    arc_pressure_df = create_dataframe(column_HVPS, total_arc_counts, arc_pressure_counts, arc_pressure_percent)
    plot_counts(arc_pressure_df)
    plot_percents(arc_pressure_df)
    plot_total_counts(arc_pressure_df)

    pressure_df = read_pressure_data(pressure_filename)
    for time in chamber_spikes:
        pwp.pressure_window(time, pressure_df, 'Chamber Pressure', 10)
    print(f"Saving chamber pressure spike plots to plots/pressure_spikes")
    for time in column_spikes:
        pwp.pressure_window(time, pressure_df, 'Column Pressure', 10)
    print(f"Saving column pressure spike plots to plots/pressure_spikes")