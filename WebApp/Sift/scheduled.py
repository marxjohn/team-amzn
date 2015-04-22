from __future__ import absolute_import

from datetime import datetime
from Sift.models import *
from Sift.clustering import run_diagnostic_clustering
from Sift.classification import run_classification
from Sift.notification import *
from Sift.pdf_generator import create_pdf
from Sift.scikit_utilities import create_cluster_data
from Sift import notification


import pymysql
pymysql.install_as_MySQLdb()


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
    cluster_run, pdf_lines = run_diagnostic_clustering(data, start_date, end_date, 1000, 5, .85, 20, 50, 150)
    return cluster_run, pdf_lines


def main():
    # Retrieve all posts that have not been classified / clustered
    test_list = Post.objects.filter(cluster_id__isnull=True)
    if len(test_list) > 0:
        end_date, start_date = find_min_and_max_date(test_list)

        # Take a random sampling of 10000 posts to use as the training set
        train_list = Post.objects.filter(cluster_id__isnull=False).order_by('?')[:10000]

        test_data = create_cluster_data(test_list)
        train_data = create_cluster_data(train_list)

        run_classification(train_data, test_data, 1000, start_date, end_date)

    posts = Post.objects.all()
    data = create_cluster_data(posts)
    cluster_run, pdf_lines = run_clustering(data, posts)
    s_inertia = cluster_run.normalized_inertia
    s_score = cluster_run.silo_score
    # so we still send the email even if create pdf doesn't work
    try:
        create_pdf(pdf_lines, cluster_run.id)
    except:
        print("broke creating pdf")

    # Some Magic here involving sending email alerts
    notification.Nightly_email( s_score, s_inertia )

if __name__ == '__main__':
    main()
