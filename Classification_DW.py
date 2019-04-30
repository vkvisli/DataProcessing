"""

This module performs manual and automatic classification into clusters for individual wash cycles
from dishwashers associated with the CoSSMic project. The manual classification is done with 2/3 of the cycles
(training) and automatic classification with 1/3 (verification). JSON files for each cluster is saved
and visual charts showing the clusters are displayed.

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

import csv
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.spatial import distance
from models.Appliance import Appliance
import ClusterParameters

# Data location and file names
data_location = "./data/edited/dw_runs/"
cluster_output_location = "./data/edited/dw_clusters/"
filenames = ["Dishwasher 1.csv","Dishwasher 2.csv","Dishwasher 3.csv",
             "Dishwasher 4.csv","Dishwasher 5.csv"]
appliance_list = []

# Set which time resolution the dishwasher data is read with
minute_res = 1

def mahalanobis(d, p):
    """
    Returns the Mahalanobis distance between a run (point p) and a set of runs (distribution d)

    :param d: (list) The list of runs from which to create the distribution
    :param p: (list) The list of values in the run that represent the point
    :return: (float) The Mahalanobis distance
    """

    # Get duration and energy consumption of each of the runs
    durations = []
    consumptions = []
    for run in d:
        durations.append(len(run))
        consumptions.append(max(run))

    # Create the distribution and point
    distribution = [durations, consumptions]
    point = [len(p), max(p)]

    # Calculate and return the Mahalanobis distance
    cov_matrix = np.cov(distribution)
    cov_matrix_inv = np.linalg.inv(cov_matrix)
    mean = np.mean(distribution, axis=1)
    return distance.mahalanobis(point, mean, cov_matrix_inv)

def plot_machine_separated_runs(runs, title=""):
    """
    Plots the given machine separated runs, with a unique color for each dishwasher

    :param runs: (list) A list containing the dishwasher runs
    :param title: (str) The title of the chart
    """
    plt.clf()
    plt.figure(figsize=(14, 8.75))

    colors = ['b','r','g','m','y','c']
    for i in range(len(appliance_list)):
        for run in runs[i]:
            plt.scatter(len(run), max(run), s=15, color=colors[i])

    plt.title(title)
    plt.xlabel("minutes")
    plt.ylabel("kWh")

    # Create directory 'figures', 'appliances', and 'clustering' if they do not exist, and save figures
    os.makedirs("./figures/appliances/clustering/", exist_ok=True)
    plt.savefig("./figures/appliances/clustering/DW1-5_clustering_machine_separated.png")

def plot_cluster_rectangles(runs, clusters, title=""):
    """
    Plots the given runs and parameter rectangles for the given clusters

    :param runs: (list) A list containing the dishwasher runs
    :param clusters: (list) A list of Cluster objects
    :param title: (str) The title of the chart
    """
    plt.clf()
    plt.figure(figsize=(14, 8.75))

    for run in runs:
        plt.plot(len(run), max(run), ".", color="blue")
    for c in clusters:
        plt.plot([c.min_duration, c.min_duration], [c.min_consumption, c.max_consumption],
                 color="black", linestyle="dashed", alpha=0.5)
        plt.plot([c.max_duration, c.max_duration], [c.min_consumption, c.max_consumption],
                 color="black", linestyle="dashed", alpha=0.5)
        plt.plot([c.min_duration, c.max_duration], [c.min_consumption, c.min_consumption],
                 color="black", linestyle="dashed", alpha=0.5)
        plt.plot([c.min_duration, c.max_duration], [c.max_consumption, c.max_consumption],
                 color="black", linestyle="dashed", alpha=0.5)

    plt.title(title)
    plt.xlabel("minutes")
    plt.ylabel("kWh")

    # Create directory 'figures', 'appliances', and 'clustering' if they do not exist, and save figures
    os.makedirs("./figures/appliances/clustering/", exist_ok=True)
    plt.savefig("./figures/appliances/clustering/DW1-5_clustering_rectangles.png")

def plot_classification_results(runs, clusters=None, not_classified_runs=None, title=""):
    """
    Plots the given runs and clusters. Classified runs get green colors and not classified runs get red

    :param runs: (list) A list containing the dishwasher runs
    :param clusters: (list) A list of Cluster objects
    :param not_classified_runs: (list) A list of the dishwasher runs that have not been successfully classified
    :param title: (str) The title of the chart
    """
    plt.clf()
    plt.figure(figsize=(14, 8.75))

    blue_dots, green_dots, red_dots, black_dashes = None, None, None, None

    for run in runs:
        blue_dots, = plt.plot(len(run), max(run), ".", color="blue")

    if clusters:
        for c in clusters:
            # Plot cluster rectangles
            black_dashes, = plt.plot([c.min_duration, c.min_duration], [c.min_consumption, c.max_consumption],
                     color="black", linestyle="dashed", alpha=0.5)
            plt.plot([c.max_duration, c.max_duration], [c.min_consumption, c.max_consumption],
                     color="black", linestyle="dashed", alpha=0.5)
            plt.plot([c.min_duration, c.max_duration], [c.min_consumption, c.min_consumption],
                     color="black", linestyle="dashed", alpha=0.5)
            plt.plot([c.min_duration, c.max_duration], [c.max_consumption, c.max_consumption],
                     color="black", linestyle="dashed", alpha=0.5)

            # Plot classified runs
            for run in c.classified_runs:
                green_dots, = plt.plot(len(run), max(run), ".", color="green")

    # Plot runs that could not be classified
    if not_classified_runs:
        for run in not_classified_runs:
            red_dots, = plt.plot(len(run), max(run), ".", color="red")

    plt.title(title)
    plt.xlabel("minutes")
    plt.ylabel("kWh")
    if blue_dots and green_dots and red_dots and black_dashes:
        plt.legend([blue_dots, green_dots, red_dots, black_dashes],
                   ["classified training data", "successfully classified verification data", "not classified",
                    "manual cluster parameters for training data"])

    # Create directory 'figures', 'appliances', and 'clustering' if they do not exist, and save figures
    os.makedirs("./figures/appliances/clustering/", exist_ok=True)
    plt.savefig("./figures/appliances/clustering/DW1-5_clustering_classification_results.png")

def plot_final_clusters(clusters, not_classified_runs, title):
    """
    Plots the given clusters, each with a unique color

    :param clusters: (list) A list of Cluster objects
    :param not_classified_runs: (list) A list of the dishwasher runs that have not been successfully classified
    :param title: (str) The title of the chart
    """
    plt.clf()
    plt.figure(figsize=(14, 8.75))

    colors = ['b','g','m','c','k','orange','lime','yellow','tan','violet',
              'brown','indigo','navy','grey','dodgerblue','teal','olive']
    # Plot runs that belong to a class
    for i in range(len(clusters)):
        # Plot training runs
        for run in clusters[i].training_runs:
            plt.plot(len(run), max(run), ".", color=colors[i])
        # Plot classified runs
        for run in clusters[i].classified_runs:
            plt.plot(len(run), max(run), ".", color=colors[i])

    # Plot runs that could not be classified
    red_cross = None
    for run in not_classified_runs:
        red_cross, = plt.plot(len(run), max(run), "x", color="red")

    # Show plot
    plt.title(title)
    plt.xlabel("minutes")
    plt.ylabel("kWh")
    plt.legend([red_cross], ["Not classified"])

    # Create directory 'figures', 'appliances', and 'clustering' if they do not exist, and save figures
    os.makedirs("./figures/appliances/clustering/", exist_ok=True)
    plt.savefig("./figures/appliances/clustering/DW1-5_clustering_final_clusters.png")

def save_clusters_json(clusters, location):
    """
    Saves the runs in each cluster in individual json files

    :param clusters: (list) A list of Cluster objects
    :param location: (str) The location to save files
    """

    # Create directory to store the files, if it does not exist
    os.makedirs(location, exist_ok=True)

    # Create the json files
    cluster_nr = 1
    for c in clusters:
        filename = "DW cluster " + str(cluster_nr) + " (" + str(c.min_duration) + "-" + str(c.max_duration) + " min" \
                   + ", " + str(c.min_consumption) + "-" + str(c.max_consumption) + " kWh).json"
        with open(location + filename, "w") as file:
            file.write("{\n    \"minuteRes\": " + str(minute_res) + ",\n")
            file.write("    \"data\": [\n")

            # Training runs
            for i in range(len(c.training_runs)):
                file.write("        " + str(c.training_runs[i]) + ",\n")

            # Classified testing runs
            for i in range(len(c.classified_runs)):
                if i < len(c.classified_runs)-1:
                    file.write("        " + str(c.classified_runs[i]) + ",\n")
                else:
                    file.write("        " + str(c.classified_runs[i]) + "\n")

            file.write("    ]\n")
            file.write("}")
        cluster_nr += 1

# For each dishwasher, read single run data (the result from time-series splitting) and create an Appliance object
for filename in filenames:
    with open(data_location + filename, "r") as data:
        dataReader = csv.reader(data)
        appliance = Appliance("", next(dataReader, None)[0])

        for row in dataReader:
            single_run = []
            for i in range(len(row)):
                single_run.append(float(row[i]))
            appliance.single_runs.append(single_run)

        appliance_list.append(appliance)

# Retrieve all dishwasher runs
all_runs = []
all_runs_machine_separated = []
for a in appliance_list:
    all_runs += a.single_runs
    all_runs_machine_separated.append(a.single_runs)

# Select 2/3 of the runs for manual classification (training), and 1/3 as points for automatic classification (verification)
training = all_runs.copy()
del training[::3]
testing = all_runs[::3]

# Retrieve minimum and maximum limits for duration and consumption for each cluster of the training runs
clusters = ClusterParameters.DW_clusters()

# For each training run, find its corresponding cluster. In case a run is within the parameters of several clusters,
# the first of them is chosen. If a run is not within any clusters, it is registered as not classified.
not_classified_runs = []
for run in training:
    assigned_clusters = []
    for c in clusters:
        if (c.min_duration <= len(run) <= c.max_duration) and (c.min_consumption <= max(run) <= c.max_consumption):
            assigned_clusters.append(c)
    if len(assigned_clusters) == 0:
        not_classified_runs.append(run)
    else:
        assigned_clusters[0].training_runs.append(run)

# Find the Mahalanobis distance (MD) threshold for each cluster (the highest MD of the runs)
for c in clusters:
    mahalanobis_distances = []
    for run in c.training_runs:
        mahalanobis_distances.append(mahalanobis(c.training_runs, run))
    c.mahalanobis_threshold = max(mahalanobis_distances)

# Try to classify testing runs by checking if they are within a cluster's Mahalanobis threshold
for run in testing:
    assigned_clusters = []
    for c in clusters:
        m_distance = mahalanobis(c.training_runs, run)
        if m_distance < c.mahalanobis_threshold:
            assigned_clusters.append({"cluster": c, "m_distance": m_distance})

    # Add the run to the assigned cluster
    if len(assigned_clusters) == 1:
        assigned_clusters[0]["cluster"].classified_runs.append(run)
    # If the run is within the threshold of multiple clusters, add it to the closest one
    elif len(assigned_clusters) > 1:
        smallest_dist = min([x["m_distance"] for x in assigned_clusters])
        closest_cluster = next((x for x in assigned_clusters if x["m_distance"] == smallest_dist))["cluster"]
        closest_cluster.classified_runs.append(run)
    else:
        not_classified_runs.append(run)

# Save one json file with single runs for each cluster
save_clusters_json(clusters, cluster_output_location)

# Plot and show classification figures
plot_machine_separated_runs(all_runs_machine_separated, "Dishwashers 1-5\nDuration and consumption of runs")
plot_cluster_rectangles(training, clusters, title="Dishwashers 1-5\nClustering of training runs")
plot_classification_results(training, clusters, not_classified_runs, "Dishwashers 1-5\nClassification of test runs")
plot_final_clusters(clusters, not_classified_runs, "Clusters for dishwasher runs")