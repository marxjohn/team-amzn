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

import matplotlib.pyplot as plt
try:
    from models import Post, Sentiment
except:
    from Sift.models import Post, Sentiment

from bs4 import BeautifulSoup
from lxml import html
import requests
import django
from time import time
from datetime import datetime

django.setup()



def main():
    conn = pymysql.connect(host='restorestemmedbody.cqtoghgwmxut.us-west-2.rds.amazonaws.com', port=3306, user='teamamzn', passwd='TeamAmazon2015!', db='sellerforums')
    t0 = time()
    print("grabbing posts from db")
    dataset = Post.objects.all()

    print("sentiment time!")
    for post in dataset:
        body = html.document_fromstring(BeautifulSoup(post.body).getText()).text_content()
        payload = {'text': body[:80000]}
        r = requests.post("http://text-processing.com/api/sentiment/", data=payload)
        try:
            # print(payload)
            # print(r.json())
            senti = Sentiment(post_id=post, prob_negative=r.json()['probability']['neg'],
                              prob_neutral=r.json()['probability']['neutral'], prob_positive=r.json()['probability']['pos'],
                              label=r.json()['label'])
            senti.save()
        except:
            print("broke :(")
            print(r)
            break
    print("complete")



# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == "__main__":
    main()
