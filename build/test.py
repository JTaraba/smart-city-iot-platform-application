import requests

BASE = "http://127.0.0.1:5000/"

data = [{"name": "Gbg1", "device_type": "garbage temp", "deviceID": 3},
        {"name": "Temp3", "device_type": "Temperature Sensor", "deviceID": 4},
        {"name": "Temp2", "device_type": "Temperature Sensor", "deviceID": 7}
        ]

for i in range(len(data)):
    response = requests.put(BASE + "devices/3" + str(i), data[i])
    print(response.json())


input()
response = requests.get(BASE + "devices/2")
print(response.json())