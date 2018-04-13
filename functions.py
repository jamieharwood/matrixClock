import urequests
ipAddress: str = 'http://192.168.86.240:5000'

def ltime(timeNow):

    displayTimeNow = '{0}{1}'.replace('{0}', timeNow[4]).replace('{1}', timeNow[5])

    return displayTimeNow

def getTime():
    returnText = ''
    url = '{0}/timeNow/'.replace('{0}', ipAddress)

    try:
        response = urequests.get(url)

        returnText = response.text  # This should be EPOC time

        response.close()
    except:#  Fail www connect...
        returnText = ''

    return returnText

