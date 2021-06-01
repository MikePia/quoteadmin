import datetime as dt
import json
import os
from django import forms
from quotedb.utils import util

numrepeats_choice = [('0', '0'), ('1', '1'), ('2', '2'),
                     ('3', '3'), ('4', '4'), ('5', '5'),
                     ('6', '6'), ('7', '7'), ('8', '8'),
                     ('9', '9'), ('1', '10'), ('unlimited', 'Unlimited')]
stocks_choices = [("all", "All"), ("s&p500", "S&P500"), ("nasdaq100", "Nasdaq100"),
                  ("s&p_q100", "S&P_Q100"), ("custom", "Custom")]


def twobizdays():
    day = dt.datetime.now()
    daysago = 2

    if day.weekday() > 4:
        daysago += day.weekday() - 4
    day = day - dt.timedelta(days=daysago)
    day = dt.datetime(day.year, day.month, day.day, 0, 0)
    return day


class StartCandlesAllQuotes(forms.Form):
    dadate = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh:mm"}))
    numrepeats = forms.ChoiceField(choices=numrepeats_choice, required=False)
    stocks = forms.ChoiceField(choices=stocks_choices, required=False)
    latest = forms.BooleanField(help_text="Begin with the most recent entry if checked", required=False)
    finncandles_allquotes = None
    finncandles_candles = None


class StartCandleCandlesForm(forms.Form):
    # stocks, fn, store, delt=None, polltime=5)
    start = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh:mm"}), input_formats=['%Y-%m-%d %H:%M'])
    numrepeats = forms.ChoiceField(choices=numrepeats_choice, required=False)
    num_gainerslosers = forms.IntegerField(max_value=35, min_value=5)
    stocks = forms.ChoiceField(choices=stocks_choices, required=False)
    # firstquote_date = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh-mm"}), input_formats=['%Y-%m-%d %H:%M'])

    def clean_start(self):
        start_passed = self.cleaned_data.get("start")
        start_passed = start_passed.replace(tzinfo=None)
        leastdate = twobizdays()
        print(leastdate, start_passed)
        if start_passed < leastdate:
            raise forms.ValidationError("Please choose a start date within the last 2 working days ")
        return start_passed


class StartWebsocket(forms.Form):
    # stocks, fn, store, delt=None, polltime=5)
    start = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh:mm"}), input_formats=['%Y-%m-%d %H:%M'])
    filename = forms.CharField()
    # sampleRate = forms.DecimalField(max_value=3600, min_value=0.2, decimal_places=3)
    numstocks = forms.IntegerField(max_value=25, min_value=2)


def getFileNames():
    dirname = util.getCsvDirectory()
    if dirname is None:
        dirname = "."
    dirnames = os.listdir(dirname)
    dirnames = [(x, x) for x in dirnames if not x.startswith(".") and not x.startswith("_")]
    return dirnames


def isVisualizeData(fn):
    if not os.path.isfile(fn):
        return False
    with open(fn, 'r') as f:
        line = f.readline()
    try:
        j = json.loads(line)
    except Exception:
        return False
    if not j or (
            not isinstance(j, list)) or (
            not isinstance(j[0], dict)) or (
            not j[0].values()) or (
            not list(j[0].values())[0]) or (
            not isinstance(list(j[0].values())[0], list)) or (
            not isinstance(list(j[0].values())[0][0], dict)) or (
            not set(list(j[0].values())[0][0].keys()).issubset({'volume', 'delta_t', 'delta_v', 'delta_p', 'price', 'stock'})):
        return False
    return True


def getVisualFiles():
    dirname = util.getCsvDirectory()
    filenames = [(x, x) for x in os.listdir(dirname) if isVisualizeData(os.path.join(dirname, x))]
    return filenames


def isRawData(fn):
    """Determine if fn is raw data created from the websocket"""
    if not os.path.isfile(fn):
        return False
    with open(fn, 'r') as f:
        line1 = f.readline()
        try:
            line1 = json.loads(line1)
            if {'price', 'stock', 'timestamp', 'volume'}.issubset(set(line1.keys())):
                return True
        except Exception:
            pass
    return False


def getRawFiles():
    """Get the files inside the data directory that are raw data files created by the websocket"""
    dirname = util.getCsvDirectory()
    filenames = [(x, x) for x in os.listdir(dirname) if isRawData(os.path.join(dirname, x))]
    return filenames


class ProcessVisualizeData(forms.Form):
    """A form to retrieve and process raw data files created by the web socket into visualize data."""
    def __init__(self, *args, **kwargs):
        super(ProcessVisualizeData, self).__init__(*args, **kwargs)
        self.fields['filename'] = forms.ChoiceField(choices=getRawFiles(), label="Raw data files")

    filename = forms.ChoiceField(choices=getFileNames(), label="Raw data files")
    outfile = forms.CharField(label="outfile",)
    sampleRate = forms.DecimalField(max_value=3600, min_value=0.199, decimal_places=3)
    fq = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh:mm"}),
                             input_formats=['%Y-%m-%d %H:%M'],
                             label="FirstQuote date",
                             help_text="Enter the datetime for delta comparisons")


VISUALFILE_CHOICES = [
    ('view_info', 'View info'),
    ('get_data', 'Get the data')
]


class VisualizeData(forms.Form):

    def __init__(self, *args, **kwargs):
        super(VisualizeData, self).__init__(*args, **kwargs)
        files = getVisualFiles()
        if files:
            self.fields['filename'] = forms.ChoiceField(choices=files, label="Visualize datafiles")

    filename = forms.ChoiceField(label="Visualize datafiles.")
    viewchoice = forms.CharField(label='What do you want to do?', widget=forms.RadioSelect(choices=VISUALFILE_CHOICES))


if __name__ == '__main__':
    print(getRawFiles())
    print()
