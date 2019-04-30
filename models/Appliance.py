"""

This module contains the class Appliance which is used to represent household appliances and their data

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

import matplotlib.pyplot as plt
import os


class Appliance:
    """
    The class Appliance represents a household appliance such as a washing machine or dishwasher.
    It contains relevant information about the appliance, as well as logic to e.g. split its time-series data
    and plot its data as charts.
    """

    def __init__(self, name, display_name):
        self.name = name
        self.display_name = display_name
        self.column_nr = 0
        self.time_data = []
        self.power_data = []
        self.date_data = []
        self.single_runs = []

    def split_power_data(self, max_pause_allowed, min_duration, max_consumption):
        """
        Splits the appliance time-series data into individual runs, based on a few
        threshold parameters. The parameters are the number of steps in the data array, which means
        that the amount of time will depend on the time resolution the data was initiated with

        :param max_pause_allowed: (int) The length of 'off' periods allowed within runs
        :param min_duration: (int) The minimum duration a run must have
        :param max_consumption: (int) The maximum consumption (kWh) a run can have
        """

        single_runs = []
        current_run = []
        off_period_length = 0
        climbing = False

        # Iterate all data points
        for i in range(len(self.power_data) - 1):
            if self.power_data[i] == self.power_data[i + 1]:
                off_period_length += 1
                climbing = False
            else:
                if not climbing and off_period_length > max_pause_allowed:
                    # Don't include runs shorter than minimum duration or with higher consumption than max
                    if len(current_run) > min_duration and (current_run[-1] - current_run[0]) < max_consumption:
                        single_runs.append(current_run)
                    current_run = []
                current_run.append(self.power_data[i])
                off_period_length = 0
                climbing = True

        self.single_runs = single_runs

    def shrink_runs(self):
        """ Shrinks/scales the values of each appliance run, so that each run start at 0 kWh """
        for run in self.single_runs:
            if run:
                pos_0 = run[0]
                for i in range(len(run)):
                    run[i] = run[i] - pos_0

    def plot_single_runs(self):
        """ Plots all individual runs of this appliance """
        plt.clf()
        plt.title(self.display_name)
        plt.xlabel("minutes")
        plt.ylabel("kWh")
        for i in range(len(self.single_runs)):
            plt.plot(self.single_runs[i])

        # Create directory 'figures' and 'appliances' if they do not exist, and save figures
        os.makedirs("./figures/appliances/", exist_ok=True)
        plt.savefig("./figures/appliances/" + self.display_name + "_profiles.png")

    def plot_time_series(self):
        """ Plots the cumulative time-series data for this appliance """
        plt.clf()
        plt.title(self.display_name + "\nCumulative Energy consumption")
        plt.xlabel("minutes")
        plt.ylabel("kWh")
        plt.plot(self.time_data, self.power_data)

        # Create directory 'figures' and 'appliances' if they do not exist, and save figures
        os.makedirs("./figures/appliances/", exist_ok=True)
        plt.savefig("./figures/appliances/" + self.display_name + "_time_series.png")
