#!/usr/bin/python3
### IMPORTS ###
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import json
import argparse
import os
import errno
### FUNCTIONS ###
def time_window_filter(timestamp, pressure_df, window_df, window_seconds):
    """Filter a given dataframe to keep observations within window_seconds seconds of the observation at timestamp Time value.
        Arguments:
        timestamp       --      Time value of type datetime, likely used for times of arc events
        pressure_df     --      main pressure dataframe
        window_df       --      Tidy dataframe holding pressure information, pressure_df in original form
        window_seconds  --      Integer denoting range of time for observations kept in returned dataframe filtered_df
        Returns:
        filtered_df     --      Filtered dataframe
    """
    timestamp = pd.to_datetime(timestamp)
    pressure_df['Time_diff'] = (window_df['Time'] - timestamp).abs()
    filtered_df = pressure_df[pressure_df['Time_diff'] <= pd.Timedelta(seconds=window_seconds)]
    filtered_df = filtered_df.drop(columns=['Time_diff'])
    return filtered_df
def pressure_type_filter(pressure_type, window_df):
    """Takes a pressure dataframe as input and filters the columns such that only the given pressure_type is kept in the dataframe
        Arguments:
        pressure_type   --      either Chamber Pressure or Column pressure
        window_df       --      Tidy dataframe holding pressure information, pressure_df in original form
        Returns:
        window_df       --      filtered dataframe
    """
    try:
        keep_vars = ["Time", pressure_type]
        window_df = window_df[keep_vars]
    except:
        print("pressure_type input invalid: must be either Chamber Pressure or Column Pressure, or left blank and pressure_window() will default to include both")
        return
    return window_df
def pressure_window(timestamp, pressure_df, pressure_type = None, window_seconds = 5):
    """Filters pressure_df to capture and plot a 10 second time frame surrounding an arc event
        Arguments: 
        timestamp       --      keeps rows in which Time is within 10 seconds of arc event (timestamp input) (row axis filter)
        pressure_df     --      main pressure dataframe
        pressure_type   --      either Chamber Pressure or Column Pressure, default = None (means to keep both)
        window_seconds  --      Integer denoting range of time for observations, default = 5
        Return:
        window_df       --      filtered dataframe
    """
    window_df = pressure_df
    # ROW AXIS FILTER
    timestamp = pd.to_datetime(timestamp)
    window_df = time_window_filter(timestamp, pressure_df, window_df, window_seconds)
    # COLUMN AXIS FILTER
    if pressure_type is not None:
        window_df = pressure_type_filter(pressure_type, window_df)
        pressure_type = [pressure_type]
    else:
        pressure_type = ['Chamber Pressure', 'Column Pressure']
    # PLOT PRESSURE WINDOW    
    plt.figure(figsize=(12, 6))
    ax1 = plt.gca()
    # PLOT CHAMBER PRESSURE
    if 'Chamber Pressure' in pressure_type:
        sns.lineplot(data=window_df, x="Time", y="Chamber Pressure", ax=ax1, label='Chamber Pressure', color='b')
        ax1.set_ylabel('Chamber Pressure')
        ax1.legend(loc='upper left')
        ax1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    # PLOT COLUMN PRESSURE
    if 'Column Pressure' in pressure_type:
        if 'Chamber Pressure' in pressure_type: # if both pressures plotted, put column pressure axis on right side
            ax2 = ax1.twinx()
            sns.lineplot(data=window_df, x="Time", y="Column Pressure", ax=ax2, label='Column Pressure', color='r')
            ax2.set_ylabel('Column Pressure')
            ax2.legend(loc='upper right')
            ax2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        else:
            sns.lineplot(data=window_df, x="Time", y="Column Pressure", ax=ax1, label='Column Pressure', color='r')
            ax1.set_ylabel('Column Pressure')
            ax1.legend(loc='upper right')
            ax1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    # ADDING TITLES AND LEGENDS
    title = ', '.join(pressure_type) + f" Spike at {timestamp}"
    ax1.set_title(title)
    # SAVE IMAGE
    filename = f"{title}_{str(timestamp).replace(":", "_")}.pdf".replace(" ", "_")
    output_dir = 'plots/pressure_spikes/'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f"{output_dir}{filename}", format='pdf')
    #plt.show()
    return window_df