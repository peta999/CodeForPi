import os
import time
import Adafruit_DHT
import paho.mqtt.client as mqtt
from datetime import datetime
import smtplib, ssl

DHT_SENSOR = Adafruit_DHT.AM2302
DHT_PIN = 4
temp_list = []
hum_list = []
temp_average = 0
hum_average = 0
client = mqtt.Client()
csv = None
port = 587  # For SSL email server
smtp_server = "smtp.gmail.com"
sender_email = "gewaechshaustemperatur@gmail.com"  # Enter your address
receiver_email = "gewaechshaustemperatur@gmail.com"  # Enter receiver address
password = "raspberrypi"

message = """\
Subject: Geweachshaustemperatur niedrig

Temperatur zu niedrig, bitte ueberpruefen"""



try:
    csv  = open('/home/pi/humidity.csv', 'a+')
    if os.stat('/home/pi/humdity.csv').st_size == 0:
        csv.write('Date,Time,Temperature,Humidity\t\n')
except:
    pass

def main():
#    open_csv()
#    if open_csv() is not True:
#        print("-1")
#        return -1
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.2.54", 1883, 60)
    count = 0   # count to keep cooldown after sending warning email
    while True:
        temp, hum = get_temperature_humidity()
        if(valid_temperature(temp) and valid_humidity(hum)):
            temp_list.append(temp)
            temp_list.pop(0)
            hum_list.append(hum)
            hum_list.pop(0)
            cal_avg_hum()
            cal_avg_temp()
            save_values_in_csv(temp, hum)
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            data = "temperature: {}, humidity: {}, date: {}".format(temp, hum, dt_string)
            client.publish("data", data, 1)

            if(len(temp_list) > 0 and sum(temp_list) / len(temp_list) <= 9.5 and count == 0):
                send_mail()
                count = 120

            if(count > 0):
                count = count - 1    


        time.sleep(10)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def get_temperature_humidity():
    while True:   
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            return temperature, humidity

# Berechnet Durchschnittstemperatur
def cal_avg_temp():
    if temp_list:
        help_average = 0
        for i in range(0, len(temp_list)):
            help_average = help_average + temp_list[i]
        temp_average = help_average / len(temp_list)

# Berechnet Durchschnittsfeuchtigkeit
def cal_avg_hum():
    if hum_list:
        help_average = 0
        for i in range(0, (hum_list)):
            help_average = help_average + hum_list[i]
        hum_average = help_average / len(hum_list)

# Checks if temperature is valid | abweichung von avg_temperature
def valid_temperature(temp):
    if len(temp_list) >= 15:
        if cal_avg_temp() >= (temp + 5) or cal_avg_temp <= (temp + 5):
            return True
        return False
    return True

# Checks if humidity is valid | abweichung von avg_humidity
def valid_humidity(hum):
    if len(hum_list) >= 15:
        if cal_avg_hum() >= (hum + 5) or cal_avg_hum <= (hum + 5):
            return True
        return False
    return True

# Speichert übergebene Werte in .csv Datei
def save_values_in_csv(temp, hum):
    csv.write('{0},{1},{2:0.1f}*C,{3:0.1f}%\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), temp, hum))

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

main()
