#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: matricClock
"""

import max7219
from machine import RTC, Pin, SPI
import time
import urequests
import ujson
from timeClass import TimeTank
from NeoPixelClass import NeoPixel

# addBST = 3600
# NTP_DELTA = 3155673600 - addBST

# host = '0.uk.pool.ntp.org'

# Graph
min = 100
max = 0
gOff = 8 * 8
jData = None
currentTemp = 0

# Neo pixel simple levels
numSensors = 3

neoPin = 4

np = NeoPixel(neoPin, 4)

ledPower = 3

gData = [0. for x in range(0, 32)]


def getGraphData():
    print('def getGraphData():')

    url = "http://192.168.86.240:5000/getWeatherGraph/"
    returnString = ''

    # print(url)

    response = urequests.get(url)
    returnString = response.text
    response.close()

    returnString = returnString.replace('\"', '')

    # print(returnString)
    return returnString


def displayText(display, text, show):
    display.fill(0)
    display.text(text, 0, 0, 1)

    if show:
        display.show()


def main():
    # Setup display
    spi = SPI(1, baudrate=10000000, polarity=0, phase=0)

    display = max7219.Matrix8x8(spi, Pin(15), 12)
    display.brightness(0)

    np.colour(ledPower, 'Red')
    np.colour(0, 'Black')
    np.colour(1, 'Black')
    np.colour(2, 'Black')

    np.write()

    # Init the display time variables
    initLoop = True
    currHour = 0
    lastHour = 0
    hourChanged = False

    currMinute = 0
    lastMinute = 0
    minuteChanged = False

    timeNow = (0 for x in range(0, 8))

    displayTimeNow = ''
    displayTimeLast = ''

    # Set the RTC
    mytime = TimeTank()

    while not mytime.settime():
        pass

    rtc = RTC()

    while True:
        timeNow = rtc.datetime()
        currHour = timeNow[4]
        currMinute = timeNow[5]

        if currHour != lastHour:
            np.colour(2, 'Green')
            np.write()

            while not mytime.settime():
                pass

            rtc = RTC()

            timeNow = rtc.datetime()
            lastHour = currHour
            local = time.localtime()

            np.colour(2, 'Black')
            np.write()
            hourChanged = True

        if currMinute != lastMinute:
            lastMinute = currMinute
            minuteChanged = True

        # ************
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

        displayText(display, str(displayTimeNow), 0)

        # *********************
        # Display seconds pixel

        seconds = timeNow[6]
        if (seconds/2) == round(seconds/2):
            display.rect(15, 5, 2, 2, 1)
        else:
            display.rect(15, 5, 2, 2, 0)

        # *****************
        # Display the graph

        if initLoop or (currMinute in [1, 16, 31, 46] and minuteChanged):
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

        # ******************
        # Draw the bar graph
        sample = 31
        for column in jData:

            bar = round(7 - (7 / (max - min)) * (column - min))

            display.line(gOff + sample, 7, gOff + sample, bar, 1)

            sample -= 1

        currentTemp = jData[0]

        # Print current temp
        display.text(str(currentTemp), 32, 0, 1)

        display.show()

        hourChanged = False
        minuteChanged = False
        initLoop = False

        time.sleep(0.25)


main()

