from abc import ABCMeta, abstractmethod
import logging
import os
import sys

from google.cloud import datastore

class FlightListLoader:
    __metaclass__ = ABCMeta

    ''' Loads a list of flight paths.

    Each flight path is a list of tuples (lat, long, time).
    '''
    @abstractmethod
    def load_flight_path_list(self): raise NotImplementedError

class DatastoreListLoader(FlightListLoader):
    def __init__(selfs):
        self.logger = logging.getLogger()
        logging.basicConfig(level=logging.INFO)

        self.datastore_client = datastore.Client()

    def load_flight_path_list(self):
        query = datastore_client.query(kind='FlightPoint')
        query.add_filter('Alt', '>', ALT_LOWER_BOUND)
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
        return flights




