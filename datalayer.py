#coding:utf-8
import pickle
import random
import re
from datetime import datetime, timedelta
from time import strptime, mktime, gmtime, strftime

import numpy as np
from matplotlib import pyplot as plt

from connectDB import *
from log import Log
from mat import variance
from tools import *





class DisplaySelectedStocks():
    def __init__(self):
        self.before = 90*60
        self.after = 30*60
        # self.before     = 60*60
        # self.after      = 0
        self.openTime   = "09:30:00"
        self.closeTime  = "15:00:00"
        self.midTime    = "13:00:00"
        self.getInfos   = GetSelectedStockInfos()

    def drawCurve(self, X, Y):
        plt.plot(Y, X, 'r--')

    #一天内最后一分钟的收盘价一般会跟前一价格相差3分钟
    def drawClosePriceCurve(self, wdCode, end_date):
        datas, len, len2 = self.getInfos.getClosePrices(wdCode, end_date, self.before, self.after)
        openPrice       = self.getInfos.getOpenPricesInDay(wdCode, end_date)

        prices = np.array([float(d[0]) for d in datas]) / openPrice - 1
        volumes = np.array([p[1] for p in datas])
        plt.subplot(221)
        plt.xlabel(toStringTime(end_date / 1000))
        plt.ylim(prices.min(), prices.max())

        index = len - len2
        plt.plot(index, prices[index], "ro")
        print index, prices[index]

        self.drawCurve(prices, range(len))

        plt.xlabel(toStringTime(end_date / 1000))
        plt.subplot(222)
        self.drawCurve(volumes / float(100000), range(len))

    def drawCurrentMACD(self):
        pass

    def drawLastFiveDaysRatio(self, wdCode, end_date):
        ratios = self.getInfos.getLastFiveDaysRatio(wdCode, end_date)
        plt.subplot(223)
        plt.bar(range(5, 0, -1), ratios)

    def show(self, wdCode, end_date):
        plt.figure(figsize=(30, 50))
        self.drawClosePriceCurve(wdCode, end_date)
        # self.drawCurrentMACD()
        self.drawLastFiveDaysRatio(wdCode, end_date)
        plt.show()

class GetSelectedStockInfos():
    def __init__(self):
        self.openTime   = "09:30:00"
        self.closeTime  = "15:00:00"
        self.midTime    = "13:00:00"

    def judgeEndDate(self, end_date, part):
        end_str = strftime("%Y-%m-%d", gmtime(end_date))
        if part == "one":
            mid_stamp = FromStringTime(end_str + " " + self.midTime)
            close_stamp = FromStringTime(end_str + " " + self.closeTime)
            if mid_stamp <= end_date and close_stamp > end_date:
                return True
            else:
                return False
        else:
            open_stamp = FromStringTime(end_str + " " + self.openTime)
            first_stamp = FromStringTime(end_str + " " + "11:30:00")
            if open_stamp < end_date and first_stamp >= end_date:
                return True
            else:
                return False

    def getOpenPricesInDay(self, wdCode, end_date):
        end_date /= 1000
        end_str = strftime("%Y-%m-%d", gmtime(end_date))
        open_stamp = FromStringTime(end_str + " " + self.openTime)
        sql = "SELECT nOpen FROM wdKLine WHERE nDate = %d000 AND wdCode = %s"
        db.c.execute(sql % (open_stamp, wdCode))
        return db.c.fetchone()

    def getClosePrices(self, wdCode, end_date, before, after):
        end_date /= 1000

        # judge end_str in mid_stamp and close_stamp
        start_stamp = end_date - before
        end_stamp   = end_date + after
        if self.judgeEndDate(end_date, "one"):
            start_stamp -= 1.5*60*60
        #
        elif self.judgeEndDate(end_date, "two"):
            end_stamp += 1.5*60*60

        sql = "SELECT nClose, iVolume FROM wdKLine WHERE (nDate BETWEEN %d000 AND %d000) AND wdCode = %s"
        len = db.c.execute(sql % (start_stamp, end_stamp, wdCode))
        datas = db.c.fetchall()

        len2 = db.c.execute(sql % (end_date, end_stamp, wdCode))

        return datas, len, len2

    def getCloseRate(self, wdCode, end_date, before, after):
        end_date /= 1000

        # judge end_str in mid_stamp and close_stamp
        start_stamp = end_date - before
        end_stamp   = end_date + after
        end_str = strftime("%Y-%m-%d", gmtime(end_date))
        mid_stamp = FromStringTime(end_str + " " + self.midTime)
        close_stamp = FromStringTime(end_str + " " + "14:00:00")
        if mid_stamp <= end_date and close_stamp > end_date:
            start_stamp -= 1.5*60*60
        #

        sql = 'SELECT (nClose / nOpen - 1), iVolume, nDate, nClose FROM wdKLine WHERE (nDate BETWEEN %d000 AND %d000) AND wdCode = "%s"' \
                % (start_stamp, end_stamp, wdCode)

        length = db.c.execute(sql)
        result  = db.c.fetchall()

        '''
        datas = []
        counter = 0

        for i in range(61):
            if counter >= len(result):
                break

            if result[counter][2] / 1000 == start_stamp:
                datas.append(result[counter])
                counter += 1
            elif result[counter][2] / 1000 - start_stamp == 1.5*60*60:
                start_stamp += 1.5*60*60
                datas.append(result[counter])
                counter += 1
            elif result[counter][2] / 1000 - start_stamp > 1.5*60*60:
                start_stamp += 1.5*60*60
                datas.append((0, 0))
            else:
                datas.append((0, 0))

            start_stamp += 60
        '''
        return result, length

    def getLastFiveDaysRatio(self, wdCode, end_date):
        end_str = strftime("%Y-%m-%d", gmtime(end_date / 1000))
        open_stamp = FromStringTime(end_str + " " + self.openTime)
        close_stamp = FromStringTime(end_str + " " + self.closeTime)
        one_day = 24*60*60
        sql = "SELECT nOpen, nClose FROM wdKLine WHERE nDate = %d000 AND wdCode = %s"
        ratios = []

        for n in range(5):
            open_stamp  = (open_stamp - one_day)
            close_stamp = (close_stamp - one_day)
            len = 0
            while not len:
                len = db.c.execute(sql % (open_stamp,  wdCode))
                if not len:
                    open_stamp -= one_day
                    close_stamp -= one_day

            openPrice   = db.c.fetchone()[0]
            len = db.c.execute(sql % (close_stamp, wdCode))
            counter = 0
            while not len:
                counter += 1
                len = db.c.execute(sql % (close_stamp - counter*60, wdCode))
            closePrice  = db.c.fetchone()[1]
            ratios.append((float(closePrice) / float(openPrice)) - 1)
        return ratios

    def getMACDAtOnePoint(self, wdCode, date):
        sql = "SELECT DIF, MACD FROM macd WHERE wdCode = %s AND nDate = %s" % (wdCode, date)
        db.c.execute(sql)
        return db.c.fetchone()

    def saveToSVMFile(self, filename, wdCode, end_date, polar, onlyCurve):
        f = open(filename, "a")
        data, length   = self.getCloseRate(wdCode, end_date, 60*60, 0)

        if not onlyCurve:
            if length != 61:
                return -1
        else:
            if length == 0:
                return -1
        # macds          = self.getMACDAtOnePoint(wdCode, end_date)
        # if not macds:
        #     return -1

        ratios      = self.getLastFiveDaysRatio(wdCode, end_date)

        element = []

        if onlyCurve:
            element.extend([0]*(61 - len(data)))
            element.extend([d[0] for d in data])
        else:
            volume  = []
            for i in range(len(data) - 1):
                volume.append(float(data[i+1][1]) / float(data[i][1]))
            element.extend(volume)
            element.extend(ratios)
            try:
                closePrice  = np.array([d[3] for d in data])
            except:
                return -1

            mean    = closePrice.sum() / float(len(closePrice))
            diff    = closePrice / float(mean) - 1
            element.extend(diff)
            # element.extend(macds)

        content = ""
        for i, e in enumerate(element):
            content += "%d:%f " % (i, e)
        if polar:
            f.write("+1 " + content + "\n")
        else:
            f.write("-1 " + content + "\n")
        f.close()
        return 0


def store(filename, struct):
    f = open(filename, "wb")
    pickle.dump(struct, f)
    f.close()

def load(filename):
    f = open(filename, "rb")
    struct = pickle.load(f)
    f.close()
    return struct

'''
def createNegative():
    date = "2016-03-30"
    end_date = datetime.strptime(date, "%Y-%m-%d")

    f = open("random.csv", "a")
    f.write("\n")
    f.close()

    for i in range(20):
        end_date -= timedelta(days=1)
        if end_date.weekday() in [5, 6]:
            i -= 1
            continue
        generateRandomDate(end_date.strftime("%Y-%m-%d"))
'''

def updateSVMDataFile(datasrc, datafile, polar, onlyCurve):
    f = open(datafile, "w")
    f.close()
    convertToSVMFormat(datasrc, datafile, polar, onlyCurve)

if __name__ == "__main__":
    # updateSVMDataFile("test.csv", "test.txt", True)
    # updateSVMDataFile("random.csv", "negdata.txt", False)
    # updateSVMDataFile("stocks.csv", "data.txt", True)
    getInfos = GetSelectedStockInfos()
    print getInfos.getCloseRate("600755", FromStringTime("2016-4-6 13:44:00")*1000, 60*60, 0)
    pass