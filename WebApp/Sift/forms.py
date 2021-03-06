from Sift.models import StopWord, Cluster, Post
from django import forms
from functools import partial
import datetime
import os

__author__ = 'cse498'

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

SENTI_CHOICES = (('pos', 'Positive'), ('neutral', 'Neutral'), ('neg', 'Negative'))
CLUSTER_CHOICES = [(i.clusterid, i.name) for i in Cluster.objects.all()]


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
    start_date = forms.DateField(label="Start Date", widget=DateInput(),
                                 initial=monthdelta(datetime.date.today(),
                                                    -2).strftime('%m/%d/%Y'),
                                 required=False)
    end_date = forms.DateField(
        label="End Date", widget=DateInput(),
        initial=datetime.date.today().strftime('%m/%d/%Y'), required=False)
    all_posts = forms.BooleanField(required=False)
    num_clusters = forms.IntegerField(label="Number of Clusters", initial=8)
    max_features = forms.IntegerField(
        label="Max Number of Features", initial=1000)
    is_creation_clustering = forms.BooleanField(required=False)


class StopwordDelete(forms.Form):

    def __init__(self, *args, **kwargs):
        super(StopwordDelete, self).__init__(*args, **kwargs)
        self.fields['word'].help_text = None
        self.fields['word'].widget.attrs['size'] = '12'
        self.fields['word'].widget.attrs['width'] = '3'
    word = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          queryset=StopWord.objects.all()
                                          .order_by('word'),
                                          label="")


class StopwordAdd(forms.Form):

    def __init__(self, *args, **kwargs):
        super(StopwordAdd, self).__init__(*args, **kwargs)
        self.fields['add_word'].help_text = None
    add_word = forms.CharField(label="")


class EditClusterName(forms.Form):
    edit_cluster = forms.CharField()


class ExportData(forms.Form):

    start_date = forms.DateField(label="Start Date", widget=DateInput(),
                                 initial=monthdelta(datetime.date.today(),
                                                    -1).strftime('%m/%d/%Y'),
                                 required=False)
    end_date = forms.DateField(
        label="End Date", widget=DateInput(),
        initial=datetime.date.today().strftime('%m/%d/%Y'), required=False)
    all_posts = forms.BooleanField(required=False)
    sentiment = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={"checked":""}),
                                          choices=SENTI_CHOICES)
    clusters = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={"checked":""}),
                                          choices=CLUSTER_CHOICES)


class ClusterDetails(forms.Form):

    start_date = forms.DateField(label="Start Date", widget=DateInput(),
                                 initial=monthdelta(datetime.date.today(),
                                                    -3).strftime('%m/%d/%Y'),
                                 required=True)
    end_date = forms.DateField(
        label="End Date", widget=DateInput(),
        initial=datetime.date.today().strftime('%m/%d/%Y'), required=True)
