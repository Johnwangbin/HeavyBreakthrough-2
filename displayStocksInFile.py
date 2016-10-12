from datalayer import DisplaySelectedStocks
from tools import toStringTime, FromStringTime
import random

class DisplayStocksInFile():
    def __init__(self, filename):
        f = open(filename)
        part = f.read().strip().split("\n\n")[-1]
        self.lines = part.split("\n")
        f.close()
        self.display    = DisplaySelectedStocks()

    def displayAll(self):
        for i in range(len(self.lines)):
            self.displayOne(i)

    def displaySome(self, start, end):
        for i in range(start, end):
            self.displayOne(i)

    def displayOne(self, index):
        wdCode, end_date = self.format(self.lines[index])
        self.display.show(wdCode, end_date)

    def displayRandom(self):
        index = random.randint(0, len(self.lines) - 1)
        wdCode, end_date = self.format(self.lines[index])
        self.display.show(wdCode, end_date)

    def format(self, line):
        items = line.split(",")
        return items[1], FromStringTime("-".join(items[0].split("/")) + " " + items[2]  + ":00")*1000

