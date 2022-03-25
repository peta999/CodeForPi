import subprocess
import time
from threading import Thread

# subprocess.run(['sudo', 'service', 'pilight', 'start'], capture_output=False)
# time.sleep(15)          # wait unitl pilight started
# subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-t'], capture_output=False)  #id 100 unit 1 on
# time.sleep(5)
# subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-f'], capture_output=False)  #id 100 unit 1 on
# time.sleep(5)
# subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-t'], capture_output=False)  #id 100 unit 1 on
# time.sleep(5)
# subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-f'], capture_output=False)  #id 100 unit 1 off
# time.sleep(5)
# subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-t'], capture_output=False)  #id 100 unit 1 off
# time.sleep(5)
# subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-f'], capture_output=False)  #id 100 unit 1 off
# time.sleep(5)

def main():
    #activatePowerHuehnerstall()
    activatePowerHuehnerstallThread()
    time.sleep(5)
    deactivatePowerHuehnerstall()

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

main()
