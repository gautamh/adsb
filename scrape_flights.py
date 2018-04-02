import json 
import logging
import os
import time
import urllib.request

from google.cloud import datastore

# Set up logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    filename=os.path.expanduser('~/adsb_logs/{}_adsb_log'.format(str(round(time.time())))))

# Instantiates a client
datastore_client = datastore.Client()

# The kind for the new entity
KIND = 'FlightPoint'

# KSEA lat and long
KSEA_lat = 47.449474
KSEA_long = -122.309912

KDCA_lat = 38.85120
KDCA_long = -77.03774

KORD_lat = 41.973782
KORD_long = -87.907403

KJFK_lat = 40.648870
KJFK_long = -73.790043

airport_coords = [
    #(KSEA_lat, KSEA_long)
    #(KDCA_lat, KDCA_long)
    #(KORD_lat, KORD_long)
    (KJFK_lat, KJFK_long)
]


# Radius from airport (in mi?) to track flights
radius_from_airport = 20

samples = 30
delay = 45

URL_TEMPLATE = 'https://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat={}&lng={}&fDstL=0&fDstU={}'
USER_AGENT_STR = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

VALID_TO = [
    'KDCA Ronald Reagan Washington National, United States',
    'KSEA Seattle Tacoma, United States',
    "KORD Chicago O'Hare, United States",
    'KJFK John F Kennedy, New York, United States'
]

''' Determine whether a flight point scraped from the API should be saved to datastore. '''
def should_record_flight(flightinfo, valid_to=None):
    if (valid_to is not None and ('To' not in flightinfo or flightinfo['To'] not in valid_to)):
        return False

    return True

def sample_flight_points(num_samples, delay, radius, lat, long, client):
    url = URL_TEMPLATE.format(lat, long, radius)
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': USER_AGENT_STR
        }
    )

    for i in range(samples):
        data = []

        with urllib.request.urlopen(req) as page:
            data = json.loads(page.read().decode())

        print(len(data['acList']))
        for flight in data['acList']:
            if not should_record_flight(flight, VALID_TO):
                continue
            # The name/ID for the new entity
            name = str(flight['Id']) + '-' + str(flight['PosTime'])
            # The Cloud Datastore key for the new entity
            flight_point_key = datastore_client.key(KIND, name)
            # Create the entity
            flight_point = datastore.Entity(key=flight_point_key)
            for k,v in flight.items():
                flight_point[k] = v
            
            logger.info(flight_point)
            client.put(flight_point)

        time.sleep(delay)

for airport_lat, airport_long in airport_coords:
    sample_flight_points(samples, delay, radius_from_airport, airport_lat, airport_long, datastore_client)