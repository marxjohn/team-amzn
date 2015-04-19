from time import time
import logging
import datetime

from Sift._celery import app
from django.core.cache import cache

import Sift.clustering as clustering
from Sift.models import Post, Cluster
from Sift.Notification import *
from Sift.scikit_utilities import find_min_and_max_date, create_cluster_data, ClusterData
from Sift.clustering import run_creation_clustering
from Sift.pdf_generator import create_pdf
from Sift import Notification


__author__ = 'cse498'


@app.task(bind=True)
def cluster_posts_with_input(self, start_date, end_date, num_clusters, max_features,
                             isAllPosts):
    t0 = time()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    if isAllPosts:
        start_date = "2000-01-01"
        end_date = datetime.date.today().strftime('%Y-%m-%d')
    self.update_state(state='FETCHING_POSTS')
    dataset = ClusterData(
        Post.objects.filter(creation_date__range=(start_date, end_date)),
        Cluster.objects.all())
    self.update_state(state='RUNNING_CLUSTERING')
    cluster_run, pdf_lines = clustering.run_diagnostic_clustering(
        dataset, start_date, end_date, max_features,
        num_clusters, .85, 20, 50, 150)
    self.update_state(state='SENDING_NOTIFICATIONS')
    # send email
    Notification.Diagnostic_email( str(time()-t0), str(start_date), str(end_date), num_clusters, max_features )

    self.update_state(state='CLUSTERING_COMPLETED')
    create_pdf(pdf_lines, cluster_run.id)
    cache.clear()


@app.task(bind=True)
def create_new_clusters(self, num_clusters, max_features, max_df=.85, batch_size_ratio=20, init_size_ratio=50, n_init=150):
    self.update_state(state='FETCHING_POSTS')
    posts = Post.objects.all()
    self.update_state(state='CREATING_CLUSTER_DATA')
    data = create_cluster_data(posts)
    end_date, start_date = find_min_and_max_date(posts)
    self.update_state(state='RUNNING_CREATION_CLUSTERING')
    cluster_run, pdf_lines = run_creation_clustering(
        data, start_date, end_date, max_features, num_clusters, max_df, batch_size_ratio, init_size_ratio, n_init)
    self.update_state(state='CLUSTERING_COMPLETED')
    create_pdf(pdf_lines, cluster_run.id)
    cache.clear()


def main():
    cluster_posts_with_input.delay("2015-03-15", "2015-03-30", 8, 1000, False)


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
