"""

This module performs categorization of PV runs/profiles into weather types
(sunny, partially cloudy, cloudy, and rainy), based on their total energy generation.
The categorization is done on the already season-separated runs created with "TimeSeriesSplitting_PV".
JSON files for each category is saved and visual charts showing the weather categories are displayed.

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

import csv
from models.PV_Season import PV_Season
import os
import dateutil

# Data locations and file names
data_location = "./data/edited/pv_runs/"
category_output_location = "./data/edited/pv_categories/"
spring_filenames = ["Photovoltaic 1_spring", "Photovoltaic 3_spring", "Photovoltaic 4_spring", "Photovoltaic 6_spring"]
summer_filenames = ["Photovoltaic 1_summer", "Photovoltaic 3_summer", "Photovoltaic 4_summer", "Photovoltaic 6_summer"]
autumn_filenames = ["Photovoltaic 1_autumn", "Photovoltaic 3_autumn", "Photovoltaic 4_autumn", "Photovoltaic 6_autumn"]
winter_filenames = ["Photovoltaic 1_winter", "Photovoltaic 3_winter", "Photovoltaic 4_winter", "Photovoltaic 6_winter"]

output_filenames = ["spring_sunny.json", "spring_partially_cloudy.json", "spring_cloudy.json", "spring_rainy.json",
                    "summer_sunny.json", "summer_partially_cloudy.json", "summer_cloudy.json", "summer_rainy.json",
                    "autumn_sunny.json", "autumn_partially_cloudy.json", "autumn_cloudy.json", "autumn_rainy.json",
                    "winter_sunny.json", "winter_partially_cloudy.json", "winter_cloudy.json", "winter_rainy.json"]

# Set which time resolution the PV data was read with
minute_res = 3

def read_PV_normalized_data(filenames, season):
    """
    Reads the specified PV season files with normalized data and start times, and returns a list of PV_Season objects

    :param filenames: (list) A list of strings containing the file names
    :param season: (str) The season of the data to be read
    :return: (list) A list of PV_Season objects
    """
    PV_seasons = []
    for filename in filenames:
        with open(data_location + filename + "_normalized.csv", "r") as data:
            dataReader = csv.reader(data)
            header = next(dataReader, None)
            pv_season = PV_Season(header[0], header[1], season)

            for row in dataReader:
                start_time = row[0]
                run = []
                for i in range(1, len(row)):
                    run.append(float(row[i]))

                pv_season.runs.append(run)
                pv_season.runs_start_times.append(start_time)

            PV_seasons.append(pv_season)

    return PV_seasons

def assign_weather_types(pv_season_list):
    """
    For each PV_Season, assign all its runs and start times to the correct weather type

    :param pv_season_list: (list) The list containing PV_Season objects
    """

    for PV_season in pv_season_list:
        w_limits = PV_season.accumulated_weather_limits(4)
        if w_limits != None:
            start_time_index = 0
            for run in PV_season.runs:
                if w_limits[0] <= sum(run) < w_limits[1]:
                    PV_season.rainy_runs.append(run)
                    PV_season.rainy_runs_start_times.append(PV_season.runs_start_times[start_time_index])
                elif w_limits[1] <= sum(run) < w_limits[2]:
                    PV_season.cloudy_runs.append(run)
                    PV_season.cloudy_runs_start_times.append(PV_season.runs_start_times[start_time_index])
                elif w_limits[2] <= sum(run) < w_limits[3]:
                    PV_season.partially_cloudy_runs.append(run)
                    PV_season.partially_cloudy_runs_start_times.append(PV_season.runs_start_times[start_time_index])
                elif w_limits[3] <= sum(run) <= w_limits[4]:
                    PV_season.sunny_runs.append(run)
                    PV_season.sunny_runs_start_times.append(PV_season.runs_start_times[start_time_index])
                start_time_index += 1

def save_to_json(pv_season_list, location):
    """
    Saves all runs and their corresponding meta data, one file per season and weather type.

    :param pv_season_list: (list) The list containing PV_Season objects
    :param location: (str) The location to save files
    """
    # Create files to store runs in
    initiateFiles(location)

    for PV_season in pv_season_list:

        # Append sunny runs
        for i in range(len(PV_season.sunny_runs)):
            filename = location + "/" + PV_season.season + "_sunny.json"
            run = PV_season.sunny_runs[i]
            start_time = PV_season.sunny_runs_start_times[i]
            fileContentAppend(filename, run, start_time, PV_season.name, PV_season.tilt, PV_season.orientation, minute_res)

        # Append partially cloudy runs
        for i in range(len(PV_season.partially_cloudy_runs)):
            filename = location + "/" + PV_season.season + "_partially_cloudy.json"
            run = PV_season.partially_cloudy_runs[i]
            start_time = PV_season.partially_cloudy_runs_start_times[i]
            fileContentAppend(filename, run, start_time, PV_season.name, PV_season.tilt, PV_season.orientation, minute_res)

        # Append cloudy runs
        for i in range(len(PV_season.cloudy_runs)):
            filename = location + "/" + PV_season.season + "_cloudy.json"
            run = PV_season.cloudy_runs[i]
            start_time = PV_season.cloudy_runs_start_times[i]
            fileContentAppend(filename, run, start_time, PV_season.name, PV_season.tilt, PV_season.orientation, minute_res)

        # Append rainy runs
        for i in range(len(PV_season.rainy_runs)):
            filename = location + "/" + PV_season.season + "_rainy.json"
            run = PV_season.rainy_runs[i]
            start_time = PV_season.rainy_runs_start_times[i]
            fileContentAppend(filename, run, start_time, PV_season.name, PV_season.tilt, PV_season.orientation, minute_res)

    # End files by adding closing brackets
    endFiles(location)

def initiateFiles(location):
    """
    Creates json files for each combination of season and weather type,
    and write the property to hold the data objects for production profiles.
    It also creates the directory to store the files, if it does not exist

    :param location: (str) The location to create the files in
    """

    os.makedirs(location, exist_ok=True)
    for filename in output_filenames:
        with open(location + filename, "w") as file:
            file.write("{\n    \"data\": [")

def endFiles(location):
    """
    'Ends' the files for production profiles by removing the trailing comma,
    and writing closing brackets for the objects

    :param location: (str) The location of the files to end
    """

    for filename in output_filenames:
        with open(location + filename, "a") as file:
            file.seek(file.tell() - 1, os.SEEK_SET)
            file.truncate()
            file.write("\n    ]\n}")


def fileContentAppend(filename, run, start_time, pv_name, pv_tilt, pv_orientation, minute_res):
    """
    Appends the given properties as an object in the json files for production profiles

    :param filename: (str) The file to append
    :param run: (list) The production profile
    :param start_time: (int) The start time in Unix UTC
    :param pv_name: (str) The name of the PV module
    :param pv_tilt: (int) The tilt angle of the PV module
    :param pv_orientation: The horizontal orientation angle of the PV module
    :param minute_res: (int) The time resolution in minutes
    """

    unix_UTC_start_time = dateutil.parser.parse(start_time).timestamp()
    new_content = "\n        {\n"
    new_content += "            \"pvName\": \"" + pv_name + "\",\n"
    new_content += "            \"pvTilt\": \"" + str(pv_tilt) + "\",\n"
    new_content += "            \"pvOrientation\": \"" + str(pv_orientation) + "\",\n"
    new_content += "            \"unixStartUTC\": " + str(int(unix_UTC_start_time)) + ",\n"
    new_content += "            \"minuteRes\": " + str(minute_res) + ",\n"
    new_content += "            \"profile\": " + str(run) + "\n"
    new_content += "        },"

    with open(filename, "a") as file:
        file.write(new_content)

# Read the season-separated and normalized PV data and store it in a list containing PV_Season objects
print("Reading normalized PV data from " + data_location)
PV_season_list = read_PV_normalized_data(spring_filenames, "spring")
PV_season_list += read_PV_normalized_data(summer_filenames, "summer")
PV_season_list += read_PV_normalized_data(autumn_filenames, "autumn")
PV_season_list += read_PV_normalized_data(winter_filenames, "winter")

# Assign a weather type to all runs in all PV_Seasons
print("Assigning weather types to profiles")
assign_weather_types(PV_season_list)

# Saves the runs to json files
print("Saving the profiles to json files...")
save_to_json(PV_season_list, category_output_location)

# Print number of days in each weather type
for PV_season in PV_season_list:
    print(PV_season.display_name + " " + PV_season.season + ": ")
    print(str(len(PV_season.sunny_runs)) + " sunny runs")
    print(str(len(PV_season.partially_cloudy_runs)) + " partially cloudy runs")
    print(str(len(PV_season.cloudy_runs)) + " cloudy runs")
    print(str(len(PV_season.rainy_runs)) + " rainy runs")
    print("")

# Plot weather types
print("Plotting figures")
for PV_season in PV_season_list:
    PV_season.plot_weather_runs_accumulated(minute_res)
