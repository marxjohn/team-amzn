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


@shared_task
def cluster_posts_with_input(start_date, end_date, num_clusters, max_features,
                             isMiniBatch, isAllPosts):
    t0 = time()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    if isAllPosts:
        start_date = "2000-01-01"
        end_date = datetime.date.today().strftime('%Y-%m-%d')

    dataset = clustering.ClusterData(
        Post.objects.filter(creation_date__range=(start_date, end_date)))

    clustering.run_diagnostic_clustering(
        dataset, start_date, end_date, max_features,
        num_clusters, .85, 20, 50, 150)

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

    cache.clear()


@shared_task
def create_new_clusters(num_clusters, max_features, max_df=.85, batch_size_ratio=20, init_size_ratio=50, n_init=150):
    posts = Post.objects.all()
    data = create_cluster_data(posts)
    end_date, start_date = find_min_and_max_date(posts)
    run_creation_clustering(
        data, start_date, end_date, max_features, num_clusters, max_df, batch_size_ratio, init_size_ratio, n_init)
    cache.clear()


def main():
    cluster_posts_with_input("2015-03-15", "2015-03-30", 8, 1000, False, False)


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
