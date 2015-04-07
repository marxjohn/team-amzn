from __future__ import absolute_import

from datetime import date
from datetime import datetime

from Sift.models import *
from Sift.clustering import run_diagnostic_clustering
from Sift.classification import run_classification
from Sift.scikit_utilities import create_cluster_data
from Sift.Notification import *

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


def send_nightly_runner(email_text):
    make_nightly_subscription = SNSNotification()
    make_nightly_subscription.make_arn_list()
    nightly_subscription = Sift.Notification.get_nightly_list()

    if nightly_subscription == None:
        return False
    else:
        make_nightly_subscription.set_topic_arn('NightlyRun')
        make_nightly_subscription.set_message(email_text)

        make_nightly_subscription.publication()
        return True

    # make_email_list = SESVerifyEmail()
    # email_list = make_email_list.make_verify_email_list()
    #
    # if email_list == None:
    #     return False
    # else:
    #     topic = 'SIFT MSU Runner Notification'
    #     send_message = SESMessage("siftmsu15@gmail.com", "siftmsu15@gmail.com", topic)
    #     for i in range(1, len(email_list)):
    #         send_message.add_cc_address(email_list[i])
    #     # Create email contents with information
    #     send_message.set_text(email_text)
    #     send_message.send()
    #     return True


def run_clustering(data, posts):
    end_date, start_date = find_min_and_max_date(posts)
    s_score, s_inertia = run_diagnostic_clustering(data, start_date, end_date, 1000, 5, .85, 20, 50, 150)
    return s_inertia, s_score


def run_clustering(data, posts):
    end_date, start_date = find_min_and_max_date(posts)
    s_score, s_inertia = run_diagnostic_clustering(data, start_date, end_date, 1000, 5, .85, 20, 50, 150)
    return s_inertia, s_score


def main():
    test_list = Post.objects.filter(cluster_id__isnull=True)[:10000]
    end_date, start_date = find_min_and_max_date(test_list)
    #

    train_list = Post.objects.filter(cluster_id__isnull=False, creation_date__range=('2014-01-01', '2014-01-12'))
    #train_end_date, train_start_date = find_min_and_max_date(train_list)
    #
    test_data = create_cluster_data(test_list)
    train_data = create_cluster_data(train_list)
    #
    if len(test_list) > 0:
        run_classification(train_data, test_data, 1000, start_date, end_date)

    posts = Post.objects.all()
    data = create_cluster_data(posts)
    s_inertia, s_score = run_clustering(data, posts)



    # Some Magic here involving sending email alerts
    text = "The status of the clusters are as follows: s_score: " + str(s_score) + ",  s_intertia: " + str(s_inertia)
    send_nightly_runner(text)

if __name__ == '__main__':
    main()
