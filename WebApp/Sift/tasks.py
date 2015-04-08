from celery import shared_task
from time import time
import Sift.clustering as clustering
from Sift.models import Post
from Sift.Notification import *
import logging
import datetime
from django.core.cache import cache

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
    make_nightly_subscription = SNSNotification()
    make_nightly_subscription.make_arn_list()
    nightly_subscription = get_nightly_list()

    if nightly_subscription is not None:
        make_nightly_subscription.set_topic_arn('Diagnostic Clustering')
        make_nightly_subscription.set_message("Successfully completed Diagnostic Clustering in " + str(time() - t0) + " seconds! From "
                          + str(start_date) + " to " + str(end_date) + " with "
                          + str(num_clusters) + " clusters and " + str(max_features)
                          + " features.")

        make_nightly_subscription.publication()

    cache.clear()


def main():
    cluster_posts_with_input("2015-03-15", "2015-03-30", 8, 1000, False, False)


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
