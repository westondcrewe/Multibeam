## REPOSITORY FOR MULTIBEAM ARC AND PRESSURE DATA ANALYSIS

#### File Descriptions
- ```mebl3_data_preprocess.ipynb``` makes the original dataframes tidy (original and cleaned dataframes are in ```data/MEBL3```, which only exists locally)
- ```pressure_spikes.ipynb``` identifies timestamps of spikes in the Column Pressure and Chamber Pressure measurements of MEBL3
    * Timestamp values are saved as JSON dictionaries in ```data/pressure_spike_times```
- ```arc_at_pressure_spikes.ipynb``` takes the timestamps of ```data/pressure_spike_times``` and identifies arc events that are synchronous with these pressure spikes
    * Arc counts, counts of arc synchronous with pressure spikes, and percents of arc synchronous with pressure spikes are calculated for each Column - High Voltage Power Supply component; saved as dataframe in ```data/arcs_with_pressure_spikes```
    * This file also generates plots for the total arc counts (```plots/Total_Arc_Counts.pdf```) and for counts & percentages of synchronous arc-pressure spike events (```plots/arcs_with_pressure_spikes```)
- ```synchronous_arc_clusters.ipynb``` identifies synchronous arc events between Column - High Voltage Power Supply components
    * Heatmaps of these synchronous arc events (both as counts and percentages of total component arc events) are stored in ```plots/arc_clusters```
- ```pressure_at_arcs``` files (3 of them) were created for the purpose of generating lineplots of pressure data (both chamber and column vacuums) for a 20 second window surrounding an arc event. Plots are produced and stored in ```plots/pressure_at_arcs/``` with every subfolder holding plots for each arc by column power supply component. 3 were made during the iterative project development cycle, as I was constantly trying to improve the effectiveness of plots and speed of the data filtration process, but the 3rd one is the best one to use.
- All files beginning with ```window_``` were created in the beginning phase of this project and were originally meant to be a tool for visualizing small chunks of data
    * Ultimately, the only one of these files that was useful to the whole project is ```window_pressure.ipynb```, as it is used to generate the plots of pressure values around spike events in ```plots/pressure_spikes```
- ```Z_arc_events_timestamp.ipynb``` is NOT USED, instead it acted as brainstorming for the tasks accomplished by ```arc_at_pressure_spikes.ipynb```
