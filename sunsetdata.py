import requests
import json
import time


url = "https://api.sunrise-sunset.org/json?lat=48.688737&lng=10.931199&formatted=0"
r = requests.get(url)
data = json.loads(r.content)
print(str(data))