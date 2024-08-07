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
import time
### HELPER FUNCTIONS ###
def read_arc_data(arc_filename):
    # READ-IN CLEAN ARC COUNTS DATAFRAME
    arc_count_df = pd.read_csv(arc_filename, parse_dates=['Time']).fillna(0)  
    print(f"{arc_filename} : file read into a pandas dataframe.")
    # CONVERT TO NUMPY ARRAY
    arc_count_arr = arc_count_df.to_numpy()
    return arc_count_df, arc_count_arr
def get_arc_times(col_idx, arc_count_arr):
    '''Given a column HVSP, find Time values of all arc events
        Argument
        col_idx:   type=int            index of the column HVSP of measure within arc_counts
        Return
        arc_times_df: type=np.array    numpy array arc_counts filtered to keep just arc events of column HVSP of measure
    '''
    arc_times = arc_count_arr[arc_count_arr[:, col_idx] > 0]
    return arc_times
def synchronous_arcs(col_hvsp, col_idx, col_hvsp_list, col_hvsp_arcs):
    '''function to find the number of arcs a column HVPS component has at the same time as the given col_hvsp
        Arguments
        col_hvsp:  type=string  the given column HVSP component for which we are measuring other column HVSP arcs against
        col_hvsp_list:  type=list of strings  the other columns in the system for which we are measuring arc counts
        Return
        arcs_same_time_list:  type=list  list of integers holding the arc counts for every other column HVSP that occur at the same time as arcs for col_hvsp input
    '''
    counts_list = []
    percentages_list = []                                                           # of all of col_hvsp's arc, what percent coincide with other_col_hvsp arcs
    arc_count = len(col_hvsp_arcs)
    if arc_count == 0:
        list_size = len(col_hvps_list) - 1
        counts_list = np.full(list_size, 0)
        percentages_list = np.full(list_size, np.nan)
        return counts_list, percentages_list
    print(f"{arc_count=}")
    for other_col_hvsp in col_hvsp_list:    
        other_idx = list(arc_count_df.columns).index(other_col_hvsp)
        if other_col_hvsp == col_hvsp:
            continue
        co_arcs = col_hvsp_arcs[col_hvsp_arcs[:, other_idx] > 0]
        count = co_arcs[:, other_idx].sum()
        if co_arcs.size != 0:
            print(f"{other_col_hvsp=}")
            print(" "*3, co_arcs[:, [0, col_idx, other_idx]])
            print(f"    {count=}\n")
        counts_list.append(count)
        percentages_list.append(100*count/arc_count)
    return counts_list, percentages_list
def synchronous_arcs_large_df(col_hvsp, col_idx, col_hvsp_list, col_hvsp_arcs):
    '''function to find the number of arcs a column HVPS component has at the same time as the given col_hvsp
        Arguments
        col_hvsp:  type=string  the given column HVSP component for which we are measuring other column HVSP arcs against
        col_hvsp_list:  type=list of strings  the other columns in the system for which we are measuring arc counts
        Return
        arcs_same_time_list:  type=list  list of integers holding the arc counts for every other column HVSP that occur at the same time as arcs for col_hvsp input
    '''
    counts_list = []
    percentages_list = []                                                           # of all of col_hvsp's arc, what percent coincide with other_col_hvsp arcs
    col_hvsp_arc_count = len(col_hvsp_arcs)
    if col_hvsp_arc_count == 0:
        list_size = len(col_hvps_list) - 1
        counts_list = np.full(list_size, 0)
        percentages_list = np.full(list_size, np.nan)
        return counts_list, percentages_list
    print(f"{col_hvsp_arc_count=}")
    for other_col_hvsp in col_hvsp_list:    
        other_idx = list(arc_count_df.columns).index(other_col_hvsp)
        if other_col_hvsp == col_hvsp:
            counts_list.append(0)
            percentages_list.append(0)
            continue
        co_arcs = col_hvsp_arcs[col_hvsp_arcs[:, other_idx] > 0]
        count = co_arcs[:, other_idx].sum()
        if co_arcs.size != 0:
            print(f"{other_col_hvsp=}")
            print(" "*3, co_arcs[:, [0, col_idx, other_idx]])
            print(f"    {count=}\n")
        counts_list.append(count)
        percentages_list.append(100*count/col_hvsp_arc_count)
    
    return counts_list, percentages_list
### MAIN FUNCTIONS ###
def sequential_clusters_main(col_hvps_list, arc_count_arr):
    # 63 SMALL DATAFRAMES, 7 [Col] x 9 [HVPS] PLOTS
    print("RUNNING SEQUENTIAL INDIVIDUAL FORMAT ARC CLUSTER PROCESS")
    print()
    for col_idx, col_hvps in enumerate(col_hvps_list):
        # TERMINAL OUTPUT READABILITY
        lenght_symbol = (74-len(col_hvps))//2
        print(f"{'+'*lenght_symbol}{col_hvps}{'+'*lenght_symbol}")
        # GET ARC TIMES
        col_hvps_arcs = get_arc_times(col_idx+1, arc_count_arr)                                        # col_idx from enumerate will be offset by 1 from proper index in arc_counts
        # CO-ARC COUNTS & PERCENTAGES
        counts, percentages = synchronous_arcs(col_hvps, col_idx+1, col_hvps_list, col_hvps_arcs)
        # CAST PERCENTAGES
        percentages = [int(p) for p in np.nan_to_num(percentages)]
        # CREATE DATAFRAME
        df_cols = col_hvps_list[:col_idx] + col_hvps_list[col_idx+1:]
        col = [k[:2] for k in df_cols]
        hvps = [k[3:] for k in df_cols]
        iter_arc_cluster = pd.DataFrame({"Column": col, "HVPS": hvps, "Synchronous Arc Count": counts, "Synchronous Arc Percentage": percentages})
        #iter_arc_cluster[['Column', 'HVPS']] = iter_arc_cluster['column_HVSP'].str.split(' ', expand=True)
        #iter_arc_cluster.drop('Full Name', axis=1, inplace=True)
        if sum(counts) > 0:
            print(iter_arc_cluster)
            # INITIALIZE PLOTS
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 10))
            # DATA TRANSFORMATION FOR SEPARATE PLOTS
            count_plot_data = iter_arc_cluster[["Column", "HVPS", "Synchronous Arc Count"]]
            percentage_plot_data = iter_arc_cluster[["Column", "HVPS", "Synchronous Arc Percentage"]]
            pivot_count = count_plot_data.pivot(index='Column', columns='HVPS', values='Synchronous Arc Count')
            pivot_percentage = percentage_plot_data.pivot(index='Column', columns='HVPS', values='Synchronous Arc Percentage')
            # CONSTRUCT COUNT PLOT
            sns.heatmap(pivot_count, annot=True, cmap="YlGnBu", fmt="g", ax = axes[0])
            axes[0].set_title(f'Heatmap of Synchronous {col_hvps} Arc Count')
            # CONSTRUCT PERECENTAGE PLOT
            sns.heatmap(pivot_percentage, annot=True, cmap="YlGnBu", fmt="g", ax = axes[1])
            axes[1].set_title(f'Heatmap of Synchronous {col_hvps} Arc Percentage')
            # SAVE FIGURE
            title = f"{col_hvps} Same Time Arc Clusters"
            count_filename = f"{title}.pdf".replace(" ", "_")
            output_dir = "plots/arc_clusters/"
            os.makedirs(output_dir, exist_ok=True)
            print(f"Saving sequential plots to {output_dir}")
            plt.savefig(f"{output_dir}{count_filename}", format='pdf')
def large_cluster_main(col_hvps_list):
    # 1 LARGE DATAFRAME, 63 x 63 PLOT
    print("RUNNING LARGE FORMAT ARC CLUSTER PROCESS")
    print()
    arc_cluster_arr = []
    for col_idx, col_hvps in enumerate(col_hvps_list):
        # TERMINAL OUTPUT READABILITY
        lenght_symbol = (74-len(col_hvps))//2
        print(f"{'+'*lenght_symbol}{col_hvps}{'+'*lenght_symbol}")
        # GET ARC TIMES
        col_hvps_arcs = get_arc_times(col_idx+1, arc_count_arr)                                        # col_idx from enumerate will be offset by 1 from proper index in arc_counts
        # CO-ARC COUNTS & PERCENTAGES
        counts, percentages = synchronous_arcs_large_df(col_hvps, col_idx+1, col_hvps_list, col_hvps_arcs)
        print(f"{counts=}")
        # CAST PERCENTAGES
        percentages = [int(p) for p in np.nan_to_num(percentages)]
        # CREATE DATAFRAME
        arc_cluster_arr.append(counts)
    arc_cluster_df = pd.DataFrame(arc_cluster_arr, columns=col_hvps_list)
    arc_cluster_df.insert(0, "Column HVPS", col_hvps_list)
    arc_cluster_df = arc_cluster_df.set_index("Column HVPS")
    arc_cluster_df = arc_cluster_df.fillna(0)
    data_output = 'data/arc_cluster_large.csv'
    print(f"\nSaving all components data to {data_output}\n")
    time.sleep(0.5)
    arc_cluster_df.to_csv(f'{data_output}', index=True)
    # CONDENSE (REMOVE 0 ARC COMPONENTS)
    arc_cluster_df_condensed = arc_cluster_df.loc[(arc_cluster_df != 0).any(axis=1)]
    arc_cluster_df_condensed = arc_cluster_df_condensed.loc[:, (arc_cluster_df_condensed != 0).any(axis=0)]
    print(arc_cluster_df_condensed)
    # PLOT
    plt.figure(figsize=(20, 16))
    sns.heatmap(arc_cluster_df_condensed, annot=True, cmap='viridis')
    plt.title('Heatmap of Synchronous Column Power Supply Component Arc Counts')
    output_dir = "plots/arc_clusters/"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving all components plot to {output_dir}")
    plt.savefig(f"{output_dir}All_Component_Synchronous_Arc_Counts.pdf", format = 'pdf')
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arc_filename',required=True)
    parser.add_argument('--sequential', required=False, default=False)
    parser.add_argument('--large', required=False, default=False)
    args = parser.parse_args()

    arc_filename = args.arc_filename
    sequential_format = args.sequential
    large_format = args.large

    arc_count_df, arc_count_arr = read_arc_data(arc_filename)
    col_hvps_list = list(arc_count_df.columns[1:])                                      # list of all Column HVPS to be looped through
    times = arc_count_arr[:, 0]                                                            # get all Time values
    if sequential_format: sequential_clusters_main(col_hvps_list, arc_count_arr)
    if large_format: large_cluster_main(col_hvps_list)