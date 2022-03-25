import requests
import json
from datetime import datetime, time, timedelta
import time as t


url = "https://api.sunrise-sunset.org/json?lat=48.688737&lng=10.931199&formatted=0"
r = requests.get(url)
# für raspberry pi wichtig. civil twilight ending
data = json.loads(r.content)
# returns string of civil_twilight_end
print(data)
dämmerung = data['results']['civil_twilight_end']
solar_noon = data['results']['solar_noon']
# codiert string in datetime.datetime
dämmerung = datetime(int(dämmerung[0:4]), int(dämmerung[5:7]), int(dämmerung[8:10]), int(dämmerung[11:13]), int(dämmerung[14:16]), int(dämmerung[17:18]))
# returns current time as datetime.datetime
aktuell = datetime.fromtimestamp(t.mktime(t.gmtime()))
# returns datetime in seconds per epoch, dadurch erhöhung und rückkonvertierung mit "datetime.fromtimestamp" möglich
print(dämmerung.timestamp())
# vergleich
print(dämmerung < aktuell)

four_pm_time = datetime.strptime('16:00', '%H:%M').time()
four_pm = datetime.combine(datetime.now(), four_pm_time)



