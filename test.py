import urllib.request, json 

url = "https://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat=47.449474&lng=-122.309912&fDstL=0&fDstU=50"
req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

with urllib.request.urlopen(req) as page:
    data = json.loads(page.read().decode())
    print(data)