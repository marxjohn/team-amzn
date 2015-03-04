from __future__ import absolute_import
# K-means clustering of seller forums posts

import os
try:
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Sift/stopwords.cfg')) as f:
        REMOVE_LIST = set(f.read().split())
except:
    with open('/opt/sift-env/team-amzn/WebApp/Sift/stopwords.cfg') as f:
        REMOVE_LIST = set(f.read().split())



# K-means clustering of seller forums posts


MAX_FEATURES = 1000
IS_MINI_USED = True
IS_IDF_USED = True
IS_HASHING_VECTORIZER_USED = False
IS_UPLOAD_ENABLED = True
NUM_CLUSTERS = 6
IS_NLTK_USED = False
IS_VISUALIZATION_ENABLED = False

__author__ = 'cse498'

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except:
    pass

from django.conf import settings
if not settings.configured:
    settings.configure(
        DATABASES={'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': 'restorestemmedbody.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
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

import matplotlib.pyplot as plt

try:
    from models import Post, Cluster, ClusterWord
except:
    from Sift.models import Post, Cluster, ClusterWord

from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer

from sklearn.cluster import KMeans, MiniBatchKMeans
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
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

from django.core.cache import cache
STOP_WORDS = list(REMOVE_LIST.union(stopwords.words('english')))
django.setup()


import Stemmer
english_stemmer = Stemmer.Stemmer('en')


class StemmedTfidfVectorizer(TfidfVectorizer):

    def build_analyzer(self):
        analyzer = super(TfidfVectorizer, self).build_analyzer()

        def analyze(doc):
            if doc[1]:
                temp = ' '.join([i for i in doc[0].split(' ') if i not in STOP_WORDS]).split(' ')
                temp2 = list(filter(''.__ne__, temp))
                return temp2
            else:
                stemmed = english_stemmer.stemWords(analyzer(doc[0]))
                post = Post.objects.get(postid=doc[2])
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
        keep = lambda word: not word in ClusterData.STOPWORDS
        tokenized = filter(keep, word_tokenize(post))
        stemmed = set(map(ClusterData.stemmer.lemmatize, tokenized))
        return stemmed

    def stemmed_body(post):
        if post.stemmedbody is not None:
            return (post.stemmedbody, True, post.postid)
        else:
            return (post.body, False, post.postid)

    def __init__(self, inp):
        self.id_list = [p.postid for p in inp]
        self.data = np.fromiter(
            map(ClusterData.stemmed_body, inp),
            dtype=[("body", "|U5000"), ("stemmed", "b"), ("id", "i")],
            count=len(inp))


def print_posts_in_cluster(data_count, dataset, km, num_posts, num_clusters):
    # Associate posts with created clusters
    posts_in_cluster = []

    for x in range(0, num_clusters):
        posts_in_cluster.append([])

    for i in range(0, data_count - 1):
        x = km.labels_[i]
        posts_in_cluster[x].append(dataset.data[i][0])

    for x in range(0, num_clusters):
        size_of_cluster = len(posts_in_cluster[x])
        print('\n' + '=' * 150 + "\n\tSample Posts in Cluster " + str(x) +
              '\tSize: ' + str(size_of_cluster) + '\n' + '=' * 150)

        if num_posts > size_of_cluster:
            num_printed_posts = size_of_cluster
        else:
            num_printed_posts = num_posts

        for z in range(0, num_printed_posts):
            print('\n' + posts_in_cluster[x][z])


def fit_clusters(X, num_clusters):
    if IS_MINI_USED:
        # n_clusters:   Number of clusters created
        # init:         Method of cluster mean initialization
        # n_init:       Number of random initializations that are tried
        # init_size:    Number of samples to randomly sample to speed up initialization
        # batch_size:   Size of the mini batches
        km = MiniBatchKMeans(n_clusters=num_clusters, init='k-means++', n_init=5,
                             init_size=3000, batch_size=1000, verbose=False)
    else:
        # n_cluster:    Number of clusters created
        # init:         method of initialization
        # max_iter:     Number of iterations of k-means in a single run
        # n_init        Number of times the k-means algorithm will be run, best
        # result chosen (important)
        km = KMeans(n_clusters=num_clusters, init='k-means++', max_iter=300, n_init=10, n_jobs=-1,
                    verbose=False)
    print("Clustering sparse data with %s" % km)
    t0 = time()
    km.fit(X)
    print("done in %0.3fs" % (time() - t0))
    print()
    return km


def print_cluster_centroids(km, vectorizer, num_clusters):
    print("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    for i in range(num_clusters):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
        print()


def vectorize_data(dataset, max_features):
    vectorizer = StemmedTfidfVectorizer(max_df=.8, max_features=max_features,
                                        min_df=1,
                                        use_idf=IS_IDF_USED, analyzer='word', ngram_range=(1, 1))


    vectorized_data = vectorizer.fit_transform(dataset.data)

    return vectorized_data, vectorizer


def cluster_posts(dataset, t0, num_clusters, max_features):
    data_count = len(dataset.data)
    print("done in %fs" % (time() - t0))
    print(
        "Extracting features from the training dataset using a sparse vectorizer")
    t0 = time()
    vectorized_data, vectorizer = vectorize_data(dataset, max_features)
    print("done in %fs" % (time() - t0))
    print("n_samples: %d, n_features: %d" % vectorized_data.shape)
    print()
    ##########################################################################
    # Do the actual clustering
    t0 = time()
    km = fit_clusters(vectorized_data, num_clusters)
    t_mini_batch = time() - t0

    if not IS_HASHING_VECTORIZER_USED:

        print_cluster_centroids(km, vectorizer, num_clusters)
        print_posts_in_cluster(data_count, dataset, km, 5, num_clusters)
    # Create Clusters to upload to database
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()

    if IS_UPLOAD_ENABLED:
        upload_clusters(dataset, data_count, km, order_centroids, terms, num_clusters)

    if IS_VISUALIZATION_ENABLED:
        reduced_data = PCA(n_components=2).fit_transform(vectorized_data.toarray())
        kmeans = MiniBatchKMeans(n_clusters=num_clusters, init='k-means++', n_init=5,
                             init_size=3000, batch_size=1000, verbose=False)
        kmeans.fit(reduced_data)

        # Step size of the mesh. Decrease to increase the quality of the VQ.
        h = .001     # point in the mesh [x_min, m_max]x[y_min, y_max].

        # Plot the decision boundary. For that, we will assign a color to each
        x_min, x_max = reduced_data[:, 0].min() + 1, reduced_data[:, 0].max() - 1
        y_min, y_max = reduced_data[:, 1].min() + 1, reduced_data[:, 1].max() - 1
        xx, yy = np.meshgrid(np.arange(x_max, x_min, h), np.arange(y_max, y_min, h))

        # Obtain labels for each point in mesh. Use last trained model.
        Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

        # Put the result into a color plot
        Z = Z.reshape(xx.shape)
        plt.figure(1)
        plt.clf()
        plt.imshow(Z, interpolation='nearest',
                   extent=(xx.min(), xx.max(), yy.min(), yy.max()),
                   cmap=plt.cm.Paired,
                   aspect='auto', origin='lower')

        rand_smpl0 = [reduced_data[i][0] for i in random.sample(range(len(reduced_data)), 20000)]
        rand_smpl1 = [reduced_data[i][1] for i in random.sample(range(len(reduced_data)), 20000)]

        plt.plot(rand_smpl0[:], rand_smpl1[:], 'k.', markersize=2)
        # Plot the centroids as a white X
        centroids = kmeans.cluster_centers_
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
        print_cluster_centroids(kmeans, vectorizer, num_clusters)


def upload_clusters(dataset, data_count, km, order_centroids, terms, num_clusters):
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
            query = "UPDATE posts SET posts.cluster = " + str(j+1) + " where"
            is_first = True
            count = 0
            for i in range(0, data_count):
                x = km.labels_[i] + 1
                post_id = dataset.id_list[i]
                if x == j + 1:
                    # increment count if post is part of query
                    count += 1
                    if is_first:
                        query += " posts.postId = " + str(post_id)
                        is_first = False
                    else:
                        query += " OR posts.postId = " + str(post_id)

                if count >= 7500:
                    print("uploading part of cluster " + str(j))
                    cursor = connection.cursor()
                    cursor.execute(query)
                    cursor.close()
                    query = "UPDATE posts SET posts.cluster = " + str(j+1) + " where"
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
            cwL = []
            for ind in order_centroids[x - 1, :10]:
                count = len(Post.objects.filter(cluster=c, stemmedbody__contains=terms[ind]))

                cw = ClusterWord(word=terms[ind], clusterid=c, count=count)
                cwL.append(cw)

            cwL = sorted(cwL, key=attrgetter('count'), reverse=True)
            ClusterWord.objects.bulk_create(cwL)

        # ClusterWord.objects.bulk_create(cwList)

        print("Completed date upload in " + str((time() - t0)) + " seconds.")


def main():
        # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    print("Retrieving dataset from database")
    t0 = time()

    dataset = ClusterData(

    Post.objects.filter(creationdate__range=("2012-01-01", "2015-01-01")))


    cluster_posts(dataset, t0, NUM_CLUSTERS, MAX_FEATURES)

# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
