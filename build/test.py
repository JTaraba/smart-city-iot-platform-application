import requests

BASE = "http://127.0.0.1:5000/"

response = requests.patch(BASE + "devices/2", {"name": "Temp5"})
print(response.json())