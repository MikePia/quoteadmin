import datetime as dt
import os
import subprocess
import sys
from threading import Thread
from django.contrib import messages
import pandas as pd
# import quotedb.getdata as gd
# from quotedb.
from  quotedb import sp500
from quotedb.utils import util
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.models.candlesmodel import CandlesModel
from quotedb.finnhub.finncandles import FinnCandles
from quotedb.getdata import startCandles


class BusinessOps:
    startcandle_pid = -1

    def __init__(self, stocks):
        self.stocks = self.getStocks(stocks)
        self.fc = FinnCandles(self.stocks)
        self.isrunning = False

    def getStocks(self, stocks):
        if stocks == 'all':
            print('all stocks')
            stocks = sp500.getSymbols()
            print(len(stocks))
        elif  stocks == 's&p500':
            stocks = sp500.sp500symbols
        elif stocks == 'nasdaq100':
            stocks = sp500.nasdaq100symbols
        elif stocks == 's&p_q100':
            stocks = sp500.getSymbols()
        else:
            return -1
        return stocks

    # def startCandles(self, start, model=CandlesModel, latest=False, numcycles=9999999999):
    def startCandles(self, *args, **kwargs):
        if self.isrunning:
            return
        self.fc.keepGoing = True
        if isinstance(kwargs['start'], dt.datetime):
            kwargs['start'] = util.dt2unix_ny(kwargs['start'])
        # self.fc.cycleStockCandles(start, model, latest, numcycles)
        t = Thread(target=self.fc.cycleStockCandles, args=args, kwargs=kwargs)
        t.start()
        self.isrunning = True
        # fc.cycleStockCandles(start, model=AllquotesModel, latest=latest, numcycles=numrepeats)

    def stop(self):
        self.fc.keepGoing = False


if __name__ == '__main__':
    bop = BusinessOps()
    stocks = "s&p500"
    start=dt.datetime(2021, 5, 14, 9, 30)
    model = AllquotesModel
    bop.startCandles(stocks, start, model=model, latest=True, numcycles=0)