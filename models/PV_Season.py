"""

This module contains the class PV_Season which is used to represent photovoltaic (PV) units/systems
for one specific season and its various weather types

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

import matplotlib.pyplot as plt
import os

class PV_Season:
    """
    The class PV_Season represents a PV unit/system's production for one season
    and contains information about the weather types its 24 hour 'runs', as well as logic
    for e.g. plotting charts and getting limits to divide weather types
    """

    def __init__(self, name, display_name, season):
        self.name = name
        self.display_name = display_name
        self.season = season

        # All runs and start times for this PV_Season
        self.runs = []
        self.runs_start_times = []

        # Weather specific runs
        self.sunny_runs = []
        self.partially_cloudy_runs = []
        self.cloudy_runs = []
        self.rainy_runs = []

        # Start times for each run in the weather runs
        self.sunny_runs_start_times = []
        self.partially_cloudy_runs_start_times = []
        self.cloudy_runs_start_times = []
        self.rainy_runs_start_times = []

        # Set constant tilt (from horizontal) and orientation (from south) angles based on PV name from meta data
        self.tilt = 0
        self.orientation = 0
        if name == "DE_KN_residential1_pv":
            self.tilt = 30
            self.orientation = -5 # (175° in north-based azimuth)
        elif name == "DE_KN_residential3_pv":
            self.tilt = 5
            self.orientation = -160  # (20° in north-based azimuth)
        elif name == "DE_KN_residential4_pv":
            self.tilt = 28
            self.orientation = 28  # (208° in north-based azimuth)
        elif name == "DE_KN_residential6_pv":
            self.tilt = 40
            self.orientation = 30  # (210° in north-based azimuth)

    def accumulated_weather_limits(self, n_weather_types):
        """
        Returns a list with weather limit values for the runs' accumulated values that separate n weather types
        for this PV_Season, based on the min and max of all accumulated values.
        Returns None if this PV_Season has no runs

        :param n_weather_types: (int) the number of weather types to separate
        :return: (list) The list of weather limits
        """

        if len(self.runs) == 0:
            return None

        accumulated_values = []
        for run in self.runs:
            accumulated_values.append(sum(run))

        limits = [min(accumulated_values)]
        group_size = (max(accumulated_values) - min(accumulated_values)) / n_weather_types
        for i in range(n_weather_types-1):
            limits.append(limits[-1] + group_size)
        limits.append(max(accumulated_values))

        return limits

    def plot_weather_runs_accumulated(self, minute_res):
        """
        Plots and saves accumulated profiles for this PV_Season, color-separated by weather type

        :param minute_res: (int) The minutely resolution of profiles
        """

        # Return is there are no profiles in this PV_Season
        if (len(self.sunny_runs + self.partially_cloudy_runs + self.cloudy_runs + self.rainy_runs) == 0):
            return

        plt.clf()
        plt.figure(figsize=(14, 8.75))
        sunny_lines, partially_cloudy_lines, cloudy_lines, rainy_lines = None, None, None, None

        hours = [0]
        for i in range(len(self.sunny_runs[0]) - 1):
            hours.append(hours[i] + (minute_res / 60))

        for run in self.sunny_runs:
            sunny_lines, = plt.plot(hours, self.cumulative(run), color="red")
        for run in self.partially_cloudy_runs:
            partially_cloudy_lines, = plt.plot(hours, self.cumulative(run), color="orange")
        for run in self.cloudy_runs:
            cloudy_lines, = plt.plot(hours, self.cumulative(run), color="green")
        for run in self.rainy_runs:
            rainy_lines, = plt.plot(hours, self.cumulative(run), color="blue")

        plt.title(self.display_name + " (" + self.season + ")\nAccumulated normalized production profiles by weather type")
        plt.xlabel("hours")
        plt.ylabel("accumulated factors")
        plt.legend([sunny_lines, partially_cloudy_lines, cloudy_lines, rainy_lines],
                   ["Sunny", "Partially cloudy", "Cloudy", "Rainy"])

        # Create directory 'figures', 'PV', and 'weather' if they do not exist, and save figures
        os.makedirs("./figures/PV/weather/", exist_ok=True)
        plt.savefig("./figures/PV/weather/" + self.display_name + "_" + self.season + "_weather_cumulative_.png")

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