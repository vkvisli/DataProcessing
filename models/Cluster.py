"""

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

class Cluster:
    """
    This class represents a cluster of single runs/cycles from an appliance and holds
    information about its parameter values, training runs, classified runs, and Mahalanobis threshold
    """
    def __init__(self, min_duration, max_duration, min_consumption, max_consumption):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.min_consumption = min_consumption
        self.max_consumption = max_consumption

        self.training_runs = []
        self.classified_runs = []
        self.mahalanobis_threshold = 0
