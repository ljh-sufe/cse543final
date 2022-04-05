import time

from utils import key, makeurl, makeurlMA, makeFactorName

import pandas as pd
import requests
from tqdm import tqdm
import timeit

sp500cons = pd.read_csv("spxstocks.csv")

sp500cons = sp500cons.set_index("Date")
stockList = sp500cons.Ticker.value_counts().index.to_list()

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


import os

dateList = pd.date_range("2000-01-01", "2022-04-04", freq="M")
factorsList = ["SMA", "EMA", "WMA", "DEMA", "TEMA", "TRIMA", "KAMA", "MAMA"]
# get X for predicting return
for factor in factorsList:

    filepath = "/Users/lanjunhao/Desktop/csefinal/data/" + factor + "/"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    files = os.listdir(filepath)

    nowtime = timeit.default_timer()
    pause = 0

    for count, stock in enumerate(tqdm(stockList)):

        if timeit.default_timer() - nowtime > 60 and count - pause > 75:  # if this loop executes more than 75 times in a minute, stop for a while
            time.sleep(5)
            nowtime = timeit.default_timer()
            pause = pause + 75

        factorName = makeFactorName(keyword=factor, interval="monthly", time_period=10)
        filename = stock + "_" + factorName + ".csv"
        if filename in files:
            continue

        url = makeurlMA(keyword=factor, stock=stock, interval="monthly", time_period=10)
        try:
            r = requests.get(url)
            data = r.json()
            if len(data) == 0:
                a = pd.Series(index=dateList)
            elif len(data["Technical Analysis: " + factor]) == 0:
                a = pd.Series(index=dateList)
            else:
                a = pd.DataFrame(data["Technical Analysis: " + factor]).T[factor]
        except:
            time.sleep(61)
            r = requests.get(url)
            data = r.json()
            if len(data) == 0:
                a = pd.Series(index=dateList)
            elif len(data["Technical Analysis: " + factor]) == 0:
                a = pd.Series(index=dateList)
            else:
                a = pd.DataFrame(data["Technical Analysis: " + factor]).T[factor]

        a.name = factorName

        a.to_csv(filepath + filename)
    print(factor)

# url = makeurl(keyword="BALANCE_SHEET", stock="IBM")
# r = requests.get(url)
# data = r.json()
#
# print(data)

# factorsList = ["SMA", "EMA", "WMA"]
import os

stockList
b = None
for stock in stockList:

    a = None
    for factor in factorsList:
        filepath = "/Users/lanjunhao/Desktop/csefinal/data/" + factor + "/"
        d = pd.read_csv(filepath + stock + "_" + factor + "_monthly_10.csv").set_index("Unnamed: 0")
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
b.reset_index().sort_values(by=["time", "stock"]).set_index(["time", "stock"])
