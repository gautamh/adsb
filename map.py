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

# Instantiates a client
datastore_client = datastore.Client()

#m = folium.Map(location=[47.449474, -122.309912])

query = datastore_client.query(kind='FlightPoint')
#query.add_filter('To', '=', "KSEA Seattle Tacoma, United States")
query.add_filter('Alt', '>', 50)
#query.add_filter('Alt', '<', 2500)
logger.info("query assembled")

flights = {}

logger.info("fetching query")
query_iter = query.fetch()
logger.info("query fetched")
for entity in query_iter:
    flight_lat = entity['Lat']
    flight_long = entity['Long']
    time = entity['PosTime']
    if 'Call' in entity and 'To' in entity and entity['To'] == 'KSEA Seattle Tacoma, United States' and int(entity['PosTime']) > 1520097257490 :
        if entity['Call'] in flights:
            if (flight_lat, flight_long) in [(x[0], x[1]) for x in flights[entity['Call']]]:
                continue
            flights[entity['Call']].append((flight_lat, flight_long, time, entity['Call']))
            flights[entity['Call']].sort(key=lambda x: x[2])
        else:
            flights[entity['Call']] = [(flight_lat, flight_long, time, entity['Call'])]
        #label = entity['Call'] + " " + str(entity['Alt'])
    #else:
        #str(entity['Alt'])
    #folium.Marker([flight_lat, flight_long], popup=label).add_to(m)

logger.info("finished iterating")
select_flight = []
flight_iter = iter(flights.values())
while len(select_flight) <= 4:
    select_flight = next(flight_iter)
select_flight.sort(key=lambda x: x[2])
print(select_flight)

#studyareas = []
#for v,w in zip(select_flight, select_flight[1:]):
#    left_right = generate_viewing_triangles(p1[1], p1[0], p2[1], p2[0], 0.1)
#    studyareas.extend(left_right)
#leftpop, rightpop = get_intersect_left_right_values()

logger.info("plotting tracts from line list")
studyareas = []
for p1,p2 in zip(select_flight, select_flight[1:]):
    print([p1, p2])
    left_right = plot_tracts.generate_viewing_triangles(p1[1], p1[0], p2[1], p2[0], 0.1)
    studyareas.extend(left_right)
tracts = plot_tracts.load_tracts()
intersect_tracts = plot_tracts.get_triangle_tract_intersection(tracts, studyareas)
left_pop, right_pop = plot_tracts.get_intersect_left_right_values(tracts, studyareas, 'DP0010001')
ax1 = plot_tracts.plot_tracts_and_triangles(intersect_tracts, studyareas[::2])
plot_tracts.plot_tracts_and_triangles(intersect_tracts, studyareas[1::2], 'red', ax1)
plt.show()
print("Left pop: {}".format(left_pop))
print("Right pop: {}".format(right_pop))

#m.save("index.html")
#print(flights)