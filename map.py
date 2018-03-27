import json
import logging
import os
import pdb
import sys

from branca.colormap import linear
import folium
import geopandas as gpd
from google.cloud import datastore
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import shapely

import plot_tracts

from FlightListLoaders import DatastoreListLoader

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

ALT_LOWER_BOUND = 50
ALT_UPPER_BOUND = 2500

#DEST= 'KDCA Ronald Reagan Washington National, United States'
#DEST_LAT = 38.85120
#DEST_LONG = -77.03774

#DEST = 'KSEA Seattle Tacoma, United States'
#DEST_LAT = 47.449474
#DEST_LONG = -122.309912

DEST = "KORD Chicago O'Hare, United States"
DEST_LAT = 41.973782
DEST_LONG = -87.907403

EARLIEST_TIME = 1520607257490
MIN_PATH_LENGTH = 5

# Instantiates a client
datastore_client = datastore.Client()

m = folium.Map(location=[DEST_LAT, DEST_LONG])

constraints = {
    'alt_lower_bound': ALT_LOWER_BOUND,
    'alt_upper_bound': ALT_UPPER_BOUND,
    'dest': DEST,
    'earliest_time': EARLIEST_TIME,
    'dest_lat': DEST_LAT,
    'dest_long': DEST_LONG,
    'init_dist_lower_bound': 2.6,
    'init_dist_upper_bound': 100.0
}

flights = {}

loader = DatastoreListLoader()
flights = loader.load_flight_path_list(constraints)

logger.info("finished iterating")
logger.info("Number of flights >= MIN_PATH_LENGTH: {}".format(
    len([x for x in flights.values() if len(x) >= MIN_PATH_LENGTH])))

# Find flights with path longer than MIN_PATH_LENGTH
valid_flights = []

select_flight = []
flight_iter = iter(flights.values())
for select_flight in flight_iter:
    if len(select_flight) < 2:
        continue
    for i in range(1, len(select_flight)):
        # Break up paths that are multiple flights under the same number
        t1 = select_flight[i - 1][2]
        t2 = select_flight[i][2]
        if (t2 - t1 > 2000000):
            new_select_flight = select_flight[:i]
            if len(new_select_flight) <= MIN_PATH_LENGTH:
                select_flight = select_flight[i:]
            else:
                select_flight = new_select_flight
            break
    if len(select_flight) >= MIN_PATH_LENGTH:
        select_flight.sort(key=lambda x: x[2])
        valid_flights.append(select_flight)

logger.info("loading tracts")
tracts = plot_tracts.load_tracts()
tracts = tracts[(~(tracts.INTPTLAT10.astype('float') > (DEST_LAT + 0.5))) & (~(tracts.INTPTLAT10.astype('float') < (DEST_LAT - 0.5))) & (~(tracts.INTPTLON10.astype('float') > (DEST_LONG + 1))) & (~(tracts.INTPTLON10.astype('float') < (DEST_LONG - 1)))]

tracts['left_view'] = 0
tracts['right_view'] = 0

left_tracts = gpd.GeoDataFrame(columns=tracts.columns, crs={'init': 'epsg:4326'})
right_tracts = gpd.GeoDataFrame(columns=tracts.columns, crs={'init': 'epsg:4326'})

left_study_areas = []
right_study_areas = []

logger.info("iterating over valid flights")
for valid_flight in valid_flights:
    studyareas = []
    for p1,p2 in zip(valid_flight, valid_flight[1:]):
        print([p1, p2])
        left_right = plot_tracts.generate_viewing_triangles(p1[1], p1[0], p2[1], p2[0], 0.1)
        studyareas.extend(left_right)
    intersect_tracts = plot_tracts.get_triangle_tract_intersection(tracts, studyareas)
    intersect_tracts_left = plot_tracts.get_triangle_tract_intersection(tracts, studyareas[::2])
    intersect_tracts_right = plot_tracts.get_triangle_tract_intersection(tracts, studyareas[1::2])
    left_study_areas.extend(studyareas[::2])
    right_study_areas.extend(studyareas[1::2])
    for index, left_tract in intersect_tracts_left.iterrows():
        if left_tract['GEOID10'] in left_tracts['GEOID10'].values:
            left_tracts.loc[left_tracts['GEOID10'] == left_tract['GEOID10'],'left_view'] += 1 # https://www.dataquest.io/blog/settingwithcopywarning/
        else:
            left_tract['left_view'] = 1
            left_tracts = left_tracts.append(left_tract)
    for index, right_tract in intersect_tracts_right.iterrows():
        if right_tract['GEOID10'] in right_tracts['GEOID10'].values:
            right_tracts.loc[right_tracts['GEOID10'] == right_tract['GEOID10'],'right_view'] += 1 # https://www.dataquest.io/blog/settingwithcopywarning/
        else:
            right_tract['right_view'] = 1
            right_tracts = right_tracts.append(right_tract)

left_view_density = left_tracts['popdensity'] * left_tracts['left_view']
colormap1 = linear.YlGn.scale(
    left_view_density.min(),
    left_view_density.max())
colormap1.caption = 'Left View'
colormap1.add_to(m)

right_view_density = right_tracts['popdensity'] * right_tracts['right_view']
colormap2 = linear.BuPu.scale(
    right_view_density.min(),
    right_view_density.max())
colormap2.caption = 'Right View'
colormap2.add_to(m)

folium.GeoJson(
    left_tracts,
    name='Left View',
    style_function=lambda feature: {
        'fillColor': colormap1(feature['properties']['popdensity'] * feature['properties']['left_view']),
        'color': 'black',
        'fillOpacity': (feature['properties']['popdensity'] * feature['properties']['left_view'])/left_view_density.max(),
        'weight': 1
    }
).add_to(m)

folium.GeoJson(
    right_tracts,
    name='Right View',
    style_function=lambda feature: {
        'fillColor': colormap2(feature['properties']['popdensity'] * feature['properties']['right_view']),
        'color': 'black',
        'fillOpacity': (feature['properties']['popdensity'] * feature['properties']['right_view'])/right_view_density.max(),
        'weight': 1
    }
).add_to(m)

for valid_flight in valid_flights:
    #for point in valid_flight:
        #folium.Marker([point[0], point[1]], popup="{} {}".format(point[3], point[2])).add_to(m)
    folium.PolyLine([(x[0], x[1]) for x in valid_flight]).add_to(m)

folium.LayerControl().add_to(m)
m.save("index.html")

ax1 = plot_tracts.plot_tracts_and_triangles(left_tracts, left_study_areas)
plot_tracts.plot_tracts_and_triangles(right_tracts, right_study_areas, 'red', ax1)
#plt.show()

print("Left popdensity*views: {}".format(((left_tracts['popdensity'] ** 2) * left_tracts['left_view']).sum()))
print("Right popdensity*views: {}".format(((right_tracts['popdensity'] ** 2) * right_tracts['right_view']).sum()))

logger.info("done")