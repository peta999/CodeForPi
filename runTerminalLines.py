import subprocess
import time

# subprocess.run(['sudo', 'service', 'pilight', 'start'], capture_output=False)
# time.sleep(15)          # wait unitl pilight started
subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-t'], capture_output=False)  #id 100 unit 1 on
time.sleep(5)
subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-f'], capture_output=False)  #id 100 unit 1 on
time.sleep(5)
subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-t'], capture_output=False)  #id 100 unit 1 on
time.sleep(5)
subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-f'], capture_output=False)  #id 100 unit 1 off
time.sleep(5)
subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-t'], capture_output=False)  #id 100 unit 1 off
time.sleep(5)
subprocess.run(['pilight-send', '-p', 'kaku_switch', '-i', '100', '-u', '1', '-f'], capture_output=False)  #id 100 unit 1 off
time.sleep(5)
