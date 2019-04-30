"""

This module contains the information about parameter values for clusters of appliance runs. This information
is retrieved with the two functions WM_clusters and DW_clusters which return a list of Cluster objects

Copyright 2019 Vebjørn Kvisli
License: GNU Lesser General Public License v3.0

"""

from models.Cluster import Cluster

def WM_clusters():
    """
    Returns a list of Cluster objects with manually set cluster parameters,
    specifically for washing machines from the CoSSMic project
    """
    return [Cluster(158, 185, 0.5, 0.82),
            Cluster(86, 110, 0.40, 0.85),
            Cluster(110, 130, 0.40, 0.82),
            Cluster(10, 40, 0.00, 0.12),
            Cluster(130, 152, 0.40, 0.82),
            Cluster(111, 135, 0.82, 1.55),
            Cluster(40, 71, 0.16, 0.38),
            Cluster(91, 130, 1.55, 2.31),
            Cluster(40, 70, 0.04, 0.16),
            Cluster(46, 111, 0.85, 1.55),
            Cluster(71, 95, 0.10, 0.40),
            Cluster(68, 86, 0.40, 0.85),
            Cluster(10, 40, 0.12, 0.46),
            Cluster(30, 68, 0.38, 0.77),
            Cluster(95, 130, 0.12, 0.40),
            Cluster(135, 185, 0.82, 1.41),
            Cluster(200, 255, 0.39, 1.24)]

def DW_clusters():
    """
    Returns a list of Cluster objects with manually set cluster parameters,
    specifically for dishwashers from the CoSSMic project
    """
    return [Cluster(92, 115, 0.67, 1.17),
            Cluster(117, 135, 0.80, 1.20),
            Cluster(73, 103, 1.10, 1.65),
            Cluster(51, 66, 0.99, 1.32),
            Cluster(66, 90, 0.62, 1.02),
            Cluster(55, 68, 0.53, 0.98),
            Cluster(47, 80, 0.24, 0.48),
            Cluster(28, 48, 0.35, 0.82)]