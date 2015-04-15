from time import time
import logging
import datetime

from celery import shared_task
from django.core.cache import cache

import Sift.clustering as clustering
from Sift.models import Post
from Sift.Notification import *
from WebApp.Sift.scikit_utilities import find_min_and_max_date, create_cluster_data
from WebApp.Sift.clustering import run_creation_clustering


__author__ = 'cse498'


@shared_task(bind=True)
def cluster_posts_with_input(start_date, end_date, num_clusters, max_features,isAllPosts):
    t0 = time()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    if isAllPosts:
        start_date = "2000-01-01"
        end_date = datetime.date.today().strftime('%Y-%m-%d')
    # self.update_state(state='FETCHING_POSTS')
    dataset = clustering.ClusterData(
        Post.objects.filter(creation_date__range=(start_date, end_date)))
    # self.update_state(state='RUNNING_CLUSTERING')
    clustering.run_diagnostic_clustering(
        dataset, start_date, end_date, max_features,
        num_clusters, .85, 20, 50, 150)
    # self.update_state(state='SENDING_NOTIFICATIONS')
    # send email
    email = SNSNotification()
    email.make_arn_list()
    email_list = get_nightly_list()

    if email_list is not None:
        email.set_topic_arn('DiagnosticClustering')
        email.set_message("Successfully completed Diagnostic Clustering in " + str(time() - t0) + " seconds! From "
                          + str(start_date) + " to " + str(end_date) + " with "
                          + str(num_clusters) + " clusters and " + str(max_features)
                          + " features.")
        email.set_subject('DiagnosticClustering')

        email.publication()
    # self.update_state(state='CLUSTERING_COMPLETED')
    cache.clear()


@shared_task(bind=True)
def create_new_clusters(num_clusters, max_features, max_df=.85, batch_size_ratio=20, init_size_ratio=50, n_init=150):
    self.update_state(state='FETCHING_POSTS')
    posts = Post.objects.all()
    self.update_state(state='CREATING_CLUSTER_DATA')
    data = create_cluster_data(posts)
    end_date, start_date = find_min_and_max_date(posts)
    self.update_state(state='RUNNING_CREATION_CLUSTERING')
    run_creation_clustering(
        data, start_date, end_date, max_features, num_clusters, max_df, batch_size_ratio, init_size_ratio, n_init)
    self.update_state(state='CLUSTERING_COMPLETED')
    cache.clear()


def main():
    cluster_posts_with_input("2015-03-15", "2015-03-30", 8, 1000, False, False)


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
