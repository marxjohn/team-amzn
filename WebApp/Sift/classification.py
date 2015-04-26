from __future__ import print_function

import numpy as np
from time import time
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.svm import LinearSVC
from sklearn.utils.extmath import density

from scikit_utilities import StemmedTfidfVectorizer
from scikit_utilities import get_cluster_data
from scikit_utilities import associate_post_with_cluster

import django
from django.conf import settings
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

# NUM_FEATURES = 1000
# IS_REPORT_PRINTED = True
# IS_CONFUSION_MATRIX_PRINTED = True
# IS_CHI_SQUARED_USED = True
# IS_IDF_USED = True
IS_UPLOAD_ENABLED = True
IS_PLOTTING_ON = False


class ClassificationParams():

    def __init__(self, num_features, is_report_printed, is_chi_squared_used,
                 is_idf_used, is_upload_enabled):

        self.num_features = num_features
        self.is_report_printed = is_report_printed
        self.is_chi_squared_used = is_chi_squared_used
        self.is_idf_used = is_idf_used
        self.is_upload_enabled = is_upload_enabled


class L1LinearSVC(LinearSVC):

    def fit(self, X, y):
        # The smaller C, the stronger the regularization.
        # The more regularization, the more sparsity.
        self.transformer_ = LinearSVC(penalty="l1",
                                      dual=False, tol=1e-3)
        X = self.transformer_.fit_transform(X, y)
        return LinearSVC.fit(self, X, y)

    def predict(self, X):
        X = self.transformer_.transform(X)
        return LinearSVC.predict(self, X)


def run_classification(data_train, data_test, num_features, start_date,
                       end_date):
    c_params = ClassificationParams(num_features=num_features,
                                    is_report_printed=False,
                                    is_chi_squared_used=False,
                                    is_idf_used=True, is_upload_enabled=True)

    categories = data_train.cluster_list

    X_test, X_train, vectorizer, y_train = vectorize(
        data_test, data_train, c_params)

    if c_params.is_chi_squared_used:
        chi_squared_transformer(X_test, X_train, y_train, c_params)

    # mapping from integer feature name to original token string
    feature_names = np.asarray(vectorizer.get_feature_names())

    classify(L1LinearSVC(), data_test, X_train, y_train,
             X_test, feature_names, categories, c_params)

    if c_params.is_upload_enabled:
        associate_post_with_cluster(
            data_test, len(categories), start_date, end_date)


def _vectorize(data_test, data_train, c_params):
    # list of cluster associated with each posts
    y_train = data_train.cluster_of_posts
    print(
        "Extracting features from the training dataset \
                using a sparse vectorizer")
    t0 = time()
    vectorizer = StemmedTfidfVectorizer(max_df=.8,
                                        max_features=c_params.num_features,
                                        min_df=1,
                                        use_idf=c_params.is_idf_used,
                                        analyzer='word', ngram_range=(1, 1))
    # Create training data
    X_train = vectorizer.fit_transform(data_train.data)
    # Create data to classify
    X_test = vectorizer.transform(data_test.data)
    return X_test, X_train, vectorizer, y_train


def _chi_squared_transformer(X_test, X_train, y_train, c_params):
    t0 = time()
    ch2 = SelectKBest(chi2, k=c_params.num_features)
    X_train = ch2.fit_transform(X_train, y_train)
    X_test = ch2.transform(X_test)
    print()


def _trim(s):
    """Trim string to fit on terminal (assuming 80-column display)"""
    return s if len(s) <= 80 else s[:77] + "..."


def _classify(clf, cluster_data, X_train, y_train, X_test, feature_names,
             categories, c_params):
    print('_' * 80)
    print("Training: ")
    print(clf)
    t0 = time()
    clf.fit(X_train, y_train)
    train_time = time() - t0
    print("train time: %0.3fs" % train_time)

    t0 = time()
    cluster_data.cluster_of_posts = clf.predict(X_test)
    test_time = time() - t0
    print("test time:  %0.3fs" % test_time)

    if hasattr(clf, 'coef_'):
        print("dimensionality: %d" % clf.coef_.shape[1])
        print("density: %f" % density(clf.coef_))

        if feature_names is not None:
            print("top 10 keywords per class:")
            for i, category in enumerate(categories):
                top10 = np.argsort(clf.coef_[i])[-10:]
                print(trim("%s: %s"
                           % (category, " ".join(feature_names[top10]))))
        print()

    if c_params.is_report_printed:
        print("classification report:")

    print()
    clf_descr = str(clf).split('(')[0]
    return clf_descr, train_time, test_time
