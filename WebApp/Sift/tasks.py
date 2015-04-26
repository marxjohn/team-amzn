from time import time
import logging
import datetime

from Sift._celery import app
from django.core.cache import cache

import Sift.clustering as clustering
from Sift.models import Post, Cluster
from Sift.notification import *
from Sift.scikit_utilities import find_min_and_max_date, create_cluster_data, ClusterData
from Sift.clustering import run_creation_clustering
from Sift.pdf_generator import create_pdf
from Sift import notification


__author__ = 'cse498'


@app.task(bind=True)
def cluster_posts_with_input(self, start_date, end_date, num_clusters, max_features, is_all_posts,
                        max_df=.5, batch_size_ratio=20, init_size_ratio=10, n_init=150):
    t0 = time()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    self.update_state(state='FETCHING_POSTS')
    if is_all_posts:
        posts = Post.objects.all()
        end_date, start_date = find_min_and_max_date(posts)
    else:
        posts = Post.objects.filter(creation_date__range=(start_date, end_date))

    self.update_state(state='CREATING_CLUSTER_DATA')
    data = create_cluster_data(posts)

    self.update_state(state='RUNNING_CLUSTERING')
    cluster_run, pdf_lines = clustering.run_diagnostic_clustering(
        data, start_date, end_date, max_features,
        num_clusters, max_df, batch_size_ratio, init_size_ratio, n_init)

    self.update_state(state='SENDING_NOTIFICATIONS')
    notification.Diagnostic_email((time()-t0), str(start_date), str(end_date), num_clusters, max_features)
    create_pdf(pdf_lines, cluster_run.id)
    cache.clear()


@app.task(bind=True)
def create_new_clusters(self, start_date, end_date, num_clusters, max_features, is_all_posts,
                        max_df=.8, batch_size_ratio=20, init_size_ratio=10, n_init=150):
    t0 = time()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    self.update_state(state='FETCHING_POSTS')
    if is_all_posts:
        posts = Post.objects.all()
        end_date, start_date = find_min_and_max_date(posts)
    else:
        posts = Post.objects.filter(creation_date__range=(start_date, end_date))

    self.update_state(state='CREATING_CLUSTER_DATA')
    data = create_cluster_data(posts)

    self.update_state(state='RUNNING_CREATION_CLUSTERING')
    cluster_run, pdf_lines = run_creation_clustering(
        data, start_date, end_date, max_features, num_clusters, max_df, batch_size_ratio, init_size_ratio, n_init)

    self.update_state(state='SENDING_NOTIFICATIONS')
    notification.ClusterCreation_email((time()-t0), str(start_date), str(end_date), num_clusters, max_features)
    create_pdf(pdf_lines, cluster_run.id)
    cache.clear()


def main():
    cluster_posts_with_input.delay("2015-03-15", "2015-03-30", 8, 1000, False)


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
