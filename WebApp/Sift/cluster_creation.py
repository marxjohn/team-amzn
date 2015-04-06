from __future__ import absolute_import

from datetime import datetime
try:
    from Sift.models import *
    from Sift.clustering import run_diagnostic_clustering
    from Sift.classification import classify_on_date_range
    from Sift.scikit_utilities import create_cluster_data
    from Sift.models import Notification
    from Sift.Notification import *
except:
    from clustering import run_creation_clustering
    from classification import run_classification
    from models import *
    from models import Notification
    from Notification import *

from scikit_utilities import create_cluster_data





try:
    import pymysql
    pymysql.install_as_MySQLdb()

except:
    pass

import django
django.setup()
from django.conf import settings
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


def find_min_and_max_date(c_list):
    min_date = datetime.now().date()
    for c in c_list:
        if c.creation_date <= min_date:
            min_date = c.creation_date
    max_date = datetime.min.date()
    for c in c_list:
        if c.creation_date >= max_date:
            max_date = c.creation_date
    start_date = min_date
    end_date = max_date
    return end_date, start_date


def run_clustering(data, posts):
    end_date, start_date = find_min_and_max_date(posts)
    s_score, s_inertia = run_creation_clustering(data, start_date, end_date, 1000, 5, .85, 20, 50, 150)
    return s_inertia, s_score


def main():
    posts = Post.objects.all()
    data = create_cluster_data(posts)
    run_clustering(data, posts)



if __name__ == '__main__':
    main()
