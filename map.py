import folium
from google.cloud import datastore

# Instantiates a client
datastore_client = datastore.Client()

m = folium.Map(location=[47.449474, -122.309912])

query = datastore_client.query(kind='FlightPoint')
#query.add_filter('To', '=', "KSEA Seattle Tacoma, United States")
#query.add_filter('Alt', '>', 50)
#query.add_filter('Alt', '<', 2500)

query_iter = query.fetch()
for entity in query_iter:
    flight_lat = entity['Lat']
    flight_long = entity['Long']
    if 'Call' in entity:
        label = entity['Call'] + " " + str(entity['Alt'])
    else:
        str(entity['Alt'])
    folium.Marker([flight_lat, flight_long], popup=label).add_to(m)

m.save("index.html")