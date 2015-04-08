from celery import shared_task
from time import time
import Sift.clustering as clustering
from Sift.models import Post
from django.core.cache import cache
import logging
import datetime
from django.core.cache import cache

__author__ = 'cse498'


@shared_task
def cluster_posts_with_input(start_date, end_date, num_clusters, max_features,
                             isMiniBatch, isAllPosts):
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
    cache.clear()


def main():
    dataset = clustering.ClusterData(
        Post.objects.filter(creation_date__range=("2015-03-15", "2015-03-30")))

    clustering.run_diagnostic_clustering(
        dataset, "2015-03-25", "2015-03-30", 1000, 8, .85, 20, 50, 150)


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
