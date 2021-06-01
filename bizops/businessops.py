import datetime as dt
import json
import os
from threading import Thread
import time

from quotedb import sp500
from quotedb.finnhub.finncandles import FinnCandles
from quotedb.getdata import (getJustGainersLosers, startTickWS)
# from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.models.candlesmodel import CandlesModel
from quotedb.scripts.isrunning import is_running


from quotedb.utils import util


def getStocks(stocks):
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


class BusinessOps:
    startcandle_pid = -1
    candlestocks = None
    websocketstocks = None
    socketisrunning = False
    processingdata = False

    def __init__(self, stocks):
        self.stocks = getStocks(stocks)
        self.fc = FinnCandles(self.stocks)
        self.isrunning = False
        self.outname = ''

    def startCandles(self, start, stopcks, model, latest, numcycles):
        """
        """

        if is_running('startcandles'):
            self.running = True
            return
        self.running = False

        self.fc.cycleStockCandles(start=start, model=model, latest=latest, numcycles=numcycles)

    def startCandlesold(self, *args, **kwargs):
        if self.isrunning:
            return
        if isinstance(kwargs['start'], dt.datetime):
            kwargs['start'] = util.dt2unix_ny(kwargs['start'])
        t = Thread(target=self.fc.cycleStockCandles, kwargs=kwargs)
        t.start()
        self.isrunning = True

    def stopCandles(self, p):
        for _ in range(4):
            if not is_running(p):
                self.isrunning = False
                break
            time.sleep(2)

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
        files = self.getVisualFiles()
        if files:
            return {i: x[0] for i, x in enumerate(files)}
        return None

    def getVisualFile(self, filename):
        """
        Get the greatest match for filename, open the file and return Json
        """
        maxname = ''
        for fn in self.getVisualFiles():
            if fn[0].startswith(filename) and fn[0] > maxname:
                maxname = fn[0]
        if not maxname:
            return None
        return self.openJsonFile(maxname)

    def isVisualizeData(self, fn):
        if not os.path.isfile(fn):
            return False
        with open(fn, 'r') as f:
            line = f.readline()
        try:
            j = json.loads(line)
        except Exception:
            return False
        if not j or (
                not isinstance(j, list)) or (
                not isinstance(j[0], dict)) or (
                not j[0].values()) or (
                not list(j[0].values())[0]) or (
                not isinstance(list(j[0].values())[0], list)) or (
                not isinstance(list(j[0].values())[0][0], dict)) or (
                not set(list(j[0].values())[0][0].keys()).issubset({'volume', 'delta_t', 'delta_v', 'delta_p', 'price', 'stock'})):
            return False
        return True

    def getVisualFiles(self):
        dirname = util.getCsvDirectory()
        filenames = [(x, x) for x in os.listdir(dirname) if self.isVisualizeData(os.path.join(dirname, x))]
        filenames.sort()
        return filenames

    def isRawData(self, fn):
        """Determine if fn is raw data created from the websocket"""
        if not os.path.isfile(fn):
            return False
        with open(fn, 'r') as f:
            line1 = f.readline()
            try:
                line1 = json.loads(line1)
                if {'price', 'stock', 'timestamp', 'volume'}.issubset(set(line1.keys())):
                    return True
            except Exception:
                pass
        return False

    def getRawFiles(self):
        """Get the files inside the data directory that are raw data files created by the websocket"""
        dirname = util.getCsvDirectory()
        filenames = [(x, x) for x in os.listdir(dirname) if self.isRawData(os.path.join(dirname, x))]
        filenames.sort()
        return filenames






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
