from __future__ import print_function

__author__ = 'Luke Pritchett'

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

from models import *
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans, MiniBatchKMeans
import re

import logging
from optparse import OptionParser

from time import time

import numpy as np


class ClusterData:
    target_names = 'test'
    target = 'test'
    # Create Data set, which is numpy array of strings which contain the forum posts
    def __init__(self, input):
        i = 0
        tempData = np.empty(len(input), dtype="S500")
        tempTarget = np.zeros(len(input))
        for post in input:
            try:
                temp_str = post.__str__()

                REMOVE_LIST = ["br", "title", "quote", "just", "amazon", "seller", "shipping", "buyer", "sellers", "new"
                    , "item", "customer", "account", "Re:"]

                remove = '|'.join(REMOVE_LIST)
                regex = re.compile(r'\b(' + remove + r')\b', flags=re.IGNORECASE)
                out = regex.sub("", temp_str)

                tempData[i] = out

                tempTarget[i] = 1
            except:
                tempData[i] = ''
                tempTarget[i] = 1
                pass
            i += 1

        self.data = tempData
        self.target_names = ['one', 'two']


# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# parse commandline arguments
op = OptionParser()
op.add_option("--lsa",
              dest="n_components", type="int",
              help="Preprocess documents with latent semantic analysis.")
op.add_option("--no-minibatch",
              action="store_false", dest="minibatch", default=True,
              help="Use ordinary k-means algorithm (in batch mode).")
op.add_option("--no-idf",
              action="store_false", dest="use_idf", default=True,
              help="Disable Inverse Document Frequency feature weighting.")
op.add_option("--use-hashing",
              action="store_true", default=False,
              help="Use a hashing feature vectorizer")
op.add_option("--n-features", type=int, default=10000,
              help="Maximum number of features (dimensions)"
                   " to extract from text.")
op.add_option("--verbose",
              action="store_true", dest="verbose", default=False,
              help="Print progress reports inside k-means algorithm.")

print(__doc__)
op.print_help()

(opts, args) = op.parse_args()

dataset = ClusterData(Post.objects.all())

for x in dataset.data:
    print(x)

labels = dataset.target
true_k = np.unique(labels).shape[0]
true_k = 20

print("Extracting features from the training dataset using a sparse vectorizer")
t0 = time()
if opts.use_hashing:
    if opts.use_idf:
        # Perform an IDF normalization on the output of HashingVectorizer
        hasher = HashingVectorizer(n_features=opts.n_features,
                                   stop_words='english', non_negative=True,
                                   norm=None, binary=False)
        vectorizer = make_pipeline(hasher, TfidfTransformer())
    else:
        vectorizer = HashingVectorizer(n_features=opts.n_features,
                                       stop_words='english',
                                       non_negative=False, norm='l2',
                                       binary=False)
else:
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=opts.n_features,
                                 min_df=2, stop_words='english',
                                 use_idf=opts.use_idf)
X = vectorizer.fit_transform(dataset.data)

print("done in %fs" % (time() - t0))
print("n_samples: %d, n_features: %d" % X.shape)
print()

if opts.n_components:
    print("Performing dimensionality reduction using LSA")
    t0 = time()
    # Vectorizer results are normalized, which makes KMeans behave as
    # spherical k-means for better results. Since LSA/SVD results are
    # not normalized, we have to redo the normalization.
    svd = TruncatedSVD(opts.n_components)
    lsa = make_pipeline(svd, Normalizer(copy=False))

    X = lsa.fit_transform(X)

    print("done in %fs" % (time() - t0))

    explained_variance = svd.explained_variance_ratio_.sum()
    print("Explained variance of the SVD step: {}%".format(
        int(explained_variance * 100)))

    print()


###############################################################################
# Do the actual clustering

if opts.minibatch:
    km = MiniBatchKMeans(n_clusters=20, init='k-means++', n_init=1,
                         init_size=5, batch_size=1000, verbose=opts.verbose)
else:
    km = KMeans(n_clusters=20, init='k-means++', max_iter=100000, n_init=10,
                verbose=opts.verbose)

print("Clustering sparse data with %s" % km)
t0 = time()
km.fit(X)
print("done in %0.3fs" % (time() - t0))
print()

if not (opts.n_components or opts.use_hashing):
    print("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    for i in range(true_k):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
        print()