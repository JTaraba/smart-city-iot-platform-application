import requests

BASE = "http://0.0.0.0:8080/"


response = requests.get(BASE + "devices/1")
print(response.json())

'''
for i in range(len(edge_stations)):
    response = requests.put(BASE + "edgestation/3" + str(i), edge_stations[i])
    print(response.json())

input()
response = requests.get(BASE + "edgestation/1")
print(response.json())
'''
