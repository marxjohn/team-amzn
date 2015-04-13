import os
from django.conf import settings
import pymysql
import matplotlib.pyplot as plt
from Sift.models import Post, Cluster, ClusterWord, ClusterRun, StopWord
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.preprocessing import Normalizer
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.metrics import silhouette_score
import re
import random
import logging
from operator import attrgetter
from django.db import connection
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from time import time
import numpy as np
import django
from datetime import datetime
import Stemmer
pymysql.install_as_MySQLdb()
if not settings.configured:
    settings.configure(
        DATABASES={'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': 'siftmsu.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
            'PORT': '3306',
            'USER': 'teamamzn',
            'PASSWORD': 'TeamAmazon2015!',
            'NAME': 'sellerforums',
            'OPTIONS': {
                'autocommit': True,
            },
        }
        }
    )
# K-means clustering of seller forums posts
# MAX_FEATURES = 1000
# IS_MINI_USED = True
# IS_IDF_USED = True
#
# IS_UPLOAD_ENABLED = False
# NUM_CLUSTERS = 5
# IS_NLTK_USED = False
# IS_VISUALIZATION_ENABLED = False
# IS_ADDED_TO_CLUSTER_RUN = True
# MAX_DF = .85
# BATCH_SIZE_RATIO = 10
# INIT_SIZE_RATIO = 20
# N_INIT = 150

django.setup()
REMOVE_LIST = set(StopWord.objects.all().values_list("word", flat=True))
STOP_WORDS = list(REMOVE_LIST.union(stopwords.words('english')))

english_stemmer = Stemmer.Stemmer('en')


class ClusterParameter:

    def __init__(self, max_features, is_idf_used, is_upload_enabled,
                 num_clusters, is_mini_used, max_df, batch_size_ratio,
                 init_size_ratio, n_init,
                 start_date, end_date, is_visualization_enabled):

        self.max_features = max_features
        self.is_idf_used = is_idf_used
        self.is_upload_enabled = is_upload_enabled
        self.num_clusters = num_clusters
        self.max_df = max_df
        self.batch_size_ratio = batch_size_ratio
        self.init_size_ratio = init_size_ratio
        self.n_init = n_init
        self.start_date = start_date
        self.end_date = end_date
        self.is_mini_used = is_mini_used
        self.is_visualization_enabled = is_visualization_enabled
        self.s_score = 0
        self.inertia = 0
        self.normalized_inertia = 0
        self.pdf_lines = []


class StemmedTfidfVectorizer(TfidfVectorizer):

    def build_analyzer(self):
        analyzer = super(TfidfVectorizer, self).build_analyzer()

        def analyze(doc):
            if doc[1]:
                temp = ' '.join(
                    [i for i in doc[0].split(' ') if i not in STOP_WORDS]
                ).split(' ')
                temp2 = list(filter(''.__ne__, temp))
                return temp2
            else:
                stemmed = english_stemmer.stemWords(analyzer(doc[0]))
                post = Post.objects.get(post_id=doc[2])
                post.stemmedbody = ' '.join(stemmed)
                post.save()
                return stemmed
        return analyze


class ClusterData:

    '''Represents a group of posts as a numpy array of strings,
    as well as providing functionality to tokenize posts'''
    # Seller-forums specific stopwords
    # Add general english stopwords
    STOPWORDS = REMOVE_LIST.union(stopwords.words('english'))
    stemmer = WordNetLemmatizer()
    exp = re.compile(r'[^\w^\s]+', re.UNICODE | re.IGNORECASE)

    def tokenize_post(post):
        '''Consumes a post from the seller forums and returns the
        tokenized, stemmed version'''
        post = ClusterData.exp.sub('', post).lower()
        tokenized = filter(lambda word: word not in ClusterData.STOPWORDS,
                           word_tokenize(post))
        stemmed = set(map(ClusterData.stemmer.lemmatize, tokenized))
        return stemmed

    def stemmed_body(post):
        if post.stemmed_body is not None:
            return (post.stemmed_body, True, post.post_id)
        else:
            return (post.body, False, post.post_id)

    def __init__(self, inp):
        self.id_list = [p.post_id for p in inp]
        self.data = np.fromiter(
            map(ClusterData.stemmed_body, inp),
            dtype=[("body", "|U5000"), ("stemmed", "b"), ("id", "i")],
            count=inp.count())


def print_posts_in_cluster(data_count, data_set, km, num_posts, c_param):
    # Associate posts with created clusters
    posts_in_cluster = []

    for x in range(0, c_param.num_clusters):
        posts_in_cluster.append([])

    for i in range(0, data_count - 1):
        x = km.labels_[i]
        posts_in_cluster[x].append(data_set.data[i][0])

    for x in range(0, c_param.num_clusters):
        size_of_cluster = len(posts_in_cluster[x])
        print('\n' + '=' * 150 + "\n\tSample Posts in Cluster " + str(x) +
              '\tSize: ' + str(size_of_cluster) + '\n' + '=' * 150)

        c_param.pdf_lines.append('=' * 150 + "\n\tSample Posts in Cluster " + str(x) +
              '\tSize: ' + str(size_of_cluster) + '\n' + '=' * 150)

        if num_posts > size_of_cluster:
            num_printed_posts = size_of_cluster
        else:
            num_printed_posts = num_posts

        for z in range(0, num_printed_posts):
            print('\n' + posts_in_cluster[x][z])
            c_param.pdf_lines.append(posts_in_cluster[x][z])


def fit_clusters(X, c_param):
    if c_param.is_mini_used:
        # n_clusters:   Number of clusters created
        # init:         Method of cluster mean initialization
        # n_init:       Number of random initializations that are tried
        # init_size:    Number of samples to randomly sample
        # batch_size:   Size of the mini batches
        km = MiniBatchKMeans(n_clusters=c_param.num_clusters,
                             init='k-means++', n_init=c_param.n_init,
                             init_size=int(
                                 len(X.data) / c_param.init_size_ratio),
                             batch_size=int(
                                 len(X.data) / c_param.batch_size_ratio),
                             verbose=False)
    else:
        # n_cluster:    Number of clusters created
        # init:         method of initialization
        # max_iter:     Number of iterations of k-means in a single run
        # n_init        Number of times the k-means algorithm will be run, best
        # result chosen (important)
        km = KMeans(n_clusters=c_param.num_clusters, init='k-means++',
                    max_iter=300, n_init=10, n_jobs=-1, verbose=False)
    print("Clustering sparse data with %s" % km)
    t0 = time()
    km.fit(X)
    labels = km.labels_
    print('done with clustering, calculating silhouette score')
    #s_score = silhouette_score(
     #   X, labels, metric='euclidean', sample_size=25000)
    s_score = 0
    print(s_score)
    print()
    return km, s_score


def print_cluster_centroids(km, vectorizer, c_param):
    print("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    for i in range(c_param.num_clusters):
        print("Cluster %d:" % i, end='')
        c_param.pdf_lines.append("Cluster %d:" % i)

        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
            c_param.pdf_lines.append(' %s' % terms[ind])
        print()

    print("Total Inertia")
    print(km.inertia_)
    c_param.pdf_lines.append("Total Inertia: " + km.inertia_.__str__())
    print("Normalized Inertia")
    print(km.inertia_ / len(km.labels_))
    c_param.pdf_lines.append("Normalized Inertia: " + (km.inertia_ / len(km.labels_)).__str__())


def vectorize_data(data_set, c_param):
    vectorizer = StemmedTfidfVectorizer(max_df=c_param.max_df,
                                        max_features=c_param.max_features,
                                        min_df=1,
                                        use_idf=c_param.is_idf_used,
                                        analyzer='word',
                                        ngram_range=(1, 1))

    vectorized_data = vectorizer.fit_transform(data_set.data)

    return vectorized_data, vectorizer


def visualize_clusters(num_clusters, vectorized_data, vectorizer):
    reduced_data = PCA(n_components=2).fit_transform(
        vectorized_data.toarray())  # .toarray())
    k_means = MiniBatchKMeans(n_clusters=num_clusters, init='k-means++',
                              n_init=N_INIT, init_size=INIT_SIZE_RATIO,
                              batch_size=BATCH_SIZE_RATIO, verbose=True)
    k_means.fit(reduced_data)
    # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .001  # point in the mesh [x_min, m_max]x[y_min, y_max].
    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() + 1, reduced_data[:, 0].max() - 1
    y_min, y_max = reduced_data[:, 1].min() + 1, reduced_data[:, 1].max() - 1
    xx, yy = np.meshgrid(
        np.arange(x_max, x_min, h), np.arange(y_max, y_min, h))
    # Obtain labels for each point in mesh. Use last trained model.
    Z = k_means.predict(np.c_[xx.ravel(), yy.ravel()])
    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1)
    plt.clf()
    plt.imshow(Z, interpolation='nearest',
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')
    rand_smpl0 = [reduced_data[i][0]
                  for i in random.sample(range(len(reduced_data)), 20000)]
    rand_smpl1 = [reduced_data[i][1]
                  for i in random.sample(range(len(reduced_data)), 20000)]
    plt.plot(rand_smpl0[:], rand_smpl1[:], 'k.', markersize=2)
    # Plot the centroids as a white X
    centroids = k_means.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1],
                marker='x', s=169, linewidths=3,
                color='w', zorder=10)
    plt.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
              'Centroids are marked with white cross')
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    plt.show()
    print_cluster_centroids(k_means, vectorizer, num_clusters)


def cluster_posts(data_set, c_param):
    data_count = len(data_set.data)
    print(
        "Extracting features from the training dataset\
                using a sparse vectorizer")
    vectorized_data, vectorizer = vectorize_data(data_set, c_param)
    # svd = TruncatedSVD(n_components = 100)
    # lsa = make_pipeline(svd, Normalizer(copy=False))
    # vectorized_data = lsa.fit_transform(vectorized_data)
    print("n_samples: %d, n_features: %d" % vectorized_data.shape)
    print()
    ##########################################################################
    # Do the actual clustering
    km, c_param.s_score = fit_clusters(vectorized_data, c_param)

    print_cluster_centroids(km, vectorizer, c_param)
    print_posts_in_cluster(data_count, data_set, km, 5, c_param)
    # Create Clusters to upload to database
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()

    if c_param.is_upload_enabled:
        upload_clusters(
            data_set, data_count, km, order_centroids, terms,
            c_param.num_clusters)

    if c_param.is_visualization_enabled:
        visualize_clusters(c_param.num_clusters, vectorized_data, vectorizer)

    return create_cluster_run(km, c_param)


def upload_clusters(data_set, data_count, km, order_centroids,
                    terms, num_clusters):
    t0 = time()
    print("Uploading Clusters")

    clusterList = []
    for x in range(1, num_clusters + 1):
        temp_name = ""
        for ind in order_centroids[x - 1, :3]:
            temp_name = temp_name + ' ' + terms[ind]
        c = Cluster(name=temp_name, clusterid=x, ispinned=False)
        clusterList.append(c)

    print("Clearing Data")
    # Clear data about to be updated
    Cluster.objects.filter(ispinned=0).delete()
    ClusterWord.objects.filter().delete()

    # After clearing bulk create the new cluster list
    Cluster.objects.bulk_create(clusterList)

    # Associate Post with Cluster
    # do for every 5k
    for j in range(0, num_clusters):
        query = "UPDATE Post SET Post.cluster = " + str(j + 1) + " where"
        is_first = True
        count = 0
        for i in range(0, data_count):
            x = km.labels_[i] + 1
            post_id = data_set.id_list[i]
            if x == j + 1:
                # increment count if post is part of query
                count += 1
                if is_first:
                    query += " Post.postId = " + str(post_id)
                    is_first = False
                else:
                    query += " OR Post.postId = " + str(post_id)

            if count >= 7500:
                print("uploading part of cluster " + str(j))
                cursor = connection.cursor()
                cursor.execute(query)
                cursor.close()
                query = "UPDATE Post SET Post.cluster = " + \
                    str(j + 1) + " where"
                is_first = True
                count = 0

        print("Uploading Cluster: " + str(j))
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()

    print("Counting Cluster Words")
    # cwList = []
    for x in range(1, num_clusters + 1):
        c = Cluster.objects.get(clusterid=x)
        cluster_words = []

        if len(order_centroids[x-1]) < 100:
            num_centroids = len(order_centroids[x-1])
        else:
            num_centroids = 100


        # Save top 100 cluster words
        rank = 1
        for ind in order_centroids[x - 1, :num_centroids]:
            count = len(
                Post.objects.filter(cluster=c,
                                    stemmed_body__contains=terms[ind]))

            cw = ClusterWord(word=terms[ind], clusterid=c, count=count, rank=rank)
            cluster_words.append(cw)
            rank += 1

        cluster_words = sorted(cluster_words, key=attrgetter('count'), reverse=True)
        ClusterWord.objects.bulk_create(cluster_words)

    # ClusterWord.objects.bulk_create(cwList)

    print("Completed date upload in " + str((time() - t0)) + " seconds.")


def create_cluster_run(km, c_param):
    format = '%Y-%m-%d'
    c_param.normalized_inertia = km.inertia_ / len(km.labels_)
    start_datetime = c_param.start_date
    end_datetime = c_param.end_date

    cr = ClusterRun(start_date=start_datetime, end_date=end_datetime,
                    normalized_inertia=c_param.normalized_inertia,
                    run_date=datetime.today(), n_init=c_param.n_init,
                    num_features=c_param.max_features,
                    num_clusters=c_param.num_clusters, batch_size=int(
                        len(km.labels_) / c_param.batch_size_ratio),
                    sample_size=int(len(km.labels_) / c_param.init_size_ratio),
                    max_df=c_param.max_df,
                    num_posts=len(km.labels_), total_inertia=km.inertia_,
                    batch_size_ratio=1 / c_param.batch_size_ratio,
                    sample_size_ratio=1 / c_param.init_size_ratio,
                    silo_score=c_param.s_score, is_creation_run=c_param.is_upload_enabled)
    cr.save()
    # Django trickery with getting the id of the model (probably should be changed somehow)
    # But it works....
    cr_with_id = ClusterRun.objects.get(run_date=cr.run_date)
    cr_with_id.data_dump_url = "https://s3-us-west-2.amazonaws.com/cluster-runs/" + cr_with_id.id.__str__()
    cr_with_id.save()
    return cr_with_id


def run_diagnostic_clustering(data_set, start_date, end_date, max_features,
                              num_clusters, max_df, batch_size_ratio,
                              init_size_ratio, n_init):

    c_param = ClusterParameter(num_clusters=num_clusters,
                               batch_size_ratio=batch_size_ratio,
                               is_idf_used=True, is_upload_enabled=False,
                               max_features=max_features, max_df=max_df,
                               init_size_ratio=init_size_ratio, n_init=n_init,
                               start_date=start_date, end_date=end_date,
                               is_mini_used=True,
                               is_visualization_enabled=False)

    cluster_run = cluster_posts(data_set, c_param)
    return cluster_run, c_param.pdf_lines


def run_creation_clustering(data_set, start_date, end_date, max_features,
                            num_clusters, max_df, batch_size_ratio,
                            init_size_ratio, n_init):

    c_param = ClusterParameter(num_clusters=num_clusters,
                               batch_size_ratio=batch_size_ratio,
                               is_idf_used=True, is_upload_enabled=True,
                               max_features=max_features, max_df=max_df,
                               init_size_ratio=init_size_ratio,
                               n_init=n_init, start_date=start_date,
                               end_date=end_date, is_mini_used=True,
                               is_visualization_enabled=False)

    return cluster_posts(data_set, c_param)
