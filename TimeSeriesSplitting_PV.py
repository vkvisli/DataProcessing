"""

This module reads time-series data for photovoltaic (PV) solar panels associated with the CoSSMic project
and splits this data into individual 24 hour 'runs'. These runs are also split by season, and are saved as csv files.
Finally, it plots visual charts for both time-series data and the individual runs.

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

import csv
import os
from models.PV import PV

# File location and file names for original and edited data
single_run_output = "./data/edited/pv_runs/"
data_location = "./data/original/"
data_filename_1 = "household_data_1min_singleindex.csv"
data_filename_3 = "household_data_3min_singleindex.csv"
data_filename_15 = "household_data_15min_singleindex.csv"
data_filename_60 = "household_data_60min_singleindex.csv"

# Set which file and time resolution to use in these two variables
dataFilename = data_filename_3
time_res = 3

# The PV units and their various information are stored in a list of PV objects
PV_list = [PV("DE_KN_residential1_pv", "Photovoltaic 1"),
           PV("DE_KN_residential3_pv", "Photovoltaic 3"),
           PV("DE_KN_residential4_pv", "Photovoltaic 4"),
           PV("DE_KN_residential6_pv", "Photovoltaic 6")]

def read_PV_data(dataLocation, time_res):
    """
    Reads the specified data file and appends time and power data for each PV unit

    :param dataLocation: (str) The file to read
    :param time_res: (int) Resolution of the file to read in minutes
    """

    print("0%", end="\r", flush=True)

    # Count number of rows in file to show progress info
    rowCount = 0
    with open(dataLocation, "r") as data:
        rowCount = len(list(csv.reader((data))))

    with open(dataLocation, "r") as data:
        dataReader = csv.reader(data)
        header = next(dataReader, None)
        rows_executed = 0
        progress_percentage = 0
        new_progress_percentage = 0
        time_minutes = 0

        # Find the column numbers for each PV
        for pv in PV_list:
            column_nr = 0
            for item in header:
                if (item == pv.name):
                    pv.column_nr = column_nr
                    break
                column_nr += 1

        # Iterate each row in the data file
        for row in dataReader:

            # update progress bar
            new_progress_percentage = int(rows_executed / rowCount * 100)
            if (new_progress_percentage != progress_percentage):
                print(str(new_progress_percentage) + "%", end="\r", flush=True)
            progress_percentage = new_progress_percentage

            # Append time and power data points for each PV
            for pv in PV_list:
                pv.time_data.append(time_minutes) # Relative time in minutes
                pv.date_data_utc.append(row[0]) # UTC timestamp
                pv.date_data_cet_cest.append(row[1]) # CET/CEST timestamp
                if (row[pv.column_nr] != ""):
                    pv.power_data.append(float(row[pv.column_nr]))                    # append new value
                else:
                    pv.power_data.append(pv.power_data[-1] if pv.power_data else 0)    # append last value

            rows_executed += 1
            time_minutes += time_res

        print("100%")

def split_time_series():
    """ Splits the time-series of each PV unit in the PV list into individual 24 hour 'runs' by season """
    for pv in PV_list:
        pv.split_power_data_by_season(time_res)
        print(pv.display_name + ": " + str(len(pv.spring_runs)) + " spring days, " + str(len(pv.summer_runs)) + " summer days, " +
              str(len(pv.autumn_runs)) + " autumn days and " + str(len(pv.winter_runs)) + " winter days.")

def convert_to_non_cumulative():
    """ Converts all runs in each PV unit to non-cumulative versions """
    for pv in PV_list:
        pv.convert_to_non_cumulative()

def normalize_runs():
    """ Normalize the PV 'runs' to values between 0 and 1, separately for each PV unit """
    for pv in PV_list:
        pv.normalize_and_plot_profiles(time_res)

def save_season_runs(loc):
    """
    Saves all PV's season runs to separate csv files, both for normalized and non-normalized.
    The UTC start time for each run is added as the first value of each line.

    :param loc: (str) The location to save files
    """

    # Create directory to store the files, if it does not exist
    os.makedirs(loc, exist_ok=True)

    # Create the csv files
    for pv in PV_list:

        # Spring (normalized)
        with open(loc + pv.display_name + "_spring_normalized.csv", "w") as file:
            file.write(pv.name + "," + pv.display_name + "\n")
            start_time_index = 0
            for run in pv.spring_runs:
                file.write(pv.spring_runs_start_times[start_time_index] + ",")
                for i in range(len(run)):
                    file.write(str(run[i]))
                    if i < len(run) - 1:
                        file.write(",")
                file.write("\n")
                start_time_index += 1

        # Summer (normalized)
        with open(loc + pv.display_name + "_summer_normalized.csv", "w") as file:
            file.write(pv.name + "," + pv.display_name + "\n")
            start_time_index = 0
            for run in pv.summer_runs:
                file.write(pv.summer_runs_start_times[start_time_index] + ",")
                for i in range(len(run)):
                    file.write(str(run[i]))
                    if i < len(run) - 1:
                        file.write(",")
                file.write("\n")
                start_time_index += 1

        # Autumn (normalized)
        with open(loc + pv.display_name + "_autumn_normalized.csv", "w") as file:
            file.write(pv.name + "," + pv.display_name + "\n")
            start_time_index = 0
            for run in pv.autumn_runs:
                file.write(pv.autumn_runs_start_times[start_time_index] + ",")
                for i in range(len(run)):
                    file.write(str(run[i]))
                    if i < len(run) - 1:
                        file.write(",")
                file.write("\n")
                start_time_index += 1

        # Winter (normalized)
        with open(loc + pv.display_name + "_winter_normalized.csv", "w") as file:
            file.write(pv.name + "," + pv.display_name + "\n")
            start_time_index = 0
            for run in pv.winter_runs:
                file.write(pv.winter_runs_start_times[start_time_index] + ",")
                for i in range(len(run)):
                    file.write(str(run[i]))
                    if i < len(run) - 1:
                        file.write(",")
                file.write("\n")
                start_time_index += 1

# Read CSV data file with data for the PV units
print("Reading from '" + dataFilename + "'")
read_PV_data(data_location + dataFilename, time_res)

# Split the time-series into individual runs for each PV
print("Splitting time series into individual 24 hour profiles")
split_time_series()

# Plot cumulative production profiles (both for time-series and 24 hour profiles)
print("Saving figures for time series data and cumulative production profiles")
for pv in PV_list:
    pv.plot_time_series("Cumulative energy production time-series", "time_series")
    pv.plot_profiles(time_res, "Cumulative energy production profiles over 24 hours", "seasons_cumulative", "hours", "kWh")

# Convert all runs to non-cumulative versions
print("Converting to non-cumulative profiles")
convert_to_non_cumulative()

# Normalize the runs (separately for each PV and each season)
print("Normalizing profiles")
normalize_runs()

# Save PV runs in csv files (one for each PV and each season)
print("Saving normalized profiles to directory: " + single_run_output)
save_season_runs(single_run_output)