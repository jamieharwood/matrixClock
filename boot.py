# boot.py -- run on boot-up
from network import WLAN
import pycom, machine, time

pycom.heartbeat(False)
pycom.rgbled(0x007f00) # green

toggleLed = True
flashCount = 5

wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()

for net in nets:
    if net.ssid == 'dodger':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'skinner2263'), timeout=5000)
        while not wlan.isconnected():
            if toggleLed == True:
                toggleLed == False
                pycom.rgbled(0x7f0000) # red
            else:
                toggleLed == True
                pycom.rgbled(0x007f00) # green
            
            machine.idle() # save power while waiting
        
        print('WLAN connection succeeded!')

        for count in range(1, flashCount):
            pycom.rgbled(0x007f00) # green
            time.sleep(0.1)
            pycom.rgbled(0x7f0000) # red
            time.sleep(0.1)
        pycom.rgbled(0x000000) # black
        break