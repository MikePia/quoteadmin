import pandas as pd
import subprocess
import sys
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.utils import util

from django.contrib import messages
from threading import Thread
from django.shortcuts import render
from django.http import HttpResponse
from .businessops import BusinessOps
from .forms import StartCandlesAllQuotes
from .forms import StartCandleCandles
from .forms import StartWebsocket

from quotedb.finnhub.finncandles import FinnCandles

thebop = None
# Create your views here.
def startAllQuotes(request):
    global thebop
    if request.method == "POST":
        form = StartCandlesAllQuotes(request.POST)
        if form.is_valid():
            if thebop and thebop.isrunning:
                thebop.fc.keepGoing = False
                messages.success(request, "Stopping candle gathering")
                form.finncandles = None
                thebop.isrunning=False
            else:
                dadate = form.cleaned_data['dadate']
                start = dadate.replace(tzinfo=None)
                start = util.dt2unix_ny(pd.Timestamp(start))

                numrepeats = form.cleaned_data['numrepeats']
                numrepeats = 10000 if numrepeats == 'unlimited' else int(numrepeats)
                stocks = form.cleaned_data['stocks']
            
            
                latest = form.cleaned_data['latest']
                messages.success(request, 'Candle form was processed')
                bop = BusinessOps(stocks)
                thebop = bop
                bop.startCandles(start=start,model=AllquotesModel, latest=latest, numcycles=numrepeats)
                form.finncandles = True

        else:
            # Form validation errors
            for err in form.errors:
                for msg in form.errors[err]:
                    messages.error(request, msg)
                print()
    else:
        # Uninit for for GET
        form = StartCandlesAllQuotes()
    form_candles = StartCandleCandles()
    # formc 
    return render(request, 'form.html', {'form': form, 
                                         'form_candles': form_candles})


def startCandleCandles(request):
    if request.method == "POST":
        form_candles = StartCandleCandles(request.POST)
        if form_candles.is_valid():
            start = form_candles.cleaned_data['start']
            num_gainerslosers = form_candles.cleaned_data['num_gainerslosers']
            firstquote_date = form_candles.cleaned_data['firstquote_date']
        
    form = StartCandlesAllQuotes()
    form_candles = StartCandleCandles()
    form_websocket = StartWebsocket()
    return render(request, 'form.html', {'form': form, 
                                         'form_candles': form_candles})


def startWebsocket(request):
    if request.method == "POST":
        form_websocket = StartWebsocket(request.POST)
        if form_websocket.is_valid():
            filename = form_websocket.cleaned_data['filename']
            sampleRate = form_websocket.cleaned_data['sampleRate']
            numStocks = form_websocket.cleaned_data['sampleRate']
        
    form = StartCandlesAllQuotes()
    form_candles = StartCandleCandles()
    form_websocket = StartWebsocket()
    return render(request, 'form.html', {'form': form, 
                                         'form_candles': form_candles})

    pass