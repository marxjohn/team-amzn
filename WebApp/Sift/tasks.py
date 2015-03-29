from __future__ import absolute_import
__author__ = 'cse498'

from celery import shared_task
from time import time
from Sift.models import Post

import Sift.clustering
import logging

@shared_task
def cluster_posts_with_input(start_date, end_date, num_clusters, max_features, isMiniBatch, isAllPosts):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    print("Retrieving dataset from database")
    t0 = time()

    if isAllPosts:
        dataset = Sift.clustering.ClusterData(Post.objects.all())
    else:
        dataset = Sift.clustering.ClusterData(Post.objects.filter(creation_date__range=(start_date, end_date)))

    Sift.clustering.run_diagnostic_clustering(dataset, start_date, end_date, 1000, 5, .85, 20, 50, 150)