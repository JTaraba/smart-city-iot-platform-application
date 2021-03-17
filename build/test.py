import requests
import json

url = ""

response = requests.get(url)
print(response.text)