import max7219
from machine import RTC, Pin, SPI
import time
import socket
import machine
import ustruct
import urequests
import ujson
import neopixel


addBST = 3600
NTP_DELTA = 3155673600 - addBST

host = '0.uk.pool.ntp.org'

# Neo pixel simple levels
numSensors = 3

neoLow = 0
neoMid = 64
neoHi = 255


def getGraphData():
    url = "http://192.168.86.240:5000/getWeatherGraph/"
    returnString = ''

    # print(url)

    try:
        response = urequests.get(url)
        returnString = response.text
        response.close()

        returnString = returnString.replace('\"', '')

        # print(returnString)
    except:
        print('Fail www connect...')

    return returnString


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
    np = neopixel.NeoPixel(machine.Pin(4), 4)

    np[3] = (neoMid, neoLow, neoLow)

    np[0] = (neoMid, neoLow, neoMid)
    np[1] = (neoMid, neoLow, neoMid)
    np[2] = (neoMid, neoLow, neoMid)

    np.write()

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

        #*************
        # Display time
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
            displayTimeLast = displayTimeNow

        display.fill(0)
        display.text(str(displayTimeNow), 0, 0, 1)


        # *********************
        # Display seconds pixel

        seconds = timeNow[6]
        if (seconds/2) == round(seconds/2):
            display.rect(15, 5, 2, 2, 1)
        else:
            display.rect(15, 5, 2, 2, 0)


        # Display the graph
        gData = getGraphData()

        jData = ujson.loads(gData)
        min = 100
        max = 0

        gOff = 8 * 8

        display.line(gOff, 0, gOff, 7, 1)
        display.line(gOff, 7, gOff + 32, 7, 1)

        # Get min and max
        sample = 0
        for column in jData:
            # print(jData[sample])

            if column < min:
                min = column
            if column > max:
                max = column

            sample += 1

        # Draw the bar graph
        sample = 31
        for column in jData:

            bar = round(7 - (7 / (max - min)) * (column - min))

            display.line(gOff + sample, 7, gOff + sample, bar, 1)

            sample -= 1

        display.show()

        time.sleep(0.25)

main()

