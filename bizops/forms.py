from django import forms


class StartCandlesAllQuotes(forms.Form):
    dadate = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh:mm"}))
    numrepeats = forms.ChoiceField(choices=[('0', '0'), ('1', '1'), ('2', '2'),
                                            ('3', '3'), ('4', '4'), ('5', '5'),
                                            ('6', '6'), ('7', '7'), ('8', '8'),
                                            ('9', '9'), ('1', '10'), ('unlimited', 'Unlimited')], required=False)
    stocks = forms.ChoiceField(choices=[("all", "All"),
                                        ("s&p500", "S&P500"),
                                        ("nasdaq100", "Nasdaq100"),
                                        ("s&p_q100", "S&P_Q100"),
                                        ("custom", "Custom")], required=False)
    latest = forms.BooleanField(help_text="Begin with the most recent entry if checked", required=False)
    finncandles_allquotes = None
    finncandles_candles = None


class StartCandleCandles(forms.Form):
    # stocks, fn, store, delt=None, polltime=5)
    start = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh-mm"}), input_formats=['%Y-%m-%d %H:%M'])
    num_gainerslosers = forms. IntegerField(max_value=35, min_value=5)
    # firstquote_date = forms.DateTimeField(widget=forms.DateTimeInput({"placeholder": "yyyy-mm-dd hh-mm"}), input_formats=['%Y-%m-%d %H:%M'])


class StartWebsocket(forms.Form):
    # stocks, fn, store, delt=None, polltime=5)
    filename = forms.CharField()
    sampleRate = forms.DecimalField(max_value=3600, min_value=0.2, decimal_places=3)
    numStocks = forms.IntegerField(max_value=25, min_value=2)
