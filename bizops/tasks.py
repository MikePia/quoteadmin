from celery import shared_task
from time import sleep
from .businessops import BusinessOps
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.scripts.isrunning import is_running
from quotedb.finnhub.finncandles import FinnCandles
from .businessops import getStocks
import os

@shared_task
def sleepy(duration):
    rfile = "writethedamnfile"
    fn = os.path.join(os.environ.get('RUNDIR'), rfile)
    with open(fn, 'w') as f:
        f.write(str(os.getpid()))
    sleep(duration)
    return None


@shared_task
def startCandles(start, stocks, latest, numcycles):
    fc = FinnCandles(getStocks(stocks))
    fc.cycleStockCandles(start=start, stocks=stocks, model=AllquotesModel, latest=latest, numcycles=numcycles)
    return None
