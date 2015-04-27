from datetime import datetime
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
import numpy as np
import django
from django.db import connection
import Stemmer
from Sift.models import Post, Cluster, ClusterWord, StopWord
import pymysql
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

english_stemmer = Stemmer.Stemmer('en')

django.setup()
REMOVE_LIST = set(StopWord.objects.all().values_list("word", flat=True))
STOP_WORDS = list(REMOVE_LIST.union(stopwords.words('english')))


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

    def __init__(self, inp, cluster_inp):

        self.id_list = [p.post_id for p in inp]
        self.cluster_of_posts = [p.cluster_id for p in inp]
        self.cluster_list = [c.clusterid for c in cluster_inp]
        self.data = np.fromiter(
            ((i.stemmed_body, i.post_id) for i in inp),
            dtype=[("body", "|U5000"), ("id", "i")],
            count=inp.count())


def get_cluster_data(start_date, end_date):

    data_set = ClusterData(Post.objects.filter(
        creation_date__range=(start_date, end_date)), Cluster.objects.all())
    return data_set


def _create_cluster_data(post_list):
    return ClusterData(post_list, Cluster.objects.all())


def associate_post_with_cluster(data_set, num_clusters, start_date, end_date):
    for j in range(0, num_clusters):
        query = "UPDATE Post SET Post.cluster = " + str(j + 1) + " where"
        is_first = True
        count = 0
        for i in range(0, len(data_set.id_list)):
            x = data_set.cluster_of_posts[i]
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
                query = "UPDATE Post SET posts.cluster = " + \
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

        for cw in ClusterWord.objects.all():
            count = len(Post.objects.filter(cluster=c,
                                            stemmed_body__contains=cw.word,
                                            creation_date__range=(start_date,
                                                                  end_date)))

            cw.count += count
            cw.save()


def _find_min_and_max_date(c_list):
    min_date = datetime.now().date()
    for c in c_list:
        if c.creation_date <= min_date:
            min_date = c.creation_date
    max_date = datetime.min.date()
    for c in c_list:
        if c.creation_date >= max_date:
            max_date = c.creation_date
    start_date = min_date
    end_date = max_date
    return end_date, start_date
