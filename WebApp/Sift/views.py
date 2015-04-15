from django.shortcuts import render, get_object_or_404
from Sift.models import Cluster, Post, ClusterWord, StopWord
from django.http import HttpResponseRedirect
# from postmarkup import render_bbcode
from lxml import html
from django.core.cache import cache
from django.views.decorators.cache import cache_page

import os
import csv
from django.db.models import Q
from django.http import StreamingHttpResponse
import time
import Sift.clustering
import Sift.Notification

from Sift.tasks import cluster_posts_with_input, create_new_clusters
import Sift.forms
from Sift.models import *
from Sift.forms import StopwordDelete, StopwordAdd


@cache_page(60 * 60)
def general(request):
    headline = "General Analytics"
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    pieData = [['Forum ID', 'Number of Posts']]
    for cluster in trendingClusters:
        pieData.append(
            [cluster.name,
             Post.objects.filter(cluster=cluster.clusterid).count()])

    sentimentData = [['Group', 'Negative', 'Neutral', 'Positive']]
    s_neg = Post.objects.filter(sentiment="neg").count()
    s_neutral = Post.objects.filter(sentiment="neutral").count()
    s_pos = Post.objects.filter(sentiment="pos").count()
    s_all = s_neg + s_neutral + s_pos
    sentimentData.append(["All Posts", round((s_neg / s_all) * 100, 2), round((s_neutral / s_all) * 100, 2),
                          round((s_pos / s_all) * 100, 2)])

    # Calculate sentiment data for each cluster
    for cluster in trendingClusters:
        s_neg = Post.objects.filter(cluster=cluster.clusterid, sentiment="neg").count()
        s_neutral = Post.objects.filter(cluster=cluster.clusterid, sentiment="neutral").count()
        s_pos = Post.objects.filter(cluster=cluster.clusterid, sentiment="pos").count()
        s_all = s_neg + s_neutral + s_pos
        sentimentData.append([cluster.name, round((s_neg / s_all) * 100, 2), round((s_neutral / s_all) * 100, 2),
                              round((s_pos / s_all) * 100, 2)])

    lineClusterNames = []

    for cluster in trendingClusters:
        lineClusterNames.append(cluster.name)

    lineDates = []
    lineData = {}
    posts = Post.objects.values(
        'creation_date', 'cluster').order_by('creation_date')
    for post in posts:
        id = post["cluster"]
        if (id is not None):
            date = int(time.mktime(post["creation_date"].timetuple())) * 1000
            try:
                if date in lineData:
                    lineData[date][id - 1] += 1
                else:
                    lineData[date] = [0] * len(lineClusterNames)
                    lineData[date][id - 1] = 1
                    lineDates.append(date)
            except:
                pass

    context = {'pinnedClusters': pinnedClusters, 'trendingClusters':
        trendingClusters, "headline": headline,
               'pieData': pieData,
               'lineData': lineData, 'lineDates': lineDates,
               'lineClusterNames': lineClusterNames,
               'sentimentData': sentimentData}

    return render(request, 'general_analytics.html', context)


@cache_page(60 * 60)
def details(request, cluster_id):
    headline = "Topic Analytics"
    cluster = get_object_or_404(Cluster, pk=cluster_id)
    trendingClusters = Cluster.objects.filter(ispinned=0)
    pinnedClusters = Cluster.objects.filter(ispinned=1)

    # data
    cluster_posts = {}
    posts = Post.objects.values(
        'creation_date', 'sentiment', 'body').filter(cluster=cluster_id)
    for post in posts:
        date = int(time.mktime(post["creation_date"].timetuple())) * 1000
        if date in cluster_posts:
            cluster_posts[date]['numPosts'] += 1
        else:
            cluster_posts[date] = {
                "numPosts": 1, "posts": [], "sentiments": []}
        try:
            body = html.document_fromstring(post['body']).text_content()
        except:
            body = post['body']
        cluster_posts[date]['posts'].append(body)

        # Add sentiment
        if post['sentiment'] is None:
            cluster_posts[date]['sentiments'].append('null')
        else:
            cluster_posts[date]['sentiments'].append(post['sentiment'])

    # Cluster word count
    wordPieData = [['Word', 'Instances']]

    words = ClusterWord.objects.filter(clusterid=cluster_id)[:10]
    for w in words:
        wordPieData.append([w.word, w.count])

    # Sentiment Data
    sentimentData = [['Group', 'Negative', 'Neutral', 'Positive']]
    s_neg = Post.objects.filter(cluster=cluster_id, sentiment="neg").count()
    s_neutral = Post.objects.filter(cluster=cluster_id, sentiment="neutral").count()
    s_pos = Post.objects.filter(cluster=cluster_id, sentiment="pos").count()
    s_all = s_neg + s_neutral + s_pos
    sentimentData.append(["All Posts", round((s_neg / s_all) * 100, 2), round((s_neutral / s_all) * 100, 2),
                          round((s_pos / s_all) * 100, 2)])

    context = {'pinnedClusters': pinnedClusters,
               'trendingClusters': trendingClusters, "headline": headline,
               'cluster': cluster, 'cluster_posts': cluster_posts,
               'wordPieData': wordPieData, 'sentimentData': sentimentData}

    return render(request, 'details.html', context)


def notifications(request):
    headline = "Notifications"

    nightly_list = Sift.Notification.get_nightly_list()
    important_list = Sift.Notification.get_important_list()
    email_list = Sift.Notification.email_verify()

    context = {"headline": headline, 'nightly_list': nightly_list, 'important_list': important_list,
               'email_list': email_list}
    if request.method == 'POST':
        if 'ADD_EMAIL' in request.POST:
            Sift.Notification.add_email(request.POST['ADD_EMAIL'])
        elif 'Remove' in request.POST:
            Sift.Notification.remove(request.POST.get('email'))
            return HttpResponseRedirect('/notifications')

    return render(request, 'notifications.html', context)


def clusters(request):
    headline = "Clusters"
    clusters = Cluster.objects.all()

    top_words = {}
    for cluster in clusters:
        words = ClusterWord.objects.filter(clusterid=cluster.clusterid)
        for word in words:
            if (cluster.name, cluster.clusterid) in top_words:
                top_words[(cluster.name, cluster.clusterid)].append((word.word, word.count))
            else:
                top_words[(cluster.name, cluster.clusterid)] = [(word.word, word.count)]

    context = {"headline": headline, 'clusters': clusters,
               'top_words': top_words.items()}

    if request.method == 'POST':
        # edit the name of the cluster.
        cluster_names = request.POST.items()
        for key, value in cluster_names:
            if value == "on":
                # check to make sure the stop word isn't currently in the list
                if StopWord.objects.filter(word=key).__len__() is 0:
                    StopWord(word=key).save()
            elif key != "csrfmiddlewaretoken":
                if value != "" or value:
                    print("updating cluster ", value)
                    c = Cluster.objects.get(clusterid=key)
                    c.name = value
                    c.save()

    return render(request, 'clusters.html', context)


def clustering(request):
    deleteThese = ""
    if request.method == 'POST':
        clusterForm = Sift.forms.ClusterForm(request.POST)

        if clusterForm.is_valid():
            if clusterForm.cleaned_data['cluster_type'] == 1:
                is_mini_batched = False
            else:
                is_mini_batched = True
            if clusterForm.cleaned_data['all_posts'] == 1:
                is_all_posts = True
            else:
                is_all_posts = False
            if clusterForm.cleaned_data['is_creation_clustering'] == 1:
                is_creation_clustering = True
            else:
                is_creation_clustering = False

            if is_creation_clustering:
                create_new_clusters.delay(
                    int(clusterForm.cleaned_data['num_clusters']),
                    int(clusterForm.cleaned_data['max_features']))
            else:
                cluster_posts_with_input.delay(
                    str(clusterForm.cleaned_data['start_date']),
                    str(clusterForm.cleaned_data['end_date']),
                    int(clusterForm.cleaned_data['num_clusters']),
                    int(clusterForm.cleaned_data['max_features']),
                    is_mini_batched, is_all_posts)
    if request.method == "POST" and not clusterForm.is_valid():
        stopwordDelete = StopwordDelete(request.POST)
        if stopwordDelete.is_valid():
            deleteThese = stopwordDelete.cleaned_data['word']
            for element in deleteThese:
                StopWord.objects.filter(word=element).delete()

    addStopWord = request.method == "POST" and not clusterForm.is_valid()
    addStopWord = addStopWord and not stopwordDelete.is_valid()
    if addStopWord:
        stopwordAdd = StopwordAdd(request.POST)
        if stopwordAdd.is_valid():
            addThis = stopwordAdd.cleaned_data['add_word']
            # check to make sure the stop word isn't currently in the list
            if StopWord.objects.filter(word=addThis).__len__() is 0:
                StopWord(word=addThis).save()

    form = Sift.forms.ClusterForm()
    headline = "Clustering"

    stopwords = StopWord.objects.all().values_list("word", flat=True)
    runclustering = ClusterRun.objects.all()

    for clusterrun in runclustering:
        clusterrun.run_date = int(
            time.mktime(clusterrun.run_date.timetuple())) * 1000
        clusterrun.start_date = int(
            time.mktime(clusterrun.start_date.timetuple())) * 1000
        clusterrun.end_date = int(
            time.mktime(clusterrun.end_date.timetuple())) * 1000
        if clusterrun.silo_score is None:
            clusterrun.silo_score = 'null'

    context = {'headline': headline, 'form': form, 'stopwords': stopwords,
               'deleteForm': StopwordDelete(), 'addForm': StopwordAdd(),
               'runclustering': runclustering}
    return render(request, 'clustering.html', context)


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def exportdata(request):
    if request.method == 'POST':
        exportData = Sift.forms.ExportData(request.POST)

        if exportData.is_valid():
            if exportData.cleaned_data['all_posts'] == 1:
                is_all_posts = True
            else:
                is_all_posts = False

            start_date = exportData.cleaned_data['start_date']
            end_date = exportData.cleaned_data['end_date']

            if is_all_posts:
                data = Post.objects.all()[:1000]
                # data = Post.objects.filter(Q(sentiment="pos")|Q(sentiment="neg")|Q(sentiment="neutral"))[:1000]
            else:
                data = Post.objects.filter(creation_date__range=(start_date, end_date))[:1000]

            # Generate a sequence of rows. The range is based on the maximum number of
            # rows that can be handled by a single sheet in most spreadsheet
            # applications.
            rows = ([post.post_id, post.thread_id, post.message_id,
                     post.forum_id, post.user_id, post.category_id,
                     post.subject, post.body, post.username, post.creation_date,
                     post.modification_date, post.stemmed_body, post.probpositive,
                     post.probneutral, post.probnegative, post.sentiment]
                    for post in data)

            pseudo_buffer = Echo()
            writer = csv.writer(pseudo_buffer)
            response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                             content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename="sift.csv"'

            return response

    form = Sift.forms.ExportData()
    headline = "Export Data"

    context = {'headline': headline, 'form': form}
    return render(request, 'exportdata.html', context)