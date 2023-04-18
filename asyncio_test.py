import asyncio
import random
from re import A
import time
import threading
from multiprocessing.pool import ThreadPool
import requests
from datetime import datetime, timedelta
import json



def main():
    url_string = "https://api.sunrise-sunset.org/json?lat=48.688737&lng=10.931199&"
    url_string2 = "&formatted=0"
    date_object = datetime.now()
    date = date_object.strftime("%Y-%m-%d")

    all_data = []

    for i in range(0, 14600):
        # get current date YYYY-MM-DD
        date_string_for_url = "date=" + date
        request_string = url_string + date_string_for_url + url_string2
        re = requests.get(request_string)

        data = json.loads(re.content)


        civil_twilight_end = data['results']['civil_twilight_end']
        solar_noon = data['results']['solar_noon']

        # codiert string in datetime.datetime
        civil_twilight_end = datetime(int(civil_twilight_end[0:4]), int(civil_twilight_end[5:7]), int(civil_twilight_end[8:10]), int(civil_twilight_end[11:13]), int(civil_twilight_end[14:16]), int(civil_twilight_end[17:18]))
        solar_noon = datetime(int(solar_noon[0:4]), int(solar_noon[5:7]), int(solar_noon[8:10]), int(solar_noon[11:13]), int(solar_noon[14:16]), int(solar_noon[17:18]))
        
        # create a string in Json format data:[{date, result{civil_twilight_end, solar_noon}}]
        
        data_string = '{"date": "' + date + '", "result": {"civil_twilight_end": "' + civil_twilight_end.strftime("%H:%M:%S") + '", "solar_noon": "' + solar_noon.strftime("%H:%M:%S") + '"}},'
        all_data.append(data_string)

        # date_object + 1 day
        date_object = date_object + timedelta(days=1)
        date = date_object.strftime("%Y-%m-%d")

    # write all_data to data.json
    with open('data.json', 'a') as outfile:
        outfile.write("[")
        outfile.write("\n")
        for i in range(0, len(all_data)):
            outfile.write(all_data[i])
            outfile.write("\n")
        outfile.write("]")
        outfile.write("\n")


if __name__ == '__main__':
    main()