import pandas as pd
from datalayer import GetSelectedStockInfos
from modelOnlyCurve import SVCModel
from tools import *
from datetime import timedelta, datetime
from connectDB import db
import random
import numpy as np
from libsvm.svmutil import *
from log import Log
from useSVM import scaleTrainSet

class traverseCurve():
    def __init__(self):
        self.getSeletedStockInfos = GetSelectedStockInfos()
        self.stockIdsInDB         = getStocksIdsInDB("stocksInMacd.txt")
        self.log                  = Log()

    def getCurve(self, wdCode, end_date, bias):
        num     = bias / 60
        bias    = bias + 1.5*60*60
        data, length = self.getSeletedStockInfos.getCloseRate(wdCode, end_date, bias, 0)
        if length <= num:
            return -1

        # convert wdCode to macdCode (add region marker)
        macdCode = ""
        for code in self.stockIdsInDB:
            if wdCode == code[:-3]:
                macdCode = code

        macds, length   = self.getAllMACDs(macdCode, end_date, bias)

        if length <= num:
            return -1

        return data, macds

    def getAllMACDs(self, wdCode, end_date, bias):
        end_date /= 1000
        sql = """SELECT DIF, MACD FROM macd WHERE wdCode = "%s" AND nDate BETWEEN %d000""" \
              """ AND %d000""" % (wdCode, end_date - bias, end_date)

        length = db.c.execute(sql)
        return db.c.fetchall(), length


    def traverseOneCurve(self, wdCode, day):
        end_time = "14:45:00"
        end_date = FromStringTime(day + " " + end_time)*1000
        bias     = 3.75*60*60
        offset   = 60

        rtn = self.getCurve(wdCode, end_date, bias)
        if rtn == -1:
            return -1
        else:
            data, macds = rtn

        ratios      = self.getSeletedStockInfos.getLastFiveDaysRatio(wdCode, end_date)
        for i in range(int(bias / 60) + 1 - offset):
            element = []
            element.extend([d[0] for d in data[i:i + offset]])
            element.extend([d[1] / float(100000) for d in data[i:i + offset]])
            element.extend(ratios)
            try:
                closePrice  = [d[3] for d in data[i:i + offset]]
            except:
                return -1

            mean    = sum(closePrice) / float(len(closePrice))
            diff    = [c / float(mean) - 1 for c in closePrice]

            element.extend(diff)
            element.extend(macds[i + 59])

            res = self.judgeBySVM(element)
            if res == 1.0:
                date = datetime.strptime("09:30:00", "%H:%M:%S") + datetime.timedelta(minutes=i)
                self.log.log(wdCode, day + " " + date)

    def judgeBySVM(self, element):
        m       = svm_load_model(models + "heavy.model")
        res = svm_predict([1.0], [element], m)
        return res[0][0]

    def normalization(self, element, range_name):
        f = open(range_name)
        lines = f.read().strip().split("\n")
        f.close()

        rtn = []
        # rtn.append(element[0])
        for e, line in zip(element, lines):
            upper = float(line.split(" ")[1])
            floor = float(line.split(" ")[0])
            rtn.append(-1 + 2*(e - floor) / (upper - floor))

        return rtn

    def getRange(self, path, range_path):
        f = open(path)
        lines = f.read().strip().split("\n")
        f.close()

        values = []
        for line in lines:
            items = line.strip().split(" ")[1:]
            row     = []
            for i in items:
                row.append(float(i.split(":")[1]))
            values.append(row)

        f = open(range_path, "w")
        for i in range(len(values[0])):
            vector = np.array([row[i] for row in values])
            f.write(str(vector.min()) + " " + str(vector.max()) + "\n")
        f.close()

def convert():
    f = open(svmdata + "data.txt")
    lines = f.read().strip().split("\n")
    f.close()

    traver = traverseCurve()

    w_lines = []
    for l in lines:
        vect = []
        for item in l.strip().split(" ")[1:]:
            vect.append(float(item.split(":")[1]))
        w_lines.append(traver.normalization(vect, dRange + "data.myrange"))

    f = open(scale + "myscale.scale", "w")
    ha_lines = []
    for line in w_lines:
        str = "+1 "
        items = []
        for i, item in enumerate(line):
            items.append("%d:%f" % (i, item))

        str += " ".join(items)
        ha_lines.append(str)
    f.write("\n".join(ha_lines))
    f.close()

'''
def traverseSomeCurves():
    traver  = traverseCurve()
    day = "2016-03-21"
    ids = getStocksIdsInDB("stocksInMacd.txt")
    for i, id in enumerate(ids):
        if i == 10:
            break
        if rtn == -1:
            print "not enough"
        else:
            data, macds = rtn
            print data
            print macds
'''

if __name__ == "__main__":
    traver  = traverseCurve()
    # traver.traverseOneCurve("600458", "2016-3-29")
    # scaleTrainSet(svmdata + "data.txt", scale + "data.scale", dRange + "data.range")
    # traver.getRange(svmdata + "data.txt", dRange + "data.myrange")
    convert()
    pass
    # print toStringTime(1459510080000 / 1000)