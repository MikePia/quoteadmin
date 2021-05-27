from celery import shared_task
from time import sleep
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.finnhub.finncandles import FinnCandles, isRunning, stopRunning
from .businessops import getStocks
import os

@shared_task
def sleepy(duration):
    
    rfile = "writethedamnfile"
    print('in tasks')
    rfile = os.path.join(os.environ.get('RUNDIR'), rfile)
    with open(rfile, 'w') as f:
        print(f'Creating file for pid {os.getpid} in {rfile}')
        f.write(str(os.getpid()))
    while True:
        sleep(15)
        print('Checking for existance of file')
        if not os.path.exists(rfile):
            break
    print(f'File has been deleted going to exit now')
    return None


@shared_task
def startCandles(start, stocks, latest, numcycles):
    fc = FinnCandles(getStocks(stocks))
    fc.cycleStockCandles(start=start, stocks=stocks, model=AllquotesModel, latest=latest, numcycles=numcycles)
    return None
