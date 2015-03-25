from __future__ import absolute_import
# K-means clustering of seller forums posts

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



from models import Post, Cluster, ClusterWord, StopWord


from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
import numpy as np
import django
from django.db import connection

import Stemmer
english_stemmer = Stemmer.Stemmer('en')

django.setup()
REMOVE_LIST = set(StopWord.objects.all().values_list("word", flat=True))
STOP_WORDS = list(REMOVE_LIST.union(stopwords.words('english')))

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

    def __init__(self, inp, cluster_inp):
        self.id_list = [p.postid for p in inp]
        self.cluster_of_posts = [p.cluster_id for p in inp]
        self.cluster_list = [c.clusterid for c in cluster_inp]
        self.data = np.fromiter(
            map(ClusterData.stemmed_body, inp),
            dtype=[("body", "|U5000"), ("stemmed", "b"), ("id", "i")],
            count=len(inp))


def get_cluster_data(start_date, end_date):

    data_set = ClusterData(Post.objects.filter(creationdate__range=(start_date, end_date)), Cluster.objects.all())
    return data_set


def associate_post_with_cluster(data_set, num_clusters, start_date, end_date):
    for j in range(0, num_clusters):
        query = "UPDATE posts SET posts.cluster = " + str(j+1) + " where"
        is_first = True
        count = 0
        for i in range(0, len(data_set.id_list)):
            x = data_set.cluster_of_posts[i]
            post_id = data_set.id_list[i]
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

        for cw in ClusterWord.objects.all():
            count = len(Post.objects.filter(cluster=c, stemmedbody__contains=cw.word,
                                            creationdate__range=(start_date, end_date)))

            cw.count += count
            cw.save()



