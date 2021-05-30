import pandas as pd
from quotedb.models.allquotes_candlemodel import AllquotesModel
from quotedb.models.candlesmodel import CandlesModel
from quotedb.utils import util

from quotedb.finnhub.finncandles import FinnCandles

from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .businessops import BusinessOps
from .forms import (StartCandlesAllQuotes,  StartCandleCandlesForm,
                    StartWebsocket, ProcessVisualizeData,
                    VisualizeData)
from .tasks import sleepy as sleepytask
from .tasks import startCandles as startCandlesTask, startCandleCandlesTask

thebebop = None     # for startCandleCandles
thebebopsocket = None    # For web socket, copied from thebebop
thebebopprocessing = None

QUOTERUNNING = False
CANDLERUNNING = False
SOCKETRUNNING = False
QUOTEPID = "startcandles.pid"
CANDLEPID = "startcandlecandles.pid"
SOCKETPID = "socket.pid"

def startAllQuotes(request):
    global QUOTERUNNING
    QUOTERUNNING = util.isRunning(QUOTEPID)
    if request.method == "POST":

        if QUOTERUNNING:
            util.stopRunning(QUOTEPID)
            messages.success(request, "Stopping candle gathering for the allquotes table")
            QUOTERUNNING = False
            form = StartCandlesAllQuotes()
        else:

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
                startCandlesTask.delay(start, stocks, latest, int(numrepeats))
                QUOTERUNNING = True
                # bop.startCandlesold(kwargs)
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
    form_candles = StartCandleCandlesForm()
    form_websocket = StartWebsocket()
    form_processdata = ProcessVisualizeData()
    form_visualizedata = VisualizeData()

    return render(request, 'form.html', {'form_quotes': form,
                                         'form_candles': form_candles,
                                         'form_websocket': form_websocket,
                                         'form_processdata': form_processdata,
                                         'form_visualizedata': form_visualizedata,
                                         'quoterunning': QUOTERUNNING,
                                         'candlerunning': CANDLERUNNING,
                                         'socketrunning': SOCKETRUNNING
                                         })


def startCandleCandles(request):
    global CANDLERUNNING
    CANDLERUNNING = util.isRunning(CANDLEPID)
    if request.method == "POST":
        if CANDLERUNNING:
            util.stopRunning(CANDLEPID)
            messages.success(request, "Stopping candle gathering for the candles table")
            CANDLERUNNING = False
            form_candles = StartCandleCandlesForm(request.POST)
        else:

            form_candles = StartCandleCandlesForm(request.POST)

            if form_candles.is_valid():
                start = form_candles.cleaned_data['start']
                # start = start.replace(tzinfo=None)
                start = util.dt2unix_ny(pd.Timestamp(start))
                stocks = form_candles.cleaned_data['stocks']
                numrepeats = form_candles.cleaned_data['numrepeats']
                numrepeats = 10000 if numrepeats == 'unlimited' else int(numrepeats)

                num_gainerslosers = form_candles.cleaned_data['num_gainerslosers']
                latest = False
                messages.success(request, 'Candle form was processed')

                # startCandleCandlesTask.delay(start, stocks, latest, numrepeats, num_gainerslosers)
                startCandleCandlesTask(start, stocks, latest, numrepeats, num_gainerslosers)
                messages.success(request, 'Started gathering candles')
                CANDLERUNNING = True

    else:
        messages.warning(request, "Failed to validate the candles form")
        form_candles = StartCandleCandlesForm()
    form_quotes = StartCandlesAllQuotes()
    form_websocket = StartWebsocket()
    form_processdata = ProcessVisualizeData()
    form_visualizedata = VisualizeData()
    return render(request, 'form.html', {'form_quotes': form_quotes,
                                         'form_candles': form_candles,
                                         'form_websocket': form_websocket,
                                         'form_processdata': form_processdata,
                                         'form_visualizedata': form_visualizedata,
                                         'quoterunning': QUOTERUNNING,
                                         'candlerunning': CANDLERUNNING,
                                         'socketrunning': SOCKETRUNNING
                                         })


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
    form_candles = StartCandleCandlesForm()
    form_processdata = ProcessVisualizeData()
    form_visualizedata = VisualizeData()
    return render(request, 'form.html', {'form_quotes': form_quotes,
                                         'form_candles': form_candles,
                                         'form_websocket': form_websocket,
                                         'form_processdata': form_processdata,
                                         'form_visualizedata': form_visualizedata,
                                         'quoterunning': QUOTERUNNING,
                                         'candlerunning': CANDLERUNNING,
                                         'socketrunning': SOCKETRUNNING
                                         })


def processVisualizeData(request):
    global thebebopprocessing
    ofn = None
    if request.method == "POST":
        if thebebopprocessing and thebebopprocessing.processingdata:
            thebebopprocessing.stopProcess()
            messages.success(request, "Stopping the data processing")
            thebebopprocessing = None
        form_processdata = ProcessVisualizeData(request.POST)
        if form_processdata.is_valid():
            filename = form_processdata.cleaned_data['filename']
            outfile = form_processdata.cleaned_data['outfile']
            srate = float(form_processdata.cleaned_data['sampleRate'])
            fq = form_processdata.cleaned_data['fq'].replace(tzinfo=None)
            fq = util.dt2unix_ny(pd.Timestamp(fq))
            if not thebebopprocessing:
                thebebopprocessing = BusinessOps([])
            thebebopprocessing.processingdata = False
            ofn = thebebopprocessing.processData(filename=filename, srate=srate, fq=fq, outfile=outfile)
    else:
        form_processdata = ProcessVisualizeData()
    form_quotes = StartCandlesAllQuotes()
    form_candles = StartCandleCandlesForm()
    form_websocket = StartWebsocket()
    form_visualizedata = VisualizeData()
    return render(request, 'form.html', {'form_quotes': form_quotes,
                                         'form_candles': form_candles,
                                         'form_websocket': form_websocket,
                                         'form_processdata': form_processdata,
                                         'form_visualizedata': form_visualizedata,
                                         'thebebop': thebebop,
                                         'thebebopsocket': thebebopsocket,
                                         'thebebopprocessing': thebebopprocessing,
                                         'outfilename': ofn
                                         })


def getVisualData(request):
    if request.method == 'POST':
        form_visualizedata = VisualizeData(request.POST)
        if form_visualizedata.is_valid():
            filename = form_visualizedata.cleaned_data['filename']
            viewchoice = form_visualizedata.cleaned_data['viewchoice']
        bop = BusinessOps([])
        if viewchoice == "get_data":
            jdata = bop.openJsonFile(filename)
            if jdata:
                return JsonResponse(jdata, safe=False)
        elif viewchoice == "view_info":
            finfo = bop.getFileInfo(filename)
            if finfo:
                return JsonResponse(finfo)

    form_quotes = StartCandlesAllQuotes()
    form_candles = StartCandleCandlesForm()
    form_websocket = StartWebsocket()
    form_processdata = ProcessVisualizeData()
    form_visualizedata = VisualizeData()

    return render(request, 'form.html', {'form_quotes': form_quotes,
                                         'form_candles': form_candles,
                                         'form_websocket': form_websocket,
                                         'form_processdata': form_processdata,
                                         'form_visualizedata': form_visualizedata,
                                         'thebebop': thebebop,
                                         'thebebopsocket': thebebopsocket,
                                         'thebebopprocessing': thebebopprocessing
                                         })


def getVisualFilenames(request):
    bop = BusinessOps([])
    fnames = bop.getVisualFilenames()
    if fnames:
        return JsonResponse(fnames)
    return JsonResponse({"No visual data found"})
    print()


def getVisualFile(request, filename):
    """Return the latest matching file matching filename
    Latest is determined by the filename and the timestamp in its name
    """
    print()
    bop = BusinessOps([])
    jdata = bop.getVisualFile(filename)
    if jdata:
        return JsonResponse(jdata, safe=False)
    return JsonResponse({'error': f"File not found with visual data matching {filename}"})


def sleepy(request):
    sleepytask.delay(12)
    return HttpResponse('Done sleepy like!')
