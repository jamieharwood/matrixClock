#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: npt
"""

# borrowed from https://github.com/micropython/micropython/blob/master/esp8266/scripts/ntptime.py
import socket
import machine
import time
import ustruct

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600
host = "pool.ntp.org"

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


print("Get NTP Time")
# set the RTC using time from ntp
settime()
print("Display RTC Time")
# print out RTC datetime
print(machine.RTC().datetime())
print("Set NIC Time")


