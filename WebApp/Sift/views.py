from django.shortcuts import render, get_object_or_404
from Sift.models import Cluster, Post
from django.http import HttpResponseRedirect
# from postmarkup import render_bbcode
from lxml import html
from bs4 import BeautifulSoup
from django.core.cache import cache

import time
import Sift.NLTKClustering
import Sift.tasks as tasks
import Sift.forms


def general(request):
    headline = "General Analytics"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)


    pieData = [['Forum ID', 'Number of Posts']]
    for cluster in trendingClusters:
        pieData.append([cluster.name, Post.objects.filter(cluster=cluster.clusterid).count()])

    lineClusterNames = []

    for cluster in trendingClusters:
        lineClusterNames.append(cluster.name)

    lineDates = []
    lineData = {}
    posts = Post.objects.values('creationdate', 'cluster').order_by('creationdate')
    for post in posts:
        id = post["cluster"]
        if (id != None):
            date = post["creationdate"].timetuple()
            unix_date = int(time.mktime(date)) * 1000
            try:
                if unix_date in lineData:
                    lineData[unix_date][id-1] += 1
                else:
                    lineData[unix_date] = [0] * len(lineClusterNames)
                    lineData[unix_date][id-1] = 1
                    lineDates.append(unix_date)
            except:
                pass

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters':
               trendingClusters, "headline": headline, 'pieData': pieData,
               'lineData': lineData, 'lineDates': lineDates, 'lineClusterNames': lineClusterNames}

    return render(request, 'general_analytics.html', context)


def details(request, cluster_id):
    headline = "Topic Analytics"
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    # data
    cluster_posts = {}
    posts = Post.objects.values(
        'creationdate', 'body').filter(cluster=cluster_id)
    for post in posts:
        # convert date object to unix timestamp int
        date = post["creationdate"].timetuple()
        unix_date = int(time.mktime(date)) * 1000
        if unix_date in cluster_posts:
            cluster_posts[unix_date]['numPosts'] += 1
        else:
            # bbcode_body = body.text_content()
            cluster_posts[unix_date] = {"numPosts": 1, "posts": []}

        # body = html.document_fromstring(post['body']).drop_tag()
        body = BeautifulSoup(post['body']).getText()
        cluster_posts[unix_date]['posts'].append(body)

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline,
               'cluster': cluster, 'cluster_posts': cluster_posts}

    return render(request, 'details.html', context)


def settings(request):
    headline = "Settings"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    context = {'pinnedClusters': pinnedClusters,
               'trendingClusters': trendingClusters, "headline": headline}
    return render(request, 'settings.html', context)


def clustering(request):
    # cache.clear()
    if request.method == 'POST':
        f = Sift.forms.ClusterForm(request.POST)

        if f.is_valid():
            if f.cleaned_data['cluster_type'] == 1:
                is_mini_batched = False
            else:
                is_mini_batched = True

            tasks.cluster_posts_with_input.delay(str(f.cleaned_data['start_date']), str(f.cleaned_data['end_date']),
                                                         int(f.cleaned_data['num_clusters']), int(f.cleaned_data['max_features']),
                                                         is_mini_batched)

    form = Sift.forms.ClusterForm()

    headline = "Clustering"
    context = {'headline': headline, 'form': form}
    return render(request, 'clustering.html', context)


def cluster_running(request):
    headline = "Cluster Running"
    context = {'headline': headline}
    return render(request, 'cluster_running.html', context)
