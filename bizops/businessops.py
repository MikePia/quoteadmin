import datetime as dt
import json
import os
from threading import Thread
import time

from quotedb import sp500
from quotedb.finnhub.finncandles import FinnCandles
from quotedb.finnhub.finntrade_ws import ProcessData
from quotedb.getdata import (getJustGainersLosers, startTickWS)
# from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.models.candlesmodel import CandlesModel
from . forms import getVisualFiles


from quotedb.utils import util


class BusinessOps:
    startcandle_pid = -1
    candlestocks = None
    websocketstocks = None
    threadkeepgoing = True
    socketisrunning = False
    processingdata = False

    def __init__(self, stocks):
        self.stocks = self.getStocks(stocks)
        self.fc = FinnCandles(self.stocks)
        self.isrunning = False
        self.outname = ''

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
            stocks = sp500.getQ100_Sp500()
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

        self.candlestocks = glstocks
        self.fc.tickers = glstocks
        return glstocks

    def startWebSocket(self, start, srate, numstocks, fn):
        self.threadkeepgoing = True
        self.socketisrunning = False
        if not self.candlestocks:
            return None
        if isinstance(start, dt.datetime):
            start = util.dt2unix_ny(start)
        end = util.dt2unix(dt.datetime.utcnow())
        self.websocketstocks = getJustGainersLosers(start, end, self.websocketstocks, numstocks, model=CandlesModel)

        fn = util.formatFn(fn, 'json')

        fn = os.path.normpath(fn)
        # self.websocketstocks.append('BINANCE:BTCUSDT')
        t = Thread(target=self.startTickWSKeepAlive,
                   kwargs={'stocks': self.websocketstocks,
                           'fn': fn,
                           'store': ['json'],
                           'delt': None,
                           'polltime': 5})
        t.start()
        self.socketisrunning = True
        print('thread starteed')

    def stopSocket(self):
        self.socketisrunning = False
        self.threadkeepgoing = False

    def startTickWSKeepAlive(self, stocks=[], fn="websocketdata", store=['json'], delt=None, polltime=5):

        ws_thread = startTickWS(stocks, fn=fn, store=store)

        while self.threadkeepgoing:
            cur = time.time()
            nexttime = cur + 5

            while time.time() < nexttime and self.threadkeepgoing:
                if not ws_thread.is_alive() and ws_thread.keepgoing:
                    print('Websocket was stopped: restarting...')

                    ws_thread = startTickWS(stocks, store=[format], fn=fn)
                print(' ** ')
                time.sleep(polltime)

        # This is where a new gainers could be found new subscription could be called

    def getFileNames(self):
        dirname = util.getCsvDirectory()
        if dirname is None:
            dirname = "."
        dirnames = os.listdir(dirname)
        dirnames = [(x, x) for x in dirnames if not x.startswith(".") and not x.startswith("_")]
        return dirnames

    def stopProcessing(self):
        pass

    def runVizData(self, filename='', srate=1.0, fq=None, outfile='out.json'):
        print("runVixData")
        procd = ProcessData([], None, srate)
        self.outname = procd.visualizeDataNew(filename, fq, outfile)
        self.processingdata = False
        return self.outname

    def processData(self, *args, **kwargs):
        self.processingdata = True
        kwargs['srate'] = dt.timedelta(seconds=kwargs['srate'])
        kwargs['filename'] = os.path.normpath(os.path.join(util.getCsvDirectory(), kwargs['filename']))
        t = Thread(target=self.runVizData, kwargs=kwargs)
        t.start()
        t.join()
        self.processingdata = False

        return self.outname

    def openJsonFile(self, fn):
        """
        fn should be from a list of files verified to be visualize json files
        """
        fn = os.path.join(util.getCsvDirectory(), fn)
        with open(fn, 'r') as f:
            data = f.read()
        try:
            j = json.loads(data)
        except Exception as ex:
            print(ex)
            return None
        return j

    def getFileInfo(self, fn):
        j = self.openJsonFile(fn)
        if not j:
            return None
        ret = {}
        mindate, maxdate = list(j[0].keys())[0], list(j[0].keys())[-1]
        ret['mindate'] = str(util.unix2date(int(mindate), unit='m'))
        ret['maxdate'] = str(util.unix2date(int(maxdate), unit='m'))
        try:
            stocks = [x['stock'] for x in list(j[0].values())[0]]
            ret['stocks'] = stocks
        except Exception:
            pass
        ret['filename'] = fn

        # ret = json.dumps(ret)
        return ret

    def getVisualFilenames(self):
        """Get Visual files (formatted for widget in tuples, convert to dict for json"""
        files = getVisualFiles()
        if files:
            return {i: x[0] for i, x in enumerate(files)}
        return None

    def getVisualFile(self, filename):
        """
        Get the greatest match for filename, open the file and return Json
        """
        maxname = ''
        for fn in getVisualFiles():
            if fn[0].startswith(filename) and fn[0] > maxname:
                maxname = fn[0]
        if not maxname:
            return None
        return self.openJsonFile(maxname)



if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    # stocks = []
    # end = util.dt2unix(dt.datetime.utcnow())
    # model = AllquotesModel
    # numrec = 50
    # local = False
    # bop = BusinessOps(stocks)
    # # Need the stocks first then reinitialize bop.fc with it
    # bop.fc = FinnCandles(stocks)
    # model = CandlesModel
    # bop.startCandles(start=start, model=model, latest=True, numcycles=10)
    ###########################################################################
    bop = BusinessOps([])
    start = util.dt2unix_ny(dt.datetime(2021, 5, 17, 9, 30))
    stocks = bop.getGainersLosers(start=start, stocks=[], model=CandlesModel)
    bop.candlestocks = stocks
    bop.startWebSocket(CandlesModel, start, None, 10, 'fredthefile')
    print('sleeping')
    time.sleep(60)
    bop.threadkeepgoing = False
