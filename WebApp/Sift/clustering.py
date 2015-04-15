import random
from operator import attrgetter
from time import time
from datetime import datetime
import Stemmer

from django.conf import settings
import pymysql
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans
from nltk.corpus import stopwords
from sklearn.metrics import silhouette_score
from django.db import connection
from sklearn.decomposition import PCA
import numpy as np
import django

from Sift.models import Post, Cluster, ClusterWord, ClusterRun, StopWord
from Sift.scikit_utilities import StemmedTfidfVectorizer


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


def _print_posts_in_cluster(data_count, data_set, km, num_posts, c_param):
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


def _fit_clusters(vectorized_data, c_param):
    # n_clusters:   Number of clusters created
    # init:         Method of cluster mean initialization
    # n_init:       Number of random initializations that are tried
    # init_size:    Number of samples to randomly sample
    # batch_size:   Size of the mini batches
    km = MiniBatchKMeans(n_clusters=c_param.num_clusters,
                         init='k-means++', n_init=c_param.n_init,
                         init_size=int(
                             len(vectorized_data.data) / c_param.init_size_ratio),
                         batch_size=int(
                             len(vectorized_data.data) / c_param.batch_size_ratio),
                         verbose=False)

    print("Clustering sparse data with %s" % km)
    km.fit(vectorized_data)
    labels = km.labels_

    print('done with clustering, calculating silhouette score')
    s_score = silhouette_score(vectorized_data, labels, metric='euclidean', sample_size=25000)

    print(s_score)
    print()
    return km, s_score


def _print_cluster_centroids(km, vectorizer, c_param):
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


def _vectorize_data(data_set, c_param):
    vectorizer = StemmedTfidfVectorizer(max_df=c_param.max_df,
                                        max_features=c_param.max_features,
                                        min_df=1,
                                        use_idf=c_param.is_idf_used,
                                        analyzer='word',
                                        ngram_range=(1, 1))

    vectorized_data = vectorizer.fit_transform(data_set.data)

    return vectorized_data, vectorizer


def _visualize_clusters(num_clusters, vectorized_data, vectorizer):
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
    _print_cluster_centroids(k_means, vectorizer, num_clusters)


def cluster_posts(data_set, c_param):
    data_count = len(data_set.data)
    print(
        "Extracting features from the training dataset\
                using a sparse vectorizer")
    vectorized_data, vectorizer = _vectorize_data(data_set, c_param)

    print("n_samples: %d, n_features: %d" % vectorized_data.shape)
    print()
    ##########################################################################
    # Do the actual clustering
    km, c_param.s_score = _fit_clusters(vectorized_data, c_param)

    _print_cluster_centroids(km, vectorizer, c_param)
    _print_posts_in_cluster(data_count, data_set, km, 5, c_param)

    # Create Clusters to upload to database
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()

    if c_param.is_upload_enabled:
        _upload_clusters(data_set, data_count, km, order_centroids, terms, c_param.num_clusters)

    if c_param.is_visualization_enabled:
        _visualize_clusters(c_param.num_clusters, vectorized_data, vectorizer)

    return _create_cluster_run(km, c_param)


def _upload_clusters(data_set, data_count, km, order_centroids,
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

        if len(order_centroids[x - 1]) < 100:
            num_centroids = len(order_centroids[x - 1])
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


def _create_cluster_run(km, c_param):
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
    print(str(cr.run_date))
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

    cluster_run = cluster_posts(data_set, c_param)
    return cluster_run, c_param.pdf_lines
