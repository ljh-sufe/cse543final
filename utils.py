# key = "WUJ3DLML0IG4WL6W"
key = "6KC4LXT70B7P9KRY"


def makeurl(keyword, stock, key=key):
    url = 'https://www.alphavantage.co/query?function=' + keyword + '&symbol=' + stock + '&apikey=' + key
    return url


def makeFactorName(keyword, interval, time_period):
    return keyword + "_" + str(interval) + "_" + str(time_period)


def makeurlMA(keyword, stock, interval, time_period, series_type="close", key=key):
    interval = str(interval)
    time_period = str(time_period)
    url = "https://www.alphavantage.co/query?function=" + keyword + "&symbol=" + stock + "&interval=" + interval + "&time_period=" + time_period + "&series_type=" + series_type + "&apikey=" + key
    return url



def makeurlHT(keyword, stock, interval, series_type="close", key=key):
    interval = str(interval)
    url = "https://www.alphavantage.co/query?function=" + keyword + "&symbol=" + stock + "&interval=" + interval + "&series_type=" + series_type + "&apikey=" + key
    return url
