import json
import os
import sys

import folium
import geopandas as gpd
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import shapely


def generate_viewing_triangles(x1, y1, x2, y2, offset_dist):
    segment = shapely.geometry.LineString(coordinates=[(x1, y1), (x2, y2)])
    left = segment.parallel_offset(offset_dist, 'left')
    left_scaled = shapely.affinity.scale(left, 0.1/left.length, 0.1/left.length)
    right = segment.parallel_offset(offset_dist, 'right')
    right_scaled = shapely.affinity.scale(right, 0.1/left.length, 0.1/right.length)

    left_triangle = shapely.geometry.polygon.Polygon(list(left_scaled.coords) + [((x2+x1)/2,(y2+y1)/2)])
    right_triangle = shapely.geometry.polygon.Polygon(list(right_scaled.coords) + [((x2+x1)/2,(y2+y1)/2)])
    return [left_triangle, right_triangle]


def load_tracts():
    tracts = gpd.GeoDataFrame.from_file("/mnt/c/Users/Gautam/Downloads/Profile-County_Tract/Profile-County_Tract.gdb", layer='Tract_2010Census_DP1')
    tracts['popdensity'] = tracts['DP0010001']/tracts['ALAND10']
    return tracts


def get_triangle_tract_intersection(tracts, studyareas):
    print(studyareas)
    intersect_tracts = tracts[tracts.geometry.intersects(studyareas[0]) | tracts.geometry.intersects(studyareas[1])]
    left_pop = np.sum(intersect_tracts[intersect_tracts.geometry.intersects(studyareas[0])]['DP0010001'])
    right_pop = np.sum(intersect_tracts[intersect_tracts.geometry.intersects(studyareas[1])]['DP0010001'])
    print("Left pop: {}".format(left_pop))
    print("Right pop: {}".format(right_pop))
    return intersect_tracts


def plot_tracts_and_triangles(tracts, studyareas):
    tractplot = tracts.plot(column='popdensity')
    polys1 = gpd.GeoSeries(studyareas)
    df1 = gpd.GeoDataFrame({'geometry': polys1, 'df1':[0] * len(studyareas)})
    df1.plot(ax=tractplot, color='green', alpha=0.5)
    plt.show()


def run_dca_plot():
    tracts = load_tracts()
    studyareas = generate_viewing_triangles(-77.06, 38.89, -77.05, 38.88, 0.1)
    intersect_tracts = get_triangle_tract_intersection(tracts, studyareas)
    plot_tracts_and_triangles(intersect_tracts, studyareas)


#run_dca_plot()