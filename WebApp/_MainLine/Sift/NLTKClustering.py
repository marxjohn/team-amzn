# K-means clustering of seller forums posts
__author__ = 'Ben'

# This looks like it's for 2-to-3 compatibility as well?
# Yupp, no mysql in python 3 so some trickery is needed
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
            'HOST': 'sellerforums.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
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

from models import Post
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
import logging
from optparse import OptionParser
from time import time
import numpy as np
from pprint import pprint


IS_MINI_USED = False
IS_IDF_USED = True
NUM_CLUSTERS = 50

class ClusterData:
    '''Represents a group of posts as a numpy array of strings,
    as well as providing functionality to tokenize posts'''
    # Seller-forums specific stopwords
    REMOVE_LIST = set([
        "br", "title", "quote", "just", "amazon",
        "seller", "shipping", "buyer", "sellers", "new",
        "item", "customer", "account", "re", "quotetitle"
    ])
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

    def __init__(self, inp):
        self.data = np.array(list(map(str, inp)))


def print_posts_in_cluster(data_count, dataset, km, num_posts, num_clusters):
    # Associate posts with created clusters
    posts_in_cluster = []

    for x in range(0, num_clusters):
        posts_in_cluster.append([])

    for i in range(0, data_count - 1):
        x = km.labels_[i]
        posts_in_cluster[x].append(dataset.data[i])

    for x in range(0, num_clusters):
        size_of_cluster = len(posts_in_cluster[x])
        print('\n' + '=' * 150 + "\n\tPosts in Cluster " + x.__str__() +
              '\tSize: ' + size_of_cluster.__str__()+ '\n' + '=' * 150)

        if num_posts > size_of_cluster:
            num_printed_posts = size_of_cluster
        else:
            num_printed_posts = num_posts

        for z in range(0, num_printed_posts):
            print('\n' + posts_in_cluster[x][z])


def fit_clusters(X):
    if IS_MINI_USED:
        # n_clusters:   Number of clusters created
        # init:         Method of cluster mean initialization
        # n_init:       Number of random initializations that are tried
        # init_size:    Number of samples to randomly sample to speed up initialization
        # batch_size:   Size of the mini batches
        km = MiniBatchKMeans(n_clusters=NUM_CLUSTERS, init='k-means++', n_init=5,
                             init_size=300, batch_size=100, verbose=False)
    else:
        # n_cluster:    Number of clusters created
        # init:         method of initialization
        # max_iter:     Number of iterations of k-means in a single run
        # n_init        Number of times the k-means algorithm will be run, best result chosen (important)
        km = KMeans(n_clusters=NUM_CLUSTERS, init='k-means++', max_iter=300, n_init=10,
                    verbose=False)
    print("Clustering sparse data with %s" % km)
    t0 = time()
    km.fit(X)
    print("done in %0.3fs" % (time() - t0))
    print()
    return km


def print_cluster_centroids(km, vectorizer):
    print("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    for i in range(NUM_CLUSTERS):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
        print()


def vectorize_data(dataset):
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
                                 min_df=2, stop_words='english',
                                 use_idf=IS_IDF_USED, tokenizer=ClusterData.tokenize_post)
    vectorized_data = vectorizer.fit_transform(dataset.data)
    return vectorized_data, vectorizer


def main():
    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')


    print("Retrieving dataset from database")
    t0 = time()

    dataset = ClusterData(Post.objects.all())
    data_count = len(dataset.data)

    print("done in %fs" % (time() - t0))

    print("Extracting features from the training dataset using a sparse vectorizer")
    t0 = time()

    vectorized_data, vectorizer = vectorize_data(dataset)

    print("done in %fs" % (time() - t0))
    print("n_samples: %d, n_features: %d" % vectorized_data.shape)
    print()

    ##########################################################################
    # Do the actual clustering

    km = fit_clusters(vectorized_data)

    print_cluster_centroids(km, vectorizer)

    print_posts_in_cluster(data_count, dataset, km, 5, NUM_CLUSTERS)


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
