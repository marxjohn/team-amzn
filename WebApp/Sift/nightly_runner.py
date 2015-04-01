from __future__ import absolute_import

from datetime import date
from datetime import datetime
try:
    from Sift.models import *
    from Sift.clustering import run_diagnostic_clustering
    from Sift.classification import classify_on_date_range
    from Sift.scikit_utilities import create_cluster_data
except:
    from clustering import run_diagnostic_clustering
    from classification import run_classification
    from models import *

from scikit_utilities import create_cluster_data

from Sift.models import Notification



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
            'HOST': 'restorestemmedbody.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
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


def send_nightly_runner( s_score, s_inertia ):
    make_email_list = VerifyEmail()
    email_list = make_email_list.make_verify_email_list()

    if email_list == None:
        return False
    else:
        topic = 'Nightly Runner Notification'
        send_message = SESMessage( email_list[0], email_list[0], topic )
        for i in range( 1, len(email_list) ):
            send_message.add_bcc_address( email_list[i] )
        text = 's_score = ' + str(s_score) + ', ' + 's_inertia = ' + str(s_inertia)
        send_message.set_text( text )
        send_message.send()
        return True



def main():
    c_list = Post.objects.filter(cluster_id=None).order_by('creation_date')
    # end_date, start_date = find_min_and_max_date(c_list)

    train_list = Post.objects.filter(cluster_id=not None).order_by('creation_date')
    # train_end_date, train_start_date = find_min_and_max_date(train_list)

    cluster_data = create_cluster_data(c_list)
    train_data = create_cluster_data(train_list)

    run_classification(train_data, cluster_data, 1000)
    posts = Posts.objects.all()
    end_date, start_date = find_min_and_max_date(posts)
    s_score, s_inertia = run_diagnostic_clustering(posts, start_date, end_date, 1000, 5, .85, 20, 50, 150)

    # TODO: Some Magic here involving sending email alerts

    send_nightly_runner( s_score, s_inertia )

if __name__ == '__main__':
    main()
