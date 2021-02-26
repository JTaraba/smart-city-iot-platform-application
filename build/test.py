import requests

BASE = "http://ec2-50-19-241-198.compute-1.amazonaws.com:8080/"


response = requests.get(BASE + "devices/1")
print(response.json())



input()
response = requests.get(BASE + "edgestation/1")
print(response.json())
