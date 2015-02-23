__author__ = 'cse498'

from django import forms
from functools import partial
import datetime

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

CHOICES = (('1', 'K-Means'), ('2', 'Mini-Batch'))


def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + \
        ((date.month) + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31,
                       29 if not y % 40 and y % 400 else 28, 31, 30, 31, 30,
                       31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


class ClusterForm(forms.Form):
    start_date = forms.DateField(label="Start Date", widget=DateInput(
    ), initial=monthdelta(datetime.date.today(), -2))
    end_date = forms.DateField(
        label="End Date", widget=DateInput(), initial=datetime.date.today())
    all_posts = forms.BooleanField(required = False)
    num_clusters = forms.IntegerField(label="Number of Clusters", initial=8)
    max_features = forms.IntegerField(
        label="Max Number of Features", initial=10000)
    cluster_type = forms.ChoiceField(widget=forms.Select, choices=CHOICES)
