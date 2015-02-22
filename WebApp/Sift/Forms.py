__author__ = 'cse498'

from django import forms


class ClusterForm(forms.Form):
    num_clusters = forms.CharField(label=" Number of Clusters")
    max_features = forms.CharField(label="Max number of Features")
    start_date = forms.CharField(label="Start date: Format mm-dd-yyyy")
    end_date = forms.CharField(label="End date: Format mm-dd-yyyy")
