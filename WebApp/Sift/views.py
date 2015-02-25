from django.shortcuts import render, get_object_or_404
from Sift.models import Cluster, Post
from django.http import HttpResponseRedirect
# from postmarkup import render_bbcode
from lxml import html
from django.core.cache import cache

import time
import Sift.NLTKClustering

import Sift.forms



def general(request):
    headline = "General Analytics"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)


    # pieData = ([['Forum ID', 'Number of Posts'],
    #             ['Selling on Amazon', Post.objects.filter(forumid=2).count()],
    #             ['Fulfillment by Amazon', Post.objects.filter(forumid=3).count()],
    #             ['Amazon Payments', Post.objects.filter(forumid=7).count()],
    #             ['MWS', Post.objects.filter(forumid=8).count()],
    #             ['Amazon Webstore', Post.objects.filter(forumid=10).count()],
    #             ['Amazon Sponsored Products', Post.objects.filter(forumid=22).count()],
    #             ['Login With Amazon', Post.objects.filter(forumid=23).count()],
    #             ['Amazon Announcements', Post.objects.filter(forumid=21).count()],
    #             ['Amazon Services', Post.objects.filter(forumid=17).count()],
    #             ['Seller Discussions', Post.objects.filter(forumid=23).count()],
    #             ['Checkout by Amazon forums', Post.objects.filter(forumid=16).count()],
    #             ['Amazon Product Ads forum', Post.objects.filter(forumid=20).count()],
    #             ['Forums Feedback', Post.objects.filter(forumid=6).count()],
    #             ['Your Groups', Post.objects.filter(forumid=26).count()],
    #             ['Amazon Product Ads', Post.objects.filter(forumid=4).count()],
    #             ['Amazon Seller Community Archive', Post.objects.filter(forumid=15).count()]
    #    ])

    pieData = [['Forum ID', 'Number of Posts']]
    for cluster in trendingClusters:
        pieData.append([cluster.name, Post.objects.filter(cluster=cluster.clusterid).count()])

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters':
               trendingClusters, "headline": headline, 'pieData': pieData}

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
            body = html.document_fromstring(post['body']).text_content()
            # bbcode_body = body.text_content()
            cluster_posts[unix_date] = {"numPosts": 1, "posts": []}
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
    cache.clear()
    if request.method == 'POST':
        f = Sift.forms.ClusterForm(request.POST)

        if f.is_valid():
            if f.cleaned_data['cluster_type'] == 1:
                is_mini_batched = False
            else:
                is_mini_batched = True

            Sift.NLTKClustering.cluster_posts_with_input(str(f.cleaned_data['start_date']), str(f.cleaned_data['end_date']),
                                                         int(f.cleaned_data['num_clusters']), int(f.cleaned_data['max_features']),
                                                         is_mini_batched)\
                                                        .delay("sample")

            return HttpResponseRedirect('/cluster_running')

    else:
        form = Sift.forms.ClusterForm()

    headline = "Clustering"
    context = {'headline': headline, 'form': form}
    return render(request, 'clustering.html', context)


def cluster_running(request):
    headline = "Cluster Running"
    context = {'headline': headline}
    return render(request, 'cluster_running.html', context)
