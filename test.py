import urllib.request, json 
import time
from google.cloud import datastore

# KSEA lat and long
airport_lat = 47.449474
airport_long = -122.309912

# Radius from airport (in mi?) to track flights
radius_from_airport = 15

url = "https://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat={}&lng={}&fDstL=0&fDstU={}".format(airport_lat, airport_long, radius_from_airport)
req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

samples = 30
delay = 30

# Instantiates a client
datastore_client = datastore.Client()

# The kind for the new entity
kind = 'FlightPoint'

for i in range(samples):
    data = []

    with urllib.request.urlopen(req) as page:
        data = json.loads(page.read().decode())

    print(len(data['acList']))
    for flight in data['acList']:
        # The name/ID for the new entity
        name = str(flight['Id']) + '-' + str(flight['PosTime'])
        # The Cloud Datastore key for the new entity
        flight_point_key = datastore_client.key(kind, name)
        # Create the entity
        flight_point = datastore.Entity(key=flight_point_key)
        for k,v in flight.items():
            flight_point[k] = v
        
        datastore_client.put(flight_point)

    #query = datastore_client.query(kind='FlightPoint')
    #query.add_filter('To', '=', "KSEA Seattle Tacoma, United States")

    #query_iter = query.fetch()
    #for entity in query_iter:
        #pass
        #print(entity)
    time.sleep(delay)