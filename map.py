import json
import logging
import os
import pdb
import sys

import folium
import geopandas as gpd
from google.cloud import datastore
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import shapely

import plot_tracts

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

ALT_LOWER_BOUND = 50
ALT_UPPER_BOUND = 2500
DEST = 'KSEA Seattle Tacoma, United States'
EARLIEST_TIME = 1520607257490#1520397257490
MIN_PATH_LENGTH = 5

# Instantiates a client
datastore_client = datastore.Client()

m = folium.Map(location=[47.449474, -122.309912])

query = datastore_client.query(kind='FlightPoint')
#query.add_filter('To', '=', DEST)
query.add_filter('Alt', '>', ALT_LOWER_BOUND)
#query.add_filter('Alt', '<', ALT_UPPER_BOUND)
logger.info("query assembled")

flights = {}

logger.info("fetching query")
query_iter = query.fetch()
logger.info("query fetched")
for entity in query_iter:
    flight_lat = entity['Lat']
    flight_long = entity['Long']
    time = entity['PosTime']
    if 'Call' in entity and 'To' in entity and entity['To'] == DEST and int(entity['PosTime']) > EARLIEST_TIME:
        if entity['Call'] in flights:
            if (flight_lat, flight_long) in [(x[0], x[1]) for x in flights[entity['Call']]]:
                continue
            flights[entity['Call']].append((flight_lat, flight_long, time, entity['Call']))
            flights[entity['Call']].sort(key=lambda x: x[2])
        else:
            flights[entity['Call']] = [(flight_lat, flight_long, time, entity['Call'])]

logger.info("finished iterating")
logger.info("Number of flights >= MIN_PATH_LENGTH: {}".format(
    len([x for x in flights.values() if len(x) >= MIN_PATH_LENGTH])))

# Find a flight path longer than MIN_PATH_LENGTH
select_flight = []
flight_iter = iter(flights.values())
while len(select_flight) <= MIN_PATH_LENGTH:
    select_flight = next(flight_iter)
    if len(select_flight) < 2:
        continue
    for i in range(1, len(select_flight)):
        # Break up paths that are multiple flights under the same number
        t1 = select_flight[i - 1][2]
        t2 = select_flight[i][2]
        if (t2 - t1 > 2000000):
            select_flight = select_flight[:i]
            if len(select_flight) <= MIN_PATH_LENGTH:
                select_flight = select_flight[i:]
            else:
                break
select_flight.sort(key=lambda x: x[2])
print(select_flight)

logger.info("plotting tracts from line list")
studyareas = []
for p1,p2 in zip(select_flight, select_flight[1:]):
    print([p1, p2])
    left_right = plot_tracts.generate_viewing_triangles(p1[1], p1[0], p2[1], p2[0], 0.1)
    studyareas.extend(left_right)
tracts = plot_tracts.load_tracts()
intersect_tracts = plot_tracts.get_triangle_tract_intersection(tracts, studyareas)
#print(intersect_tracts)
left_pop, right_pop = plot_tracts.get_intersect_left_right_values(tracts, studyareas, 'DP0010001')
ax1 = plot_tracts.plot_tracts_and_triangles(intersect_tracts, studyareas[::2])
plot_tracts.plot_tracts_and_triangles(intersect_tracts, studyareas[1::2], 'red', ax1)
plt.show()
print("Left pop: {}".format(left_pop))
print("Right pop: {}".format(right_pop))

m.choropleth(geo_data=intersect_tracts.to_json(), data=intersect_tracts, columns = ['GEOID10', 'DP0010001'], key_on = 'feature.properties.{}'.format('GEOID10'), fill_color = 'YlOrRd', fill_opacity = 0.6, line_opacity = 0.2)

m.save("index.html")