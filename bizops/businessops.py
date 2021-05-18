import datetime as dt
import os
from threading import Thread

from quotedb import sp500
from quotedb.finnhub.finncandles import FinnCandles
from quotedb.getdata import (getJustGainersLosers, startTickWSKeepAlive)
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.models.candlesmodel import CandlesModel
from quotedb.models.managecandles import ManageCandles
from quotedb.utils import util


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
        elif stocks == 's&p500':
            stocks = sp500.sp500symbols
        elif stocks == 'nasdaq100':
            stocks = sp500.nasdaq100symbols
        elif stocks == 's&p_q100':
            stocks = sp500.getSymbols()
        return stocks

    # def startCandles(self, start, model=CandlesModel, latest=False, numcycles=9999999999):
    def startCandles(self, *args, **kwargs):
        if self.isrunning:
            return
        self.fc.keepGoing = True
        if isinstance(kwargs['start'], dt.datetime):
            kwargs['start'] = util.dt2unix_ny(kwargs['start'])
        t = Thread(target=self.fc.cycleStockCandles, kwargs=kwargs)
        t.start()
        self.isrunning = True

    def stop(self):
        self.fc.keepGoing = False

    def getGainersLosers(self, start, stocks, model, numrec=50):
        end = util.dt2unix(dt.datetime.utcnow())

        glstocks = getJustGainersLosers(start, end, stocks, numrec, model, local=False)
        self.stocks = glstocks
        self.fc.tickers = glstocks
        return glstocks

    def startWebSocket(self, model, start, numstocks):

        if isinstance(start, dt.datetime):
            start = util.dt2unix_ny(start)
        mc = ManageCandles(None, model)
        stocks = mc.getTickers()
        gainers, losers = mc.filterGainersLosers(stocks, start, numstocks)
        gainers.extend(losers[1:])
        gainers = [x[0] for x in gainers][1:]
        # This bogus addition of bitcoin allows it to run after hours and get something from the websocket server most any time 24/7
        # gainers.append('BINANCE:BTCUSDT')
        print(len(gainers))

        fn = util.formatFn("mockbiz.json", 'json')

        fn = os.path.normpath(fn)
        startTickWSKeepAlive(gainers, fn, ['json'], delt=None, polltime=5)


if __name__ == '__main__':
    stocks = []
    start = util.dt2unix_ny(dt.datetime(2021, 5, 17, 9, 30))
    end = util.dt2unix(dt.datetime.utcnow())
    model = AllquotesModel
    numrec = 50
    local = False
    bop = BusinessOps(stocks)
    stocks = bop.getGainersLosers(start=start, stocks=stocks, model=model)
    # Need the stocks first then reinitialize bop.fc with it
    bop.fc = FinnCandles(stocks)
    model = CandlesModel
    bop.startCandles(start=start, model=model, latest=True, numcycles=10)
