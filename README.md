## REPOSITORY FOR MULTIBEAM ARC AND PRESSURE DATA ANALYSIS

All plots and data results stored in this repository are for MEBL3 data. 
When the ```run_all.sh``` script runs, all plots and data results are erased, so it is recommended to run this script when using brand new (non-MEBL3)system data.

### <ins>Cloning GitHub Remote Repository Onto Local Machine and Running from Terminal</ins>
1. Make sure you are on the `main` branch of the `Multibeam` GitHub remote repository
2. Click the green dropdown menu labelled "< > Code"; select "Download ZIP" and unzip the downloaded file
3. Open the terminal/command line on your local machine; Use the `cd` command to navigate to the repository's root directory, ```Multibeam-main/```
4. Run the following command to ensure all necessary libraries and packages are installed (at most 5 packages will be installed):
```
sh library_package_installs.sh
```
5. To run individual features within the project repository, follow along with the provided **Flowchart and Manual**
5. Alternatively, to run the entire project in one go, use the following command to run the ```run_all.sh``` script (must have MEBL data downloaded already, see Flowchart and Manual pt.1):
```
sh run_all.sh
```
### <ins>Flowchart and Manual</ins>
![Project Flowchart](WCMultibeamProjectFlowchart.png)
1. Database is accessed via Grafana; `all arc counts` and `pressure` data is downloaded to the repository’s `data/MEBL/` subfolder.
2. The two downloaded dataframes are passed into the file `mebl_data_preprocess.py`, which cleans the data and passes the tidy files to the `data/tidy/` subfolder. This becomes the new data source for the rest of the programs to run. 
    - Terminal command to run `mebl_data_preprocess.py` (current directory is repository’s root, all programs and scripts are in the folder `python_files/`):
    ```
    python3 python_files/mebl_data_preprocess.py --arc_filename data/MEBL/MEBL3_All\ Arc\ Counts-data-as-joinbyfield-2024-07-01\ 10_16_54.csv --pressure_filename data/MEBL/MEBL3_Pressure-data-2024-06-28\ 09_40_08.csv
    ``` 
    - Note: 
        - `–-arc_filename`, `–-pressure_filename` arguments are required, and should be the relative paths to the downloaded MB csv files 
        - If filenames include whitespace, put an escape character (\ ) before the whitespace
3. The tidy `pressure_data` file is used as input to the `pressure_spike_times.py` file, which identifies and stores the timestamps of all system vacuum pressure spikes.
    - Pressure spikes are defined as observations in the pressure dataset for which the pressure value exceeds 2x the “local pressure mean”. This mean is calculated from the pressure values of the 10 preceding seconds to the spike time
    - Terminal command to run: 
    ```
    python3 python_files/pressure_spike_times.py --pressure_filename data/tidy/pressure_data --time_range 5
    ```
    - Note: 
        - `–-pressure_filename` argument is required; it is the path to the clean pressure_data file 
        - `–-time_range` argument is optional; it is the number of seconds for which a local mean pressure value is calculated, a factor in the identification of the spike threshold (default=5)
        - Pressure spike timestamps are separated by pressure type and time_range (this information is held in the filenames) and saved as JSON files to the `pressure_spike_times/` folder
4. Once pressure_spikes have been saved, any of the 3 features may be utilized:
    1. `synchronous_arc_clusters.py`
    2. `pressure_at_arcs.py`
    3. `arcs_at_pressure_spikes.py` and `window_pressure.py`
### <ins>synchronous_arc_clusters.py</ins>
**Inputs:**
- Only the clean `all_arc_data` file is passed as an input

**Outputs:**
- `plots/arc_clusters`
    - A folder containing heatmaps displaying synchronous arc counts and percentages
    - Arcs are considered synchronous if an arc event occurs at the same time for two different system components 
    - Heatmaps of these synchronous arcs are made for each component, as well as one heatmap displaying the entire synchronous arc dataframe for all system components
- `data/results/arc_cluster_large.csv`
    - If the `--large` format is used, then that corresponding dataframe will be saved
    - Too many dataframes are made during the `--sequential` process, and all of that information is held within the large dataframe, so those dataframes are not saved

**Terminal command to run:**
```
python3 python_files/synchronous_arc_clusters.py --arc_filename data/tidy/all_arc_count_data --sequential True --large True
```
- <ins>Note</ins>:
    - `--arc_filename` argument is required; path to tidy arc data file
    - `--sequential` and `--large` are optional arguments; these tell the program what the desired outputs are. A `True` sequential argument will produce outputs for each system component one by one (several small format heatmaps), and a `True` large argument produces an output for the entire synchronous arc dataframe with every system component contained in one plot. Default values are `False`, so to indicate the desired outputs you must provide the argument as `True` (otherwise it may be left out of the terminal command all together)

### <ins>pressure_at_arcs.py</ins>:
**Inputs:**
- Scripts take both clean data files from `data/tidy/`

**Outputs:**
- `plots/pressure_at_arcs/`
    - A folder containing time-series line graphs of the system’s chamber and column pressure values over 30 second windows surrounding each arc event
    - The folder is made up of one subfolder for every system power supply component, and each of those folders contains one plot for every arc event that happened within that component
    - Plots also display pressure maximums (within +/- 5 seconds to the arc events), and pressure means for the 10 seconds preceding the maximum
- `plots/pressure_delta_histograms/`
    - A folder containing histograms displaying the distribution of “pressure delta” values across all arc events
    - Pressure deltas are calculated as the difference between the pressure maximum and pressure mean (as described in 6.b.i)
    - Histograms are created for both chamber and column pressure types, and the corresponding data is saved to `data/results/deltas/`

**Terminal command to run:**
```
python3 python_files/pressure_at_arcs.py --arc_filename data/tidy/all_arc_count_data --pressure_filename data/tidy/pressure_data --pressure_linegraphs True --delta_histograms True --n_bins 80
```
- <ins>Note</ins>:
    - `--arc_filename`, `--pressure_filename` arguments are required; paths to tidy data
    - `--pressure_linegraphs`, `--delta_histograms`, `--n_bins` are optional arguments; ; these tell the program what the desired outputs are. A `True` pressure_linegraph argument will produce the linegraphs for the `plots/pressure_at_arcs/` folder, and a `True` delta_histograms argument produces the histograms for `plots/pressure_delta_histograms`. Default values for these arguments are `False`, so to indicate the desired outputs you must provide the argument as `True` (otherwise it may be left out of the terminal command all together). The `n_bins` argument is strictly for formatting the delta histograms, giving user ability to select the number of bins for that plot (default = 75).

### <ins>arcs_at_pressure_spikes.py</ins> and <ins>window_pressure.py</ins>:
**Inputs:**
- Both clean dataframes from `data/tidy/` and both json files in `pressure_spike_times/` are used as input'

**Outputs:**
- `plots/Total_Arc_Counts.pdf`
    - A barchart showing how many total arcs there are for each system power supply component
- `plots/pressure_spikes/`
    - A folder that contains time-series line-graph plots displaying the vacuum pressure values over a 20s range surrounding every spike event
- `plots/arcs_at_pressure_spikes/`
    - A folder containing barcharts of the counts and percentages of arcs that occurred at the same time as a pressure spike for every system power supply component 
    - The corresponding dataframe is saved to `data/results/arcs_at_pressure_spikes.csv`

**Terminal command to run:**
```
python3 python_files/arcs_at_pressure_spikes.py --arc_filename data/tidy/all_arc_count_data --pressure_filename data/tidy/pressure_data --chamber_json pressure_spike_times/chamber_spike_times_5_sec.json --column_json pressure_spike_times/column_spike_times_5_sec.json
```
- <ins>Note</ins>: 
    - `-–arc_filename`, `–-pressure_filename`, `–-chamber_json`, `–-column_json` are all required, must be relative paths to each respective data file
    - The `window_pressure.py` file is inherited by the `arcs_at_pressure_spikes.py` file, so no commands need to be run for that script specifically
