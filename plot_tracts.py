import json
import logging
import os
import sys

import folium
import geopandas as gpd
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import shapely

logger = logging.getLogger()

def generate_viewing_triangles(x1, y1, x2, y2, offset_dist):
    logger.debug("generate_viewing_triangles")
    segment = shapely.geometry.LineString(coordinates=[(x1, y1), (x2, y2)])
    left = segment.parallel_offset(offset_dist, 'left')
    left_scaled = shapely.affinity.scale(left, 0.1/left.length, 0.1/left.length)
    right = segment.parallel_offset(offset_dist, 'right')
    right_scaled = shapely.affinity.scale(right, 0.1/left.length, 0.1/right.length)

    left_triangle = shapely.geometry.polygon.Polygon(list(left_scaled.coords) + [((x2+x1)/2,(y2+y1)/2)])
    right_triangle = shapely.geometry.polygon.Polygon(list(right_scaled.coords) + [((x2+x1)/2,(y2+y1)/2)])
    return [left_triangle, right_triangle]


def load_tracts():
    logger.debug("load_tracts")
    tracts = gpd.GeoDataFrame.from_file("/mnt/c/Users/Gautam/Downloads/Profile-County_Tract/Profile-County_Tract.gdb", layer='Tract_2010Census_DP1')
    tracts['popdensity'] = tracts['DP0010001']/tracts['ALAND10']
    tracts['popdensity'].fillna(0, inplace=True)
    return tracts


def get_triangle_tract_intersection(tracts, studyareas):
    logger.debug("get_triangle_tract_intersection")
    intersecting_tracts = tracts.geometry.intersects(studyareas[0])
    for area in studyareas[1:]:
        intersecting_tracts = intersecting_tracts | tracts.geometry.intersects(area)
    intersect_tracts = tracts[intersecting_tracts]
    return intersect_tracts


def get_intersect_left_right_values(tracts, studyareas, value_key):
    logger.debug("get_intersect_left_right_values")
    intersecting_tracts_left = get_triangle_tract_intersection(tracts, studyareas[::2])
    intersecting_tracts_right = get_triangle_tract_intersection(tracts, studyareas[1::2])
    left_value_sum = np.sum(intersecting_tracts_left[value_key])
    right_value_sum = np.sum(intersecting_tracts_right[value_key])
    return(left_value_sum, right_value_sum)


def plot_tracts_and_triangles(tracts, studyareas, color='green', ax=None):
    logger.debug("plot_tracts_and_triangles")
    polys1 = gpd.GeoSeries(studyareas)
    df1 = gpd.GeoDataFrame({'geometry': polys1, 'df1':[0] * len(studyareas)})
    if (ax is None):
        tractplot = tracts.plot(column='popdensity')
        return df1.plot(ax=tractplot, color=color, alpha=0.5)
    else:
        return df1.plot(ax=ax, color=color, alpha=0.5)


def plot_tracts_from_line_list(line_list):
    logger.debug("plot_tracts_from_line_list")
    studyareas = []
    for p1,p2 in zip(line_list, line_list[1:]):
        print([p1, p2])
        left_right = generate_viewing_triangles(p1[1], p1[0], p2[1], p2[0], 0.1)
        studyareas.extend(left_right)
    tracts = load_tracts()
    intersect_tracts = get_triangle_tract_intersection(tracts, studyareas)
    plot_tracts_and_triangles(intersect_tracts, studyareas)


def run_dca_plot():
    tracts = load_tracts()
    studyareas = generate_viewing_triangles(-77.06, 38.89, -77.05, 38.88, 0.1)
    intersect_tracts = get_triangle_tract_intersection(tracts, studyareas)
    plot_tracts_and_triangles(intersect_tracts, studyareas)


#run_dca_plot()