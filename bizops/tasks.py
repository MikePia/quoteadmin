from celery import shared_task
from time import sleep
from .businessops import BusinessOps


@shared_task
def sleepy(duration):
    sleep(duration)
    return None


@shared_task
def startCandles(start, stocks, model, latest, numcycles):
    bop = BusinessOps(stocks)
    bop.startCandles(start, model, latest, numcycles)
    print()
