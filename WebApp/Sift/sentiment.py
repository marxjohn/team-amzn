from __future__ import absolute_import

import os

try:
    import pymysql
    pymysql.install_as_MySQLdb()

except:
    pass

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

try:
    from models import *
except:
    from Sift.models import *

from lxml import html
import requests
import django
from time import time

django.setup()


def lazy_sentiment(start_date, end_date):
    t0 = time()
    print("grabbing posts from db")
    dataset = Post.objects.filter(
        creation_date__range=(start_date, end_date), sentiment__isnull=True)

    suc = 0
    skip = 0
    print("lazy sentiment time!")
    for post in dataset:
        if post.sentiment == None:
            try:
                body = html.document_fromstring(post.body).text_content()
            except:
                body = ""
            payload = {'text': body[:80000]}
            r = requests.post(
                "http://text-processing.com/api/sentiment/", data=payload)
            try:
                print(payload)
                print(r.json())

                post.sentiment = r.json()['label']
                post.probnegative = r.json()['probability']['neg']
                post.probneutral = r.json()['probability']['neutral']
                post.probpositive = r.json()['probability']['pos']
                post.save()
                suc += 1
            except:
                print("broke :(")
                print(r)
                if str(r) == "<Response [400]>":
                    print("bad text")
                else:
                    print("reset ip and launch again")
                    break

        else:
            skip += 1
            print(str(skip) + " skipped")

    print("Successfully sentimented: " + str(suc) + " posts")
    print("Skipped over: " + str(skip) + " posts")
    print("done in %fs" % (time() - t0))


def main():
    lazy_sentiment("2013-01-01", "2014-04-01")


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
