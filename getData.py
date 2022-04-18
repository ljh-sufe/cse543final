import time

from utils import key, makeurl, makeurlMA, makeFactorName, makeurlHT
import os
import pandas as pd
import requests
from tqdm import tqdm
import timeit
import pandas_datareader.data as pdr
import pandas as pd
import datetime as dt
from pathlib import Path

sp500cons = pd.read_csv("spxstocks.csv")

sp500cons = sp500cons.set_index("Date")
stockList = sp500cons.Ticker.value_counts().index.to_list()

test = True
if test:
    stockList = stockList[0:10]

#
# # get price data (daily) for the computing cov matrix
# priceData = None
# nowtime = timeit.default_timer()
# pause = 0
# for count, stock in enumerate(tqdm(stockList)):
#     if timeit.default_timer() - nowtime > 60 and count - pause > 75:  # if this loop executes more than 75 times in a minute, stop for a while
#         time.sleep(5)
#         nowtime = timeit.default_timer()
#         pause = pause + 75
#     url = makeurl("TIME_SERIES_DAILY_ADJUSTED", stock)
#     r = requests.get(url)
#     data = r.json()
#     try:
#         a = pd.DataFrame(data["Time Series (Daily)"]).T
#         a["stock"] = stock
#         if priceData is None:
#             priceData = a
#         else:
#             priceData = priceData.append(a)
#     except:
#         pass

# Get stock history of 10 years
start = dt.datetime(2010, 1, 1)
end = dt.datetime(2021, 1, 1)
stock_code = 'GE'
df = pdr.DataReader(stock_code, 'yahoo', start, end)
df.head(10)

dateList = pd.date_range("2000-01-01", "2022-04-04", freq="BM")
dateList = [x.__str__()[0:10] for x in dateList]


class MAfactor():
    def __init__(self, factorname, timeperiod):
        self.name = factorname
        self.timeperiod = timeperiod


# factorsList = ["SMA", "EMA", "WMA", "DEMA", "TEMA", "TRIMA", "KAMA", "MAMA", "HT_TRENDLINE", "MOM"]
factorsList = []
factorsList.append(MAfactor("SMA", 20))
factorsList.append(MAfactor("SMA", 60))
factorsList.append(MAfactor("SMA", 200))
factorsList.append(MAfactor("MOM", 20))
factorsList.append(MAfactor("MOM", 60))
factorsList.append(MAfactor("MOM", 200))
factorsList.append(MAfactor("ROC", 20))
factorsList.append(MAfactor("ROC", 60))
factorsList.append(MAfactor("ROC", 200))
factorsList.append(MAfactor("ROCR", 20))
factorsList.append(MAfactor("ROCR", 60))
factorsList.append(MAfactor("ROCR", 200))
factorsList.append(MAfactor("MFI", 20))
factorsList.append(MAfactor("MFI", 60))
factorsList.append(MAfactor("MFI", 200))

# get X for predicting return
for factor in factorsList:

    filepath = "data/" + factor.name + "_" + str(factor.timeperiod) + "/"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    files = os.listdir(filepath)

    nowtime = timeit.default_timer()
    pause = 0

    for count, stock in enumerate(tqdm(stockList)):
        # if this loop executes more than 75 times in a minute, stop for a while
        if timeit.default_timer() - nowtime > 60 and count - pause > 75:
            time.sleep(5)
            nowtime = timeit.default_timer()
            pause = pause + 75

        factorName = makeFactorName(keyword=factor.name, interval="daily", time_period=factor.timeperiod)
        filename = stock + "_" + factorName + ".csv"
        if filename in files:
            continue

        if "MA" in factor.name:
            url = makeurlMA(keyword=factor.name, stock=stock, interval="daily", time_period=factor.timeperiod)
        elif "HT" in factor.name:
            url = makeurlHT(keyword=factor.name, stock=stock, interval="daily")
        elif factor.name in ["MOM", "ROC", "ROCR", "MFI"]:
            url = makeurlMA(keyword=factor.name, stock=stock, interval="daily", time_period=factor.timeperiod)
        try:
            r = requests.get(url)
            data = r.json()
            if len(data) == 0:
                a = pd.Series(index=dateList)
            elif len(data["Technical Analysis: " + factor.name]) == 0:
                a = pd.Series(index=dateList)
            else:
                a = pd.DataFrame(data["Technical Analysis: " + factor.name]).T[factor.name]
        except:
            time.sleep(61)
            r = requests.get(url)
            data = r.json()
            if len(data) == 0:
                a = pd.Series(index=dateList)
            elif len(data["Technical Analysis: " + factor.name]) == 0:
                a = pd.Series(index=dateList)
            else:
                a = pd.DataFrame(data["Technical Analysis: " + factor.name]).T[factor.name]

        a.name = factorName
        a = a.reindex(dateList)
        a.to_csv(filepath + filename)
    print(factor)

b = None
for stock in stockList:

    a = None
    for factor in factorsList:
        filepath = "data/" + factor.name + "_" + str(factor.timeperiod) + "/"
        d = pd.read_csv(filepath + stock + "_" + factor.name + "_daily_" + str(factor.timeperiod) + ".csv").set_index(
            "Unnamed: 0")
        if a is None:
            a = d
        else:
            a = a.join(d)

    a["stock"] = stock
    if b is None:
        b = a
    else:
        b = b.append(a)

b.index.name = "time"
b = b.reset_index().sort_values(by=["time", "stock"]).set_index(["time", "stock"])

c = b.corr()

print(c.values)
