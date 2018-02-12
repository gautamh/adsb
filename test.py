import urllib.request, json 
from google.cloud import datastore

url = "https://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat=47.449474&lng=-122.309912&fDstL=0&fDstU=5"
req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

# Instantiates a client
datastore_client = datastore.Client()

# The kind for the new entity
kind = 'FlightPoint'

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

query = datastore_client.query(kind='FlightPoint')
query.add_filter('To', '=', "KSEA Seattle Tacoma, United States")

query_iter = query.fetch()
for entity in query_iter:
    print(entity)