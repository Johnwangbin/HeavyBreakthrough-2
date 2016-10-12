import matplotlib
import pylab as pl
import numpy as np
from datalayer import load
import matplotlib.pyplot as plt

def plotOneCurv(x, label):
    pl.figure(1)
    pl.plot(x, "b")
    pl.title("%s changes by days" % label)
    pl.xlabel(label)
    pl.ylabel("day")
    pl.show()


def plotOneHistogram(x, label):
    pl.hist(x)
    pl.xlabel(label)
    bins = np.arange(0.,300.,1.)
    pl.show(x, bins)

if __name__ == "__main__":
    # stock_infos, CHGs = load("store3.txt")
    # print stock_infos[0], CHGs[0]
    # plotOneCurv([stock_infos[i][1] for i in range(len(stock_infos))], "rate")
    pass
