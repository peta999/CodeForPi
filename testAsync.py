import os
import time as t
import requests
import json
from threading import Thread
from multiprocessing.pool import ThreadPool
import Adafruit_DHT
import paho.mqtt.client as mqtt
from datetime import datetime, time, timedelta
import subprocess
import yaml
import smtplib, ssl

DHT_SENSOR = Adafruit_DHT.AM2302
DHT_PIN = 4
temp_list = []
hum_list = []
temp_average = 0
hum_average = 0
client = mqtt.Client()
csv = None
verschiebung_abends = 0
verschiebung_morgens = 0
hühner_aktiviert = False
hilfsZeit = 0
url = "https://api.sunrise-sunset.org/json?lat=48.688737&lng=10.931199&formatted=0"

port = 587  # For SSL email server
smtp_server = "smtp.gmail.com"
sender_email = "gewaechshaustemperatur@gmail.com"  # Enter your address
receiver_email = "gewaechshaustemperatur@gmail.com"  # Enter receiver address
password = "raspberrypi"

message = """\
Subject: Geweachshaustemperatur niedrig

Temperatur zu niedrig, bitte ueberpruefen"""



"""try:
    csv  = open('/home/pi/humidity.csv', 'a+')
    if os.stat('/home/pi/humdity.csv').st_size == 0:
        csv.write('Date,Time,Temperature,Humidity\t\n')
except:
    pass
"""
def main():
    # open_csv()
    # if open_csv() is not True:
    #     print("-1")
    #     return -1

    # pilight-daemon starten
    subprocess.run(['sudo', 'service', 'pilight', 'start'], capture_output=False)
    
    # config laden
    getConfig()

    # declare hühner_aktiviert as global
    global hühner_aktiviert
    global hilfsZeit

    # mqtt einrichten
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect("192.168.2.24", 1883, 60)
    client.subscribe("settings", 1)
    client.loop_start()
    count = 0   # count to keep cooldown after sending warning email
    count_refresh_dämmerung = 240

    # dämmerung nach Programmstart initialisieren
    r = requests.get(url)
    # für raspberry pi wichtig. civil twilight ending
    data = json.loads(r.content)
    dämmerung = data['results']['civil_twilight_end']
    solar_noon = data['results']['solar_noon']
    # codiert string in datetime.datetime
    dämmerung = datetime(int(dämmerung[0:4]), int(dämmerung[5:7]), int(dämmerung[8:10]), int(dämmerung[11:13]), int(dämmerung[14:16]), int(dämmerung[17:18]))
    solar_noon = datetime(int(solar_noon[0:4]), int(solar_noon[5:7]), int(solar_noon[8:10]), int(solar_noon[11:13]), int(solar_noon[14:16]), int(solar_noon[17:18]))
    dämmerung_verschoben = dämmerung.timestamp() + verschiebung_abends * 60
    dämmerung_verschoben = datetime.fromtimestamp(dämmerung_verschoben) 
    while True:
        # get current time
        st_all = t.time()
        st_all1 = t.process_time()

        st = t.time()
        st1 = t.process_time()



        pool = ThreadPool(processes=1)
        temp, hum = get_temperature_humidity()
        async_result = pool.apply_async(get_temperature_humidity)

        et = t.time()
        et1 = t.process_time()

        #print wall and execution time
        print("wall time: " + str(et - st))
        print("execution time: " + str(et1 - st1))


        # wait 50 seconds
        t.sleep(50)

        st = t.time()
        st1 = t.process_time()
        
        # make a 10 second Thread to make while loop take excactly 60 seconds

        delay_thread = Thread(target=thread_sleep_x_seconds, args=(10,))
        delay_thread.start()
        
        temp, hum = async_result.get()

        et = t.time()
        et1 = t.process_time()
        print("wall time: " + str(et - st))
        print("execution time: " + str(et1 - st1))

        st = t.time()
        st1 = t.process_time()

        if(valid_temperature(temp) and valid_humidity(hum)):
            now = datetime.now()            
            cal_avg_hum()
            cal_avg_temp()       
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            data = "{}, {}, {}".format(temp, hum, dt_string)
            client.publish("data", data, 1)
            print(str(data))

            if(len(temp_list) > 10 and sum(temp_list) / len(temp_list) <= 9.5 and count == 0):
                send_mail()
                count = 120

            if(count > 0):
                count = count - 1

            if(count_refresh_dämmerung >= 240):
                re = requests.get(url)
                data = json.loads(re.content)
                vergleicher = data['results']['civil_twilight_end']
                vergleicher = datetime(int(vergleicher[0:4]), int(vergleicher[5:7]), int(vergleicher[8:10]), int(vergleicher[11:13]), int(vergleicher[14:16]), int(vergleicher[17:18]))
                if(dämmerung != vergleicher):
                    dämmerung = vergleicher
                    dämmerung_verschoben = dämmerung.timestamp() + verschiebung_abends * 60
                    dämmerung_verschoben = datetime.fromtimestamp(dämmerung_verschoben)
                count_refresh_dämmerung = 0

            aktuell = datetime.fromtimestamp(t.mktime(t.gmtime()))
            
            
            # Abends Strom anschalten
            if(hühner_aktiviert == False and dämmerung_verschoben < aktuell):
                # Strom an
                activatePowerHuehnerstall()
                
                hilfsZeit = dämmerung_verschoben.timestamp() +  60 * 60 * 16
                
                hühner_aktiviert = True

                updateConfig()
            
            # Mittags Strom ausschalten
            if (hühner_aktiviert == True and datetime.fromtimestamp(hilfsZeit) < aktuell):
                # Strom aus
                deactivatePowerHuehnerstall()
                
                hühner_aktiviert = False
            
                updateConfig()
        et = t.time()
        et1 = t.process_time()
        print("wall time: " + str(et - st))
        print("execution time: " + str(et1 - st1))
        delay_thread.join
        et_all = t.time()
        et_all1 = t.process_time()
        print("wall time: " + str(et_all - st_all))
        print("execution time: " + str(et_all1 - st_all1))


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")

def on_disconnect(client, userdata, rc):
    print("Unexpected disconnection")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    if msg.topic == "settings":
        global verschiebung_morgens
        global verschiebung_abends
        message = msg.payload
        help1, help2 = str(message).replace("'","").split(",", 1)
        help1 = help1.replace("b","")
        verschiebung_morgens = int(help1)
        verschiebung_abends = int(help2)
        print("in method on_message" + str(verschiebung_abends) + str(verschiebung_morgens) + "")

        updateConfig()


def get_temperature_humidity():
    while True:   
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            return round(temperature, 1), round(humidity, 1)

# Berechnet Durchschnittstemperatur
def cal_avg_temp():
    if temp_list:
        help_average = 0
        for i in range(0, len(temp_list)):
            help_average = help_average + temp_list[i]
        temp_average = help_average / len(temp_list)
        return temp_average
    return -500

# Berechnet Durchschnittsfeuchtigkeit
def cal_avg_hum():
    if hum_list:
        help_average = 0
        for i in range(0, (len(hum_list))):
            help_average = help_average + hum_list[i]
        hum_average = help_average / len(hum_list)
        return hum_average
    return -500

# Checks if temperature is valid | abweichung von avg_temperature
def valid_temperature(temp):
    avg_temp = cal_avg_temp()
    temp_list.append(temp)
    if len(temp_list) >= 15:
        if avg_temp >= (temp + 5) or avg_temp <= (temp + 5):
            temp_list.pop(0)
            return True
        temp_list.pop(0)
        return False
    return True

# Checks if humidity is valid | abweichung von avg_humidity
def valid_humidity(hum):
    avg_hum = cal_avg_hum()
    hum_list.append(hum)            
    if len(hum_list) >= 15:
        if avg_hum >= (hum + 5) or avg_hum <= (hum + 5):
            hum_list.pop(0)
            return True
        hum_list.pop(0)
        return False
    return True

# Speichert übergebene Werte in .csv Datei
def save_values_in_csv(temp, hum):
    csv.write('{0},{1},{2:0.1f}*C,{3:0.1f}%\r\n'.format(t.strftime('%m/%d/%y'), t.strftime('%H:%M'), temp, hum))

# Öffnet .csv Datei -> True: Erfolg
def open_csv():
    try:
        csv = open('/home/pi/humidity.csv', 'a+')
        if os.stat('/home/pi/humidity.csv').st_size == 0:
            csv.write('Date,Time,Temperature,Humidity\r\n')
            return True
    except:
        return False


# sends temperature warning email
def send_mail():
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()

def activatePowerHuehnerstall():
    x = Thread(target = activatePowerHuehnerstallThread(), args=())
    y = Thread(target = activatePowerHuehnerstallThread(), args=())
    z = Thread(target = activatePowerHuehnerstallThread(), args=())
    x.start()
    y.start()
    z.start()

def deactivatePowerHuehnerstall():
    x = Thread(target = deactivatePowerHuehnerstallThread(), args=())
    y = Thread(target = deactivatePowerHuehnerstallThread(), args=())
    z = Thread(target = deactivatePowerHuehnerstallThread(), args=())
    x.start()
    y.start()
    z.start()

# sends 433Mhz on signal to id 100, u 1
def activatePowerHuehnerstallThread():
    subprocess.run(['sudo', 'pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-t'], capture_output=False)  #id 100 unit 1 on

# sends 433Mhz off signal to id 100, u 1
def deactivatePowerHuehnerstallThread():
    subprocess.run(['sudo', 'pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-f'], capture_output=False)  #id 100 unit 1 on

# get values from config.yaml
def getConfig():
    with open("config.yaml") as file:
        global verschiebung_abends
        global verschiebung_morgens
        global hühner_aktiviert
        global hilfsZeit
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        list_doc = yaml.safe_load(file)
        verschiebung_abends = list_doc["huehnerstall"]["verschiebung_abends"]
        verschiebung_morgens = list_doc["huehnerstall"]["verschiebung_morgens"]        
        hühner_aktiviert = list_doc["huehnerstall"]["an"]
        hilfsZeit = list_doc["huehnerstall"]["hilfs_zeit"]

def updateConfig():
    with open("config.yaml") as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        list_doc = yaml.safe_load(file)

    print(str(verschiebung_abends) + str(verschiebung_morgens) + "")
    list_doc["huehnerstall"]["verschiebung_abends"] = verschiebung_abends
    list_doc["huehnerstall"]["verschiebung_morgens"] = verschiebung_morgens
    list_doc["huehnerstall"]["an"] = hühner_aktiviert
    list_doc["huehnerstall"]["hilfs_zeit"] = hilfsZeit

    with open("config.yaml", "w") as f:
        yaml.dump(list_doc, f)
    

def thread_sleep_x_seconds(x):
    t.sleep(x)

main()
