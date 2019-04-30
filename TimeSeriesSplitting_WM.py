"""

This module reads time-series data for washing machines associated with the CoSSMic project
and splits this data into individual washing cycles/runs. These runs are saved as csv files.
Finally, it plots visual charts for both time-series data and the individual runs.

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

import csv
import os
from models.Appliance import Appliance

# File location and file names for original and edited data
single_run_output = "./data/edited/wm_runs/"
data_location = "./data/original/"
data_filename_1 = "household_data_1min_singleindex.csv"
data_filename_3 = "household_data_3min_singleindex.csv"
data_filename_15 = "household_data_15min_singleindex.csv"
data_filename_60 = "household_data_60min_singleindex.csv"

# Set which file and time resolution to use in these two variables
dataFilename = data_filename_1
time_res = 1

# Washing machines and their various information are stored in a list of Appliance objects
appliance_list = [Appliance("DE_KN_residential1_washing_machine", "Washing Machine 1"),
                  Appliance("DE_KN_residential2_washing_machine", "Washing Machine 2"),
                  Appliance("DE_KN_residential3_washing_machine", "Washing Machine 3"),
                  Appliance("DE_KN_residential4_washing_machine", "Washing Machine 4"),
                  Appliance("DE_KN_residential5_washing_machine", "Washing Machine 5"),
                  Appliance("DE_KN_residential6_washing_machine", "Washing Machine 6")]

def readApplianceData(dataLocation, time_res):
    """
    Reads the specified data file and appends time and power data for each appliance

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

        # Find the column numbers for each appliance
        for a in appliance_list:
            column_nr = 0
            for item in header:
                if (item == a.name):
                    a.column_nr = column_nr
                    break
                column_nr += 1

        # Iterate each row in the data file
        for row in dataReader:

            # update progress bar
            new_progress_percentage = int(rows_executed / rowCount * 100)
            if (new_progress_percentage != progress_percentage):
                print(str(new_progress_percentage) + "%", end="\r", flush=True)
            progress_percentage = new_progress_percentage

            # Append time and power data points for each appliance
            for a in appliance_list:
                a.time_data.append(time_minutes)
                a.date_data.append(row[1])
                if (row[a.column_nr] != ""):
                    a.power_data.append(float(row[a.column_nr]))                    # append new value
                else:
                    a.power_data.append(a.power_data[-1] if a.power_data else 0)    # append last value

            rows_executed += 1
            time_minutes += time_res

        print("100%")

def plot_time_series_data():
    """ Plots time-series data for each appliance in the appliance list """
    for a in appliance_list:
        a.plot_time_series()

def plot_single_runs():
    """ Plots single run profiles for each appliance in the appliance list """
    for a in appliance_list:
        a.plot_single_runs()

def split_time_series():
    """ Splits the time-series of each appliance in the appliance list into individual runs """
    for a in appliance_list:
        a.split_power_data(max_pause_allowed=1, min_duration=10, max_consumption=5)
        print("single runs for " + a.display_name + ": " + str(len(a.single_runs)))
        a.shrink_runs()

def save_single_runs(data_location):
    """
    Saves all appliances' single runs to separate csv files in the given location

    :param data_location: (str) The location to save files
    """

    # Create directory to store the files, if it does not exist
    os.makedirs(data_location, exist_ok=True)

    # Create the csv files
    for a in appliance_list:
        with open(data_location + a.display_name + ".csv", "w") as file:
            file.write(a.display_name + "\n")
            for run in a.single_runs:
                for i in range(len(run)):
                    file.write(str(run[i]))
                    if i < len(run) - 1:
                        file.write(",")
                file.write("\n")

# Read CSV file with appliance data
print("Reading from '" + dataFilename + "'")
readApplianceData(data_location + dataFilename, time_res)

# Split the time-series into individual runs for each appliance
print("Splitting time-series into individual runs")
split_time_series()

# Save single runs in csv files
save_single_runs(single_run_output)
print("Single runs saved to directory: " + single_run_output)

# Plot the graphs for time-series and splitting results
print("Plotting figures...")
plot_time_series_data()
plot_single_runs()