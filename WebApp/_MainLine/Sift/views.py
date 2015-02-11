from django.shortcuts import render, get_object_or_404
from Sift.models import Cluster, Post
from django.db.models import Count
import json
import datetime

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

    # for s in Post:
    #     dashCategory.append



    count = Post.objects.values('creationdate').annotate(postCount = Count('threadid'))
    dateCount = list()
    dateY = list()
    dateM = list()
    dateD = list()
    for s in count:
        dateY.append(s["creationdate"].year)
        dateM.append(s["creationdate"].month)
        dateD.append(s["creationdate"].day)
        dateCount.append(s["postCount"])


    pieData = ([['Forum ID', 'Number of Posts'],
                        ['2', Post.objects.filter(forumid=2).count()],
                        ['3', Post.objects.filter(forumid=3).count()]])

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline,
               'cluster': cluster, 'pieData': pieData, 'lineDataCount': dateCount, 'lineDataDateY': dateY,
               'lineDataDateM': dateM, 'lineDataDateD': dateD,}
    return render(request, 'details.html', context)


def settings(request):
    headline = "Settings"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline}
    return render(request, 'settings.html', context)