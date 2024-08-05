#!/usr/bin/python3
### IMPORTS ###
import pandas as pd
import numpy as np
import re
import argparse
import os
import errno
### HELPER FUNCTIONS ####
def arc_tidy(filename):
    arc_count_df = pd.read_csv(filename, parse_dates=['Time']).fillna(0)
    print(f"{filename} : file read into a pandas dataframe.")
    # DROP PRESSURE COLUMNS (STORED SEPARATELY)
    arc_count_df = arc_count_df.drop(arc_count_df.columns[1:3], axis=1)
    # USE REGEX TO REPLACE QUERY FORMATTED VARIABLE NAMES WITH SYSTEM COLUMN AND COLUMN COMPONENT
    arc_count_vars = arc_count_df.columns
    arc_count_vars = list(arc_count_vars)
    for i in range(len(arc_count_vars)):
        pattern = r'\{([B-D]{1}[2-4]{1}) Arc Count=\"(.*)\"\}'
        try:
            match = re.findall(pattern, arc_count_vars[i])
            replacement = match[0][0] + ' ' + match[0][1]
            #print(replacement)
            arc_count_vars[i] = replacement
        except:
            print(f"No match for {arc_count_vars[i]}")
    arc_count_df.columns = arc_count_vars
    # CONVERT "Time" VARIABLE FROM STRING TO DATETIME OBJECT
    arc_count_df['Time'] = pd.to_datetime(arc_count_df['Time'])
    # WRTIE PREPROCESSED ARC COUNT DATAFRAME TO CSV
    arc_count_df.to_csv('data/tidy/all_arc_count_data', index = False)
def pressure_tidy(filename):
    # READ-IN PRESSURE DATA DATAFRAME
    pressure_df = pd.read_csv(filename).fillna(0)
    print(f"{filename} : file read into a pandas dataframe.")
    # CONVERT "Time" VARIABLE FROM STRING TO DATETIME OBJECT
    pressure_df['Time'] = pd.to_datetime(pressure_df['Time'])
    pressure_df.to_csv('data/tidy/pressure_data', index = False)
### MAIN FUNCTION ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arc_filename',required=True)
    parser.add_argument('--pressure_filename',required=True)
    args = parser.parse_args()
    arc_filename = args.arc_filename
    pressure_filename = args.pressure_filename
    output_dir = "data/tidy/"
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
        else:
            raise
    arc_tidy(arc_filename)
    pressure_tidy(pressure_filename)