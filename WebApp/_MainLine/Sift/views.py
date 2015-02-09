from django.shortcuts import render, get_object_or_404
from Sift.models import Cluster, Post
import json

def general(request):
    headline = "General Analytics"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline}
    return render(request, 'general_analytics.html', context)


def details(request, cluster_id):

    headline = "Topic Analytics"
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)


    data_dict = [{'value': Post.objects.filter(forumid=2).count(), 'label': 'red', 'color': '#F7464A'}
        , {'value': Post.objects.filter(forumid=3).count(), 'label': 'blue', 'color': '#468FBD'}]

    data = json.dumps(data_dict)
    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline,
               'cluster': cluster, 'data': data}
    return render(request, 'details.html', context)


def settings(request):
    headline = "Settings"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline}
    return render(request, 'settings.html', context)


class piechartData:

    def __init__(self, value):
        self.value = value

    def __init__(self, label):
        self.label = label