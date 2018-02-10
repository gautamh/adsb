import urllib.request, json 

url = "https://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat=47.449474&lng=-122.309912&fDstL=0&fDstU=50"
with urllib.request.urlopen(url) as page:
    data = json.loads(page.read().decode())
    print(data)