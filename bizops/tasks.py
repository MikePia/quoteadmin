from celery import shared_task
from time import sleep
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.finnhub.finncandles import FinnCandles
from quotedb.utils import util
from .businessops import getStocks
import os


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
