__author__ = 'MaxGoovaerts'

import logging
from time import time
from datetime import datetime
import pymysql
import django
from django.conf import settings
import Stemmer
from Sift.models import *
import requests
from lxml import html

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



DATA_FILES = ['data/expSForums' + str(i) + '.cvs' for i in range(1, 11)]

english_stemmer = Stemmer.Stemmer('en')

# this function converts the provided time format to the mysql date format
# necessary for storing properly


def convertTime(input):
    date_obj = datetime.strptime(input, '%m/%d/%y')
    return date_obj.strftime('%Y/%m/%d')


def main():
    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    print("Importing Data")
    # set up variables
    t0 = time()
    i = 0
    j = 1000
    errors = 0

    for f in DATA_FILES:
        p = 0
        print("Reading Data File: " + str(f))
        with open(f, encoding="utf-8", errors="surrogateescape") as data_file:
            while True:
                def parse(i):
                    return i if '=' in i else '=\n'
                data = [parse(data_file.readline()).split('=', 1)[1].rstrip()
                        for i in range(17)][:-1]

                # confirm that not eof
                if data[0]:
                    i += 1
                    p += 1
                else:
                    break

                # Convert dates to DB format
                data[13] = convertTime(data[13])
                data[14] = convertTime(data[14])


                # Create post obj
                post = Post()
                post.thread_id = data[0]
                post.message_id = data[1]
                post.forum_id = data[2]
                post.user_id = data[3]
                post.category_id = data[4]
                post.subject = data[5].encode('utf-8', 'ignore')
                post.body = data[6].encode('utf-8', 'ignore')
                post.posted_by_moderator = data[7]
                post.resolution_state = data[8]
                post.helpful_answer = data[9]
                post.correct_answer = data[10]
                post.username = data[11].encode('utf-8', 'ignore')
                post.user_points = data[12]
                post.creation_date = data[13]
                post.modification_date = data[14]
                post.locale = data[15]
                post.stemmed_body = ' '.join(english_stemmer.stemWords(post.body.lower().split(' ')))

                # Sentiment the post
                try:
                    body = html.document_fromstring(post.body).text_content()
                except:
                    body = post.body
                payload = {
                    'language': 'english',
                    'text': body[:80000]
                    }
                headers = {'X-Mashape-Key': '95BE98lwYHmshDH3PWsVP5w7CmLAp1es425jsneZYiyGW8F44P',
                           'Content-Type': 'application/x-www-form-urlencoded',
                           'Accept': 'application/json'}

                try:
                    r = requests.post(
                    "https://japerk-text-processing.p.mashape.com/sentiment/", data=payload, headers=headers)
                    post.sentiment = r.json()['label']
                    post.probnegative = r.json()['probability']['neg']
                    post.probneutral = r.json()['probability']['neutral']
                    post.probpositive = r.json()['probability']['pos']


                # Save the post
                try:
                    post.save()
                except:
                    errors += 1

               # Print progress indicator
                if (i - j == 0):
                    j += 1000
                    print("Uploaded ", str(i), " posts")

        print("Successfully read " + str(i) + " posts")
    print("Data Imported:")
    print("done in %fs" % (time() - t0))

# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == '__main__':
    main()
