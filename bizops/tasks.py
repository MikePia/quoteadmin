from celery import shared_task
import datetime as dt
from time import sleep
from quotedb.getdata import getJustGainersLosers
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.finnhub.finncandles import FinnCandles
from quotedb.models.candlesmodel import CandlesModel
from quotedb.utils import util
from .businessops import getStocks


@shared_task
def sleepy(duration):
    rfile = "writethedamnfile"
    util.startRunning(rfile)
    
    while True:
        sleep(15)
        if not util.isRunning(rfile):
            print('file has been deleted')
            break
    return None


@shared_task
def startCandles(start, stocks, latest, numcycles):
    fc = FinnCandles(getStocks(stocks))
    fc.cycleStockCandles(start=start, model=AllquotesModel, latest=latest, numcycles=numcycles)
    return None


@shared_task
def startCandleCandles(start, stocks, latest, numcycles, numrecs):
    stocks = getStocks(stocks)
    end = util.dt2unix(dt.datetime.utcnow())
    stocks = getJustGainersLosers(start, end, stocks, numrecs, AllquotesModel, local=False)
    fc = FinnCandles(stocks)
    fc.cycleStockCandles(start=start, model=CandlesModel, latest=latest, numcycles=numcycles)
