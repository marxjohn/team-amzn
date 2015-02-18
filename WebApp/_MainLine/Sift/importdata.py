__author__ = 'MaxGoovaerts'

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
            'HOST': 'sellerforums.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
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

# from models import *
import logging
from time import time
from datetime import datetime

DATA_FILES = ['data/expSForums' + str(i) + '.cvs' for i in range(2,11)]

def init_db():
    conn = pymysql.connect(host='sellerforums.cqtoghgwmxut.us-west-2.rds.amazonaws.com', port=3306, user='teamamzn', passwd='TeamAmazon2015!', db='sellerforums')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS data (threadId INT, \
            messageId INT, forumID INT, userID INT, categoryID INT, \
            subject TEXT, body TEXT, postedByModerator BOOL, \
            resolutionState INT, helpfulAnswer INT, correctAnswer INT, \
            userName TEXT, userPoints INT, creationDate DATE, \
            modificationDate DATE, locale TEXT)")
    conn.commit()
    return conn

def get_post_count(conn):
    cur = conn.cursor()
    cur.execute("SELECT Count(*) FROM sellerforums.posts")
    return cur.fetchone()

def commitPost(post, conn):
        cur = conn.cursor()
        query = "INSERT INTO data (threadId, messageId, forumId, userId, categoryId, subject, body, postedByModerator," \
                " resolutionState, helpfulAnswer, correctAnswer, userName, userPoints, creationDate, modificationDate, locale) VALUES "
        query += "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # posts need to be encoded to avoid weird character breaking errors
        cur.execute(query, (post[0], post[1], post[2], post[3], post[4], post[5].encode('ascii', 'replace'), post[6].encode('ascii', 'replace'),
                            post[7], post[8], post[9], post[10], post[11], post[12], post[13], post[14], post[15]))
        conn.commit()

# this function converts the provided time format to the mysql date format necessary for storing properly
def convertTime(input):
    date_obj = datetime.strptime(input, '%m/%d/%y')
    return date_obj.strftime('%Y/%m/%d')

def main():
    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    # print("Creating Database")
    # conn = init_db()
    conn = pymysql.connect(host='sellerforums.cqtoghgwmxut.us-west-2.rds.amazonaws.com', port=3306, user='teamamzn', passwd='TeamAmazon2015!', db='sellerforums')

    print("Importing Data")
    t0 = time()
    i = 0
    j = 300
    for f in DATA_FILES:
        p = 60000
        print("Reading Data File: " + str(f))
        with open(f, encoding="utf-8", errors="surrogateescape") as data_file:
            while True:
                parse = lambda i: i if '=' in i else '=\n'
                data = [parse(data_file.readline()).split('=', 1)[1].rstrip()
                        for i in range(17)][:-1]
                if data[0]:
                    data[13] = convertTime(data[13])
                    data[14] = convertTime(data[14])
                    i += 1
                    commitPost(data, conn)
                else:
                    break
                if (i-j == 0):
                    j += 300
                    print("% of file: " + str(round(p/600.0, 3)) + " post: " + str(i) + " time: " + str(round(time()-t0, 2)))

        print("Successfully read " + str(i) + " posts")
    print("Data Imported:")
    print(get_post_count(conn))
    print("done in %fs" % (time() - t0))
    conn.close()

# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == '__main__':
   main()
