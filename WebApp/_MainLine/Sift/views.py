from django.shortcuts import render, get_object_or_404
from Sift.models import Cluster, Post
from django.db.models import Count
import json
import datetime


def general(request):
    headline = "General Analytics"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    pieData = ([['Forum ID', 'Number of Posts'],
                ['Selling on Amazon', Post.objects.filter(forumid=2).count()],
                ['Fulfillment by Amazon', Post.objects.filter(forumid=3).count()],
                ['Amazon Payments', Post.objects.filter(forumid=7).count()],
                ['MWS', Post.objects.filter(forumid=8).count()],
                ['Amazon Webstore', Post.objects.filter(forumid=10).count()],
                ['Amazon Sponsored Products', Post.objects.filter(forumid=22).count()],
                ['Login With Amazon', Post.objects.filter(forumid=23).count()],
                ['Amazon Announcements', Post.objects.filter(forumid=21).count()],
                ['Amazon Services', Post.objects.filter(forumid=17).count()],
                ['Seller Discussions', Post.objects.filter(forumid=23).count()],
                ['Checkout by Amazon forums', Post.objects.filter(forumid=16).count()],
                ['Amazon Product Ads forum', Post.objects.filter(forumid=20).count()],
                ['Forums Feedback', Post.objects.filter(forumid=6).count()],
                ['Your Groups', Post.objects.filter(forumid=26).count()],
                ['Amazon Product Ads', Post.objects.filter(forumid=4).count()],
                ['Amazon Seller Community Archive', Post.objects.filter(forumid=15).count()]
       ])

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline,'pieData': pieData}
    return render(request, 'general_analytics.html', context)


def details(request, cluster_id):

    headline = "Topic Analytics"
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    #Dashboard Data
    dashCategory = list()
    dashPost = list()
    dashMod = list()
    dashY = list()
    dashM = list()
    dashD = list()

    allposts = Post.objects.all()

    for s in allposts:
        dashCategory.append(s.categoryid)
        dashPost.append(s.body)
        dashMod.append(s.postedbymoderator)
        dashY.append(s.creationdate.year)
        dashM.append(s.creationdate.month)
        dashD.append(s.creationdate.day)

    #Line Graph Data
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
                        ['Selling on Amazon', Post.objects.filter(forumid=2).count()],
                        ['Fulfillment by Amazon', Post.objects.filter(forumid=3).count()],
                        ['Amazon Payments', Post.objects.filter(forumid=7).count()],
                        ['MWS', Post.objects.filter(forumid=8).count()],
                        ['Amazon Webstore', Post.objects.filter(forumid=10).count()],
                        ['Amazon Sponsored Products', Post.objects.filter(forumid=22).count()],
                        ['Login With Amazon', Post.objects.filter(forumid=23).count()],
                        ['Amazon Announcements', Post.objects.filter(forumid=21).count()],
                        ['Amazon Services', Post.objects.filter(forumid=17).count()],
                        ['Seller Discussions', Post.objects.filter(forumid=23).count()],
                        ['Checkout by Amazon forums', Post.objects.filter(forumid=16).count()],
                        ['Amazon Product Ads forum', Post.objects.filter(forumid=20).count()],
                        ['Forums Feedback', Post.objects.filter(forumid=6).count()],
                        ['Your Groups', Post.objects.filter(forumid=26).count()],
                        ['Amazon Product Ads', Post.objects.filter(forumid=4).count()],
                        ['Amazon Seller Community Archive', Post.objects.filter(forumid=15).count()]
               ])
    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline,
               'cluster': cluster, 'lineDataCount': dateCount, 'lineDataDateY': dateY,
               'lineDataDateM': dateM, 'lineDataDateD': dateD, 'dashCategory': dashCategory, 'dashPost': dashPost,
               'dashMod': dashMod, 'dashY': dashY, 'dashM': dashM, 'dashD': dashD}
    return render(request, 'details.html', context)


def settings(request):
    headline = "Settings"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters': trendingClusters, "headline": headline}
    return render(request, 'settings.html', context)
