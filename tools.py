from time import strptime, mktime, gmtime, strftime

from datetime import datetime

import connectDB
from connectDB import *
import re

import datalayer
from log import Log


def toStringTime(seconds):
    return strftime("%Y-%m-%d %H:%M:%S", gmtime(seconds))

def FromStringTime(time_str):
    return mktime(strptime(time_str, "%Y-%m-%d %H:%M:%S")) + 8*60*60

def getAllStocksIds():
    f = open(stocksinfo + "stocks_list.txt", "r")
    items   = re.split("\s", f.read().strip())
    reg     = re.compile(r"\((\d+)\)")

    stocks_id   = []
    for item in items:
        item = item.strip()
        if not item[:3].find("ST") == -1:
            continue
        matches   = reg.findall(item)
        stocks_id.append(matches[-1])

    return stocks_id

def deleteSTStocks():
    f = open(stocksinfo + "stocksInwdKLine.txt", "r")
    lines = f.readlines()
    w_lines = []
    stocksids = getAllStocksIds()
    for line in lines:
        line = line.strip()
        if line.strip() in stocksids:
            w_lines.append(line)
    f.close()

    f = open(stocksinfo + "stocksInwdKLine.txt", "w")
    f.write("\n".join(w_lines))
    f.close()

def filterIdsInMacd():
    f = open(stocksinfo + "stocksInMacd.txt", "r")
    lines = f.readlines()
    w_lines = []
    stocksids = getAllStocksIds()

    for line in lines:
        line = line.strip()
        if line[:6] in stocksids:
            w_lines.append(line)
    f.close()

    f = open(stocksinfo + "stocksInMacd.txt", "w")
    f.write("\n".join(w_lines))
    f.close()

def getStocksIdsInDB(filename):
    f = open(stocksinfo + filename, "r")
    txt = f.read().strip()
    f.close()
    return txt.split("\n")

def getGoodExplosionPoint(wdCode, end_date):
    getInfos = datalayer.GetSelectedStockInfos()

    datas, len, len2 = getInfos.getClosePrices(wdCode, FromStringTime(end_date)*1000, 90*60, 30*60)

    prices = [d[0] for d in datas]
    index = len - len2

    val     = max(prices[:index])

    if prices[index] < val:
        for counter in range(1, 5):
            if prices[index + counter] > val:
                print "find good point"
                return 1
        return -1
    return 1

def getGoodPointFromAll():
    f = open(datasource + "stocks.csv", "r")
    lines = f.read().strip().split("\n")
    f.close()

    log = Log()
    for line in lines:
        elements = line.split(",")
        date = "-".join(elements[0].split("/")) + " " + elements[2] + ":00"
        rtn = getGoodExplosionPoint(elements[1], date)
        if rtn == 1:
            log.log("good", date)
        else:
            log.log("bad", date)

if __name__ == "__main__":
    getGoodPointFromAll()
    pass