from __future__ import absolute_import
__author__ = 'cse498'

from celery import shared_task
from time import time
from Sift.models import Post

import Sift.NLTKClustering
import logging

@shared_task
def cluster_posts_with_input(start_date, end_date, num_clusters, max_features, isMiniBatch):

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    print("Retrieving dataset from database")
    t0 = time()

    dataset = Sift.NLTKClustering.ClusterData(Post.objects.filter(creationdate__range=(start_date, end_date)))

    Sift.NLTKClustering.cluster_posts(dataset, t0, num_clusters, max_features, start_date, end_date)
