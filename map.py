import json
import os
import sys

import folium
import geopandas as gpd
from google.cloud import datastore
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import shapely

import plot_tracts

# Instantiates a client
datastore_client = datastore.Client()

#m = folium.Map(location=[47.449474, -122.309912])

query = datastore_client.query(kind='FlightPoint')
#query.add_filter('To', '=', "KSEA Seattle Tacoma, United States")
query.add_filter('Alt', '>', 50)
#query.add_filter('Alt', '<', 2500)
print("query assembled")

flights = {}

print("fetching query")
query_iter = query.fetch()
print("query fetched")
for entity in query_iter:
    flight_lat = entity['Lat']
    flight_long = entity['Long']
    time = entity['PosTime']
    if 'Call' in entity:
        if entity['Call'] in flights and not (flights[entity['Call']][-1][0] == flight_lat and flights[entity['Call']][-1][1] == flight_long):
            flights[entity['Call']].append((flight_lat, flight_long, time, entity['Call']))
        else:
            flights[entity['Call']] = [(flight_lat, flight_long, time, entity['Call'])]
        #label = entity['Call'] + " " + str(entity['Alt'])
        
    #else:
        #str(entity['Alt'])
    #folium.Marker([flight_lat, flight_long], popup=label).add_to(m)
print("finished iterating")
select_flight = []
while len(select_flight) <= 2:
    select_flight = next(iter(flights.values()))
select_flight.sort(key=lambda x: x[2])
print(select_flight)
#for v,w in zip(select_flight, select_flight[1:]):
   # print([v, w])

plot_tracts.plot_tracts_from_line_list(select_flight)

#m.save("index.html")
#print(flights)