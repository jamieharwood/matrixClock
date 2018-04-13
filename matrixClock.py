import max7219
from machine import RTC, Pin, SPI
import time
import socket
import machine
import ustruct


addBST = 3600
NTP_DELTA = 3155673600 - addBST

host = '0.uk.pool.ntp.org'

def getntptime():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1b
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    res = s.sendto(NTP_QUERY, addr)
    msg = s.recv(48)
    s.close()

    val = ustruct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA

def settime():
    t = getntptime()
    tm = time.localtime(t)
    tm = tm[0:3] + (0,) + tm[3:6] + (0,)
    rtc = machine.RTC()
    rtc.datetime(tm)

def main():
    # Set the RTC
    settime()
    rtc = RTC()

    # Setup display
    spi = SPI(1, baudrate=10000000, polarity=0, phase=0)

    display = max7219.Matrix8x8(spi, Pin(15), 12)
    display.brightness(0)

    # Init the display time variables
    timeNow = (0, 0, 0, 0, 0, 0, 0, 0)
    displayTimeNow = ''
    displayTimeLast = ''

    while True:
        timeNow = rtc.datetime()

        if timeNow[4] < 10:
            displayTimeNow = '0{0}{2}{1}'
        else:
            displayTimeNow = '{0}{2}{1}'

        if timeNow[5] < 10:
            displayTimeNow = displayTimeNow.replace('{2}', '0')
        else:
            displayTimeNow = displayTimeNow.replace('{2}', '')

        displayTimeNow = displayTimeNow.replace('{0}', str(timeNow[4]))
        displayTimeNow = displayTimeNow.replace('{1}', str(timeNow[5]))

        if displayTimeNow != displayTimeLast:
            display.fill(0)
            display.text(str(displayTimeNow),0,0,1)
            display.show()

            displayTimeLast = displayTimeNow

        time.sleep(1)

main()

