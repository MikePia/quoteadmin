import datetime as dt
import os

from threading import Thread

from quotedb import sp500

from quotedb.finnhub.finncandles import FinnCandles
from quotedb.getdata import startTickWSKeepAlive
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

    def getGainersLosers(self):

        mc = ManageCandles(None, CandlesModel)
        stocks = mc.getTickers()
        start = util.dt2unix_ny(dt.datetime(2021, 4, 26, 3, 30))
        numstocks = 12
        gainers, losers = mc.filterGainersLosers(stocks, start, numstocks)
        gainers.extend(losers[1:])
        gainers = [x[0] for x in gainers][1:]
        # This bogus addition of bitcoin allows it to run after hours and get something from the websocket server most any time 24/7
        gainers.append('BINANCE:BTCUSDT')
        print(len(gainers))

        fn = util.formatFn("mockbiz.json", 'json')

        fn = os.path.normpath(fn)
        startTickWSKeepAlive(gainers, fn, ['json'], delt=None, polltime=5)


if __name__ == '__main__':
    bop = BusinessOps()
    stocks = "s&p500"
    start = dt.datetime(2021, 5, 14, 9, 30)
    model = AllquotesModel
    bop.startCandles(stocks, start, model=model, latest=True, numcycles=0)
