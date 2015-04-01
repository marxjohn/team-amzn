from __future__ import absolute_import
__author__ = 'cse498'

from celery import shared_task
from time import time

try:
    import clustering
    from models import Post
except:
    import Sift.clustering as clustering
    from Sift.models import Post

import logging
import datetime

@shared_task
def cluster_posts_with_input(start_date, end_date, num_clusters, max_features, isMiniBatch, isAllPosts):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    if isAllPosts:
        start_date = "2000-01-01"
        end_date = datetime.date.today().strftime('%Y-%m-%d')

    print("querying db")
    dataset = clustering.ClusterData(Post.objects.filter(creation_date__range=(start_date, end_date)))

    print("starting diagnostic clustering")
    clustering.run_diagnostic_clustering(dataset, start_date, end_date, max_features, num_clusters, .85, 20, 50, 150)


def main():
    print("querying db")
    dataset = clustering.ClusterData(Post.objects.filter(creation_date__range=("2015-03-15", "2015-03-30")))

    print("starting diagnostic clustering")
    clustering.run_diagnostic_clustering(dataset, "2015-03-25", "2015-03-30", 1000, 8, .85, 20, 50, 150)
    print("complete!")


# # Only run the main function if this code is called directly
# # Not if it's imported as a module
if __name__ == "__main__":
    main()
