from celery import shared_task
import datetime as dt
import time
import os
from quotedb.dbconnection import getSaConn
from quotedb.getdata import (getJustGainersLosers, startTickWS)
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.models.managecandles import ManageCandles
from quotedb.finnhub.finncandles import FinnCandles
from quotedb.finnhub.finntrade_ws import ProcessData
from quotedb.models.candlesmodel import CandlesModel
from quotedb.utils import util
from bizops.businessops import getStocks


@shared_task
def sleepy(duration):
    rfile = "writethedamnfile"
    util.startRunning(rfile)

    while True:
        time.sleep(15)
        if not util.isRunning(rfile):
            print('file has been deleted')
            break
    return None


@shared_task
def startCandles(start, stocks, latest, numcycles, rfile):
    fc = FinnCandles(getStocks(stocks))
    fc.cycleStockCandles(start=start, model=AllquotesModel, latest=latest, numcycles=numcycles, rfile=rfile)
    return None


@shared_task
def startCandleCandlesTask(start, stocks, latest, numcycles, numrecs, rfile):
    stocks = getStocks(stocks)
    end = util.dt2unix(dt.datetime.utcnow())
    stocks = getJustGainersLosers(start, end, stocks, numrecs, AllquotesModel, local=False)
    fc = FinnCandles(stocks)
    fc.cycleStockCandles(start=start, model=CandlesModel, latest=latest, numcycles=numcycles, rfile=rfile)


@shared_task
def startWebSocketTask(start, srate, fn, numrec, rfile='socket.pid'):
    end = util.dt2unix(dt.datetime.utcnow())
    mc = ManageCandles(getSaConn(), CandlesModel)
    stocks = mc.getTickersSinceDate(start)
    fmt = ['json']
    polltime = 5

    glstocks = getJustGainersLosers(start, end, stocks, numrec, CandlesModel, local=False)
    ws_thread = startTickWS(glstocks, fn=fn, store=fmt, delt=srate)
    util.startRunning(rfile)

    while util.isRunning(rfile):
        cur = time.time()
        nexttime = cur + 5

        while time.time() < nexttime and util.isRunning:
            if not ws_thread.is_alive() and util.isRunning:
                print('Websocket was stopped: restarting...')

                ws_thread = startTickWS(glstocks, store=[format], fn=fn)
            print(' ** ')
            time.sleep(polltime)
    ws_thread.ws.close()


@shared_task
def processDataTask(filename='', srate=0.5, fq=None, outfile='visualize.json', rfile="processvisual.txt"):
    srate = dt.timedelta(seconds=srate)
    filename = os.path.normpath(os.path.join(util.getCsvDirectory(), filename))
    util.startRunning(rfile)
    procd = ProcessData([], None, srate)
    procd.visualizeDataNew(filename, fq, outfile)
    util.stopRunning(rfile)
    # while util.isRunning(kwargs['rfile']):


if __name__ == '__main__':
    start = util.dt2unix_ny(dt.datetime(2021, 5, 28, 12, 0))
    startWebSocketTask(start, None,  "thetestfiles", 35, rfile='socket.pid')
