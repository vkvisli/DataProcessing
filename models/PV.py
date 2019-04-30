"""

This module contains the class PV which is used to represent photovoltaic units/systems and their data

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

import matplotlib.pyplot as plt
import os

class PV:
    """
    The class PV represent a PV photovoltaic unit/system and contains various information
    about its 24 hour 'runs', as well as logic for e.g. normalization,
    chart plotting and splitting of time-series data.
    """

    def __init__(self, name, display_name):
        self.name = name
        self.display_name = display_name
        self.column_nr = 0
        self.time_data = []
        self.power_data = []
        self.date_data_utc = []
        self.date_data_cet_cest = []

        # Season runs
        self.spring_runs = []
        self.summer_runs = []
        self.autumn_runs = []
        self.winter_runs = []

        # Start times for each run in the season runs
        self.spring_runs_start_times = []
        self.summer_runs_start_times = []
        self.autumn_runs_start_times = []
        self.winter_runs_start_times = []

    def normalize_and_plot_profiles(self, minute_res):
        """
        Normalizes all profiles in this PV to values between 0 and 1,
        relative to optimal values across all runs within each season of this PV unit.
        Figures displaying the optimal profile, compared to the other profiles are saved.

        :param minute_res: (int) the minutely resolution of profiles
        """

        # The seasons to iterate
        seasons = [self.spring_runs, self.summer_runs, self.autumn_runs, self.winter_runs]
        season_names = ["spring", "summer", "autumn", "winter"]
        season_name_index = 0

        # Hours to display on x axis
        hours = [0]
        for i in range(len(self.spring_runs[0]) - 1):
            hours.append(hours[i] + (minute_res / 60))

        # Iterate each season
        for season in seasons:
            season_name = season_names[season_name_index]
            season_name_index += 1

            plt.clf()

            # Skip to next if there are no runs in this season
            if len(season) == 0:
                continue

            # Create an optimal profile for the current season by iterating all samples
            # in that season in this PV unit and for each sample pick from the run with
            # the highest values at that sample. This is then the reference for normalization
            optimal_season_run = season[0].copy()
            for run in season:
                plt.plot(hours, run, linewidth=0.2, color="blue")
                for i in range(len(run)):
                    if run[i] > optimal_season_run[i]:
                        optimal_season_run[i] = run[i]

            # Normalize all values in all runs within the current season of this PV unit
            # by dividing by the values of the optimal profile. If the value in optimal is 0,
            # the value 0 is inserted, since it can't be divided by 0.
            for i in range(len(season)):
                for j in range(len(season[i])):
                    if optimal_season_run[j] != 0:
                        season[i][j] = season[i][j] / optimal_season_run[j]
                    else:
                        season[i][j] = 0


            # Plot the figures
            plt.title(self.display_name + " (" + season_name + ")\n" + "Optimal production profile")
            plt.xlabel("hours")
            plt.ylabel("kWh")
            plt.plot(hours, optimal_season_run, color="red")
            os.makedirs("./figures/PV/optimal_profiles/", exist_ok=True)
            plt.savefig("./figures/PV/optimal_profiles/" + self.display_name + "_" + season_name + "_optimal.png")

    def convert_to_non_cumulative(self):
        """
        Convert all runs in this PV unit to non-cumulative versions
        """
        for i in range(len(self.spring_runs)):
            self.spring_runs[i] = self.non_cumulative(self.spring_runs[i])
        for i in range(len(self.summer_runs)):
            self.summer_runs[i] = self.non_cumulative(self.summer_runs[i])
        for i in range(len(self.autumn_runs)):
            self.autumn_runs[i] = self.non_cumulative(self.autumn_runs[i])
        for i in range(len(self.winter_runs)):
            self.winter_runs[i] = self.non_cumulative(self.winter_runs[i])

    def non_cumulative(self, cProfile):
        """
        Returns a non-cumulative version of a cumulative profile

        :param cProfile: (list) a cumulative profile to convert
        :return: (list) the non-cumulative version of the profile
        """
        profile = []
        profile.append(cProfile[0])
        for i in range(1, len(cProfile)):
            profile.append(cProfile[i] - cProfile[i - 1])
        return profile

    def cumulative(self, profile):
        """
        Returns a cumulative version of a non-cumulative profile

        :param profile: (list) a non-cumulative profile to convert
        :return: (list) the cumulative version of the profile
        """
        cProfile = []
        cProfile.append(profile[0])
        for i in range(1, len(profile)):
            cProfile.append(cProfile[-1] + profile[i])
        return cProfile

    def split_power_data_by_season(self, minute_res):
        """
        Splits the PV generation time-series data into individual days (24 hours),
        and store separate lists of runs for each season. The data is split when the local time (CET/CEST)
        is 00:00 and the UTC time stamp for this sample is stored. The runs are then shrinked/scaled down
        to they all start at 0 kWh.

        :param minute_res: (int) The minutely resolution of profiles
        """

        current_run = []
        current_run_start_utc = None
        i = 0

        # Iterate the data and add a new run for each day, excluding days with no production (missing data)
        for d in self.date_data_cet_cest:

            # If first iteration, set UTC start time to the first element
            if current_run_start_utc is None:
                current_run_start_utc = self.date_data_utc[i]

            # Check if it is a new day (CET/CEST hours and minutes = 00)
            if d[11:13] == "00" and d[14:16] == "00":

                # append runs to seasons based on month number, if it is not considered 'noise'
                # and store the UTC time stamp for the start of each run
                if not self.is_noise(current_run, minute_res):
                    if d[5:7] == "03" or d[5:7] == "04" or d[5:7] == "05":
                        self.spring_runs.append(current_run)
                        self.spring_runs_start_times.append(current_run_start_utc)
                    elif d[5:7] == "06" or d[5:7] == "07" or d[5:7] == "08":
                        self.summer_runs.append(current_run)
                        self.summer_runs_start_times.append(current_run_start_utc)
                    elif d[5:7] == "09" or d[5:7] == "10" or d[5:7] == "11":
                        self.autumn_runs.append(current_run)
                        self.autumn_runs_start_times.append(current_run_start_utc)
                    elif d[5:7] == "12" or d[5:7] == "01" or d[5:7] == "02":
                        self.winter_runs.append(current_run)
                        self.winter_runs_start_times.append(current_run_start_utc)

                # Reset the current run, and set UTC start time for the next run to this sample
                current_run = []
                current_run_start_utc = self.date_data_utc[i]

            # Append power data to the current run
            current_run.append(self.power_data[i])
            i += 1

        # Shrink/scale/shift down the runs so they all start at 0 kWh
        self.shrink_runs()

    def shrink_runs(self):
        """ Shrinks/scales the values of each PV run, so that each run start at 0 kWh """
        season_runs = [self.spring_runs, self.summer_runs, self.autumn_runs, self.winter_runs]
        for season in season_runs:
            for run in season:
                if run:
                    pos_0 = run[0]
                    for i in range(len(run)):
                        run[i] = run[i] - pos_0

    def plot_profiles(self, minute_res, title, filename_tail, xlabel, ylabel):
        """
        Plots all individual profiles of this PV, one color for each season

        :param minute_res: (int) The minutely resolution used between samples
        :param title: (string) The title of the figure
        :param filename_tail: (string) text to include at the end of the filename
        :param xlabel: (string) text to display on x axis
        :param ylabel: (string) text to display on y axis
        """
        plt.clf()
        plt.figure(figsize=(14, 8.75))
        spring_lines, summer_lines, autumn_lines, winter_lines = None, None, None, None

        hours = [0]
        for i in range(len(self.spring_runs[0])-1):
            hours.append(hours[i] + (minute_res / 60))

        for run in self.spring_runs:
            spring_lines, = plt.plot(hours, run, color="red")
        for run in self.summer_runs:
            summer_lines, = plt.plot(hours, run, color="green")
        for run in self.autumn_runs:
            autumn_lines, = plt.plot(hours, run, color="orange")
        for run in self.winter_runs:
            winter_lines, = plt.plot(hours, run, color="blue")

        plt.title(self.display_name + "\n" + title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend([spring_lines, summer_lines, autumn_lines, winter_lines],
                   ["Spring", "Summer", "Autumn", "Winter"])

        # Create directory 'figures' and 'PV' if they do not exist, and save figure
        os.makedirs("./figures/PV/", exist_ok=True)
        plt.savefig("./figures/PV/" + self.display_name + "_" + filename_tail + ".png")

    def plot_time_series(self, title, filename_tail):
        """
        Plots the cumulative time-series data for this PV

        :param title: (string) The title of the figure
        :param filename_tail: (string) text to include at the end of the filename
        """

        months = []
        for i in range(len(self.time_data)):
            months.append(self.time_data[i] / 60 / 24 / 365 * 12)

        plt.clf()
        plt.title(self.display_name + "\n" + title)
        plt.xlabel("months (from " + self.date_data_cet_cest[0][5:7] + "/" + self.date_data_cet_cest[0][0:4] + ")")
        plt.ylabel("kWh")
        plt.plot(months, self.power_data)

        # Create directory 'figures' and 'PV' if they do not exist, and save figure
        os.makedirs("./figures/PV/", exist_ok=True)
        plt.savefig("./figures/PV/" + self.display_name + "_" + filename_tail + ".png")

    def is_noise(self, run, minute_res):
        """
        Returns whether or not the given PV run should be considered noise,
        by checking its length, does not contain any production, or it's steepness is too high

        :param run: (list) The run to check for noise
        :param minute_res: (int) The minutely resolution, used to check correct length
        :return: (boolean) True if the run is considered noise, else False
        """

        # Check if steepness is too high and if there or no production
        no_prod = True
        prev_value = run[0]
        for value in run:
            if value > (prev_value + 1):
                return True
            if value != prev_value:
                no_prod = False
            prev_value = value

        if no_prod:
            return True

        # Check if correct length according to minute resolution
        if len(run) != 1440 / minute_res:
            return True

        return False

