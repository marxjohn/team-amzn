from __future__ import absolute_import

from django.core.cache import cache
import pymysql
import django
from django.conf import settings

from Sift.models import *
from Sift.scikit_utilities import create_cluster_data
from Sift.Notification import *
from Sift.clustering import run_creation_clustering
from scikit_utilities import create_cluster_data
from Sift.scikit_utilities import find_min_and_max_date

pymysql.install_as_MySQLdb()
django.setup()
if not settings.configured:
    settings.configure(
        DATABASES={'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': 'siftmsu.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
            'PORT': '3306',
            'USER': 'teamamzn',
            'PASSWORD': 'TeamAmazon2015!',
            'NAME': 'sellerforums',
            'OPTIONS': {
                'autocommit': True,
            },
        }
        }
    )


def run_clustering(data, posts):
    end_date, start_date = find_min_and_max_date(posts)
    s_score, s_inertia = run_creation_clustering(
        data, start_date, end_date, 1000, 5, .85, 20, 50, 150)
    return s_inertia, s_score


def main():
    posts = Post.objects.all()
    data = create_cluster_data(posts)
    run_clustering(data, posts)
    cache.clear()


if __name__ == '__main__':
    main()
