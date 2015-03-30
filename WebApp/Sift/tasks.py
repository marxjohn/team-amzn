from __future__ import absolute_import
__author__ = 'cse498'

from celery import shared_task
from time import time
from Sift.models import Post

import Sift.clustering
import logging
import datetime
import time

@shared_task
def cluster_posts_with_input(start_date, end_date, num_clusters, max_features, isMiniBatch, isAllPosts):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    if isAllPosts:
        start_date = "2000-01-01"
        end_date = datetime.date.today().strftime('%Y-%m-%d')

    print("querying db")
    dataset = Sift.clustering.ClusterData(Post.objects.filter(creation_date__range=(start_date, end_date)))

    print("starting diagnostic clustering")
    Sift.clustering.run_diagnostic_clustering(dataset, start_date, end_date, max_features, num_clusters, .85, 20, 50, 150)