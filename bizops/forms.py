import datetime as dt
import os
from django import forms
from quotedb.finnhub.finntrade_ws import ProcessData
from quotedb.utils import util
from .businessops import BusinessOps


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


class ProcessVisualizeData(forms.Form):
    """A form to retrieve and process raw data files created by the web socket into visualize data."""
    def __init__(self, *args, **kwargs):
        super(ProcessVisualizeData, self).__init__(*args, **kwargs)
        bop = BusinessOps([])
        self.fields['filename'] = forms.ChoiceField(choices=bop.getRawFiles(), label="Raw data files")

    filename = forms.ChoiceField(choices=getFileNames(), label="Raw data files")
    outfile = forms.CharField(label="outfile",)
    sampleRate = forms.DecimalField(max_value=3600, min_value=0.199, decimal_places=3)
    fq = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh:mm"}),
                             input_formats=['%Y-%m-%d %H:%M'],
                             label="FirstQuote date",
                             help_text="Enter the datetime for delta comparisons")

    def clean_fq(self):
        """If the time is bad for the file, change it to an acceptible time.
        If the time is in reasonable boundaries, assume it was on purpose.
        """
        fq_passed = self.cleaned_data.get("fq")
        fq_passed = fq_passed.replace(tzinfo=None)
        filename_passed = self.cleaned_data.get("filename")
        procd = ProcessData([])
        fn = os.path.join(util.getCsvDirectory(), filename_passed)
        df = procd.readRawData(fn)
        df = procd.setIndextoTimestamp(df)
        if fq_passed < df.index[0] - dt.timedelta(hours=24) or fq_passed >= df.index[-1]:
            fq_passed = df.index[0] - dt.timedelta(minutes=30)
        return fq_passed


VISUALFILE_CHOICES = [
    ('view_info', 'View info'),
    ('get_data', 'Get the data')
]


class VisualizeData(forms.Form):

    def __init__(self, *args, **kwargs):
        super(VisualizeData, self).__init__(*args, **kwargs)
        bop = BusinessOps([])
        files = bop.getVisualFiles()
        if files:
            self.fields['filename'] = forms.ChoiceField(choices=files, label="Visualize datafiles")

    filename = forms.ChoiceField(label="Visualize datafiles.")
    viewchoice = forms.CharField(label='What do you want to do?', widget=forms.RadioSelect(choices=VISUALFILE_CHOICES))


if __name__ == '__main__':
    print()
