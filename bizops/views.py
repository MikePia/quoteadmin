from django.shortcuts import render
from django.http import HttpResponse
from .forms import StartCandlesAllQuotes
from .forms import StartCandleCandles
from .forms import StartWebsocket

# Create your views here.
def startAllQuotes(request):
    if request.method == "POST":
        form = StartCandlesAllQuotes(request.POST)
        if form.is_valid():
            dadate = form.cleaned_data['dadate']
            numrepeats = form.cleaned_data['numrepeats']
            stocks = form.cleaned_data['stocks']
        
            latest = form.cleaned_data['latest']

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