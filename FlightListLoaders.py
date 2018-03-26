from abc import ABCMeta, abstractmethod
import logging
import os
import sys
import pdb

import geopy.distance
from google.cloud import datastore

class FlightListLoader:
    __metaclass__ = ABCMeta

    ''' Loads a list of flight paths.

    Each flight path is a list of tuples (lat, long, time).
    '''
    @abstractmethod
    def load_flight_path_list(self, constraints): raise NotImplementedError

class DatastoreListLoader(FlightListLoader):
    def __init__(self):
        self.logger = logging.getLogger()
        logging.basicConfig(level=logging.INFO)

        self.datastore_client = datastore.Client()

    def load_flight_path_list(self, constraints):
        query = self.datastore_client.query(kind='FlightPoint')
        query.add_filter('Alt', '>', constraints['alt_lower_bound'])
        self.logger.info("query assembled")

        flights = {}

        self.logger.info("fetching query")
        query_iter = query.fetch()
        self.logger.info("query fetched")
        for entity in query_iter:
            flight_lat = entity['Lat']
            flight_long = entity['Long']
            time = entity['PosTime']
            if 'Call' in entity and 'To' in entity and entity['To'] == constraints['dest'] and int(entity['PosTime']) > constraints['earliest_time']:
                if entity['Call'] in flights:
                    if (flight_lat, flight_long) in [(x[0], x[1]) for x in flights[entity['Call']]]:
                        continue
                    flights[entity['Call']].append((flight_lat, flight_long, time, entity['Call']))
                    flights[entity['Call']].sort(key=lambda x: x[2])
                else:
                    flights[entity['Call']] = [(flight_lat, flight_long, time, entity['Call'])]
        
        filter_keys = []
        for call in flights:
            init_point = (flights[call][0][0], flights[call][0][1])
            init_dist = geopy.distance.distance(init_point, (constraints['dest_lat'], constraints['dest_long'])).km
            if (init_dist > constraints['init_dist_upper_bound'] and call not in filter_keys):
                filter_keys.append(call)
            for i in range(len(flights[call])):
                flightpoint = flights[call][i]
                point = (flightpoint[0], flightpoint[1])
                point_dist = geopy.distance.distance(point, (constraints['dest_lat'], constraints['dest_long'])).km
                if (point_dist < constraints['init_dist_lower_bound']) and i < len(flights[call]) - 1:
                    next_point = (flights[call][i + 1][0], flights[call][i + 1][1])
                    next_point_dist = geopy.distance.distance(next_point, (constraints['dest_lat'], constraints['dest_long'])).km
                    if (next_point_dist > point_dist and call not in filter_keys):
                        filter_keys.append(call)

        for key in filter_keys:
            flights.pop(key)
        return flights




