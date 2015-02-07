from django.shortcuts import render, get_object_or_404
from Sift.models import Cluster

def general(request):
    headline = "General Analytics"
    trendingClusters = Cluster.objects.filter(pinned=0)
    pinnedClusters = Cluster.objects.filter(pinned=1)

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline}
    return render(request, 'general_analytics.html', context)


def details(request, cluster_id):

    headline = "Topic Analytics"
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    trendingClusters = Cluster.objects.filter(pinned=0)
    pinnedClusters = Cluster.objects.filter(pinned=1)

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline,
               'cluster': cluster}
    return render(request, 'details.html', context)
