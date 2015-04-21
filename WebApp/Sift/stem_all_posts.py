from __future__ import absolute_import


import pymysql
import django
from django.conf import settings
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


def main():
    posts = Post.objects.all()

    for post in posts:
        stemmed = post.body.split(' ')
        post.stemmed_body = ' '.join(stemmed)
        post.save()

if __name__ == '__main__':
    main()

