import pandas as pd
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.models.candlesmodel import CandlesModel
from quotedb.utils import util
from quotedb.finnhub.finncandles import FinnCandles

from django.contrib import messages
from django.shortcuts import render
from .businessops import BusinessOps
from .forms import StartCandlesAllQuotes
from .forms import StartCandleCandles
from .forms import StartWebsocket


thebop = None       # for startAllQuotes
thebebop = None     # for startCandleCandles
thebebopsocket = None    # For web socket, copied from thebebop


def startAllQuotes(request):
    global thebop
    if request.method == "POST":

        if thebop and thebop.isrunning:
            thebop.fc.keepGoing = False
            messages.success(request, "Stopping candle gathering for the allquotes table")
            # form.finncandles_allquotes = None
            thebop.isrunning = False
            thebop = None

        form = StartCandlesAllQuotes(request.POST)
        if form.is_valid():
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
            bop.startCandles(start=start, model=AllquotesModel, latest=latest, numcycles=numrepeats)
            form.finncandles_allquotes = True

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
    form_websocket = StartWebsocket()

    return render(request, 'form.html', {'form_quotes': form,
                                         'form_candles': form_candles,
                                         'form_websocket': form_websocket,
                                         'thebop': thebop,
                                         'thebebop': thebebop,
                                         'thebebopsocket': thebebopsocket})


def startCandleCandles(request):
    global thebebop
    global thebebopsocket
    if request.method == "POST":
        if thebebop and thebebop.isrunning:
            thebebop.fc.keepGoing = False
            messages.success(request, "Stopping candle gathering for the candles table")
            thebebop.isrunning = False
            thebebopsocket = thebebop
            thebebop = None
        form_candles = StartCandleCandles(request.POST)

        if form_candles.is_valid():
            start = form_candles.cleaned_data['start']
            start = start.replace(tzinfo=None)
            start = util.dt2unix_ny(pd.Timestamp(start))

            num_gainerslosers = form_candles.cleaned_data['num_gainerslosers']

            bop = BusinessOps([])
            stocks = bop.getGainersLosers(start=start, stocks=[], model=AllquotesModel)
            thebebop = bop
            # Need the stocks first then reinitialize bop.fc with it
            bop.fc = FinnCandles(stocks)
            bop.startCandles(start=start, model=CandlesModel, latest=True, numcycles=num_gainerslosers)

    else:
        form_candles = StartCandleCandles()
    form = StartCandlesAllQuotes()
    form_websocket = StartWebsocket()
    return render(request, 'form.html', {'form_quotes': form,
                                         'form_candles': form_candles,
                                         'form_websocket': form_websocket,
                                         'thebop': thebop,
                                         'thebebop': thebebop,
                                         'thebebopsocket': thebebopsocket})


def startWebsocket(request):
    global thebebopsocket
    if request.method == "POST":
        if thebebopsocket and thebebopsocket.socketisrunning:
            thebebopsocket.stopSocket()
            messages.success(request, "Stopping webs socket")
            thebebopsocket = None

        form_websocket = StartWebsocket(request.POST)

        if form_websocket.is_valid():
            start = form_websocket.cleaned_data['start']
            start = start.replace(tzinfo=None)
            start = util.dt2unix_ny(pd.Timestamp(start))
            fn = form_websocket.cleaned_data['filename']
            # sampleRate = form_websocket.cleaned_data['sampleRate']
            numstocks = form_websocket.cleaned_data['numstocks']

            bop = thebebopsocket
            if bop:
                bop.startWebSocket(start, None, numstocks, fn)
                messages.success(request, 'Web socket started')
                
            else:
                messages.error(request, "Missing the stocks. Please run startCandles")
    else:
        form_websocket = StartWebsocket()

    form_quotes = StartCandlesAllQuotes()
    form_candles = StartCandleCandles()
    return render(request, 'form.html', {'form_quotes': form_quotes,
                                         'form_candles': form_candles,
                                         'form_websocket': form_websocket,
                                         'thebop': thebop,
                                         'thebebop': thebebop,
                                         'thebebopsocket': thebebopsocket
                                         })

    pass
