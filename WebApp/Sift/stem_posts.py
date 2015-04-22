from __future__ import absolute_import


import pymysql
import django
from django.conf import settings
from time import time
import Stemmer
from Sift.models import *


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

english_stemmer = Stemmer.Stemmer('en')


def main(start_date, end_date):
    # set up variables
    t0 = time()
    i = 0
    j = 1000

    print("Fetching posts...")
    # posts = Post.objects.filter(creation_date__range=(start_date, end_date))
    posts = Post.objects.all()

    print("Stemming posts...")

    for post in posts:
        # stemmed = post.body.split(' ')
        # post.stemmed_body = ' '.join(stemmed)
        post.stemmed_body = ' '.join(english_stemmer.stemWords(post.body.lower().split(' ')))
        post.save()

        # print progress indicator
        i += 1
        if (i - j == 0):
            j += 1000
            print("Stemmed ", str(i), " posts, ", str(round((i/posts.count())*100, 5)), "% of total posts")

    print("Completed stemming ", str(i), " posts in ", str((time() - t0)), " seconds.")

if __name__ == '__main__':
    main("2015-01-11", "2015-01-21")

