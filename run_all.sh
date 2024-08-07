#!/bin/sh

cd ..
chmod 777 Multibeam-main/
cd Multibeam-main

rm -rf plots/*
rm -rf data/tidy
find /direcname -maxdepth 1 -type f -delete
rm -rf pressure_spike_times/

echo
echo "Cleaning Data..."
python3 python_files/mebl_data_preprocess.py --arc_filename data/MEBL/*Arc* --pressure_filename data/MEBL/*Pressure*
echo
echo "Locating Pressure Spike Times..."
python3 python_files/pressure_spike_times.py --pressure_filename data/tidy/pressure_data --time_range 5
echo
echo "Identifying Synchronous Arc Clusters..."
python3 python_files/synchronous_arc_clusters.py --arc_filename data/tidy/all_arc_count_data --sequential True --large True
echo
echo "Measuring Pressure at Every Arc..."
python3 python_files/pressure_at_arcs.py --arc_filename data/tidy/all_arc_count_data --pressure_filename data/tidy/pressure_data --pressure_linegraphs True --delta_histograms True
echo
echo "Measuring Arcs at Every Pressure Spike..."
python3 python_files/arcs_at_pressure_spikes.py --arc_filename data/tidy/all_arc_count_data --pressure_filename data/tidy/pressure_data --chamber_json pressure_spike_times/chamber_spike_times_5_sec.json --column_json pressure_spike_times/column_spike_times_5_sec.json
