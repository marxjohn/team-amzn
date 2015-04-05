from django.test import TestCase
import scikit_utilities
# Create your tests here.
class Post:
    def __init__(self, body, stemmed = False):
        self.body = body
        self.stemmed_body = body if stemmed else None
        self.post_id = 0
    def save(_):
        pass

class Posts:
    class Object:
        def __init__(self, data):
            self.data = data
        def get(self, post_id):
            return Post(self.data)
    def __init__(self, data):
        self.objects = self.Object(data)

def ClusterData_stemmed_body_test():
    data = "This is some test data"
    post = Post(data)
    res = scikit_utilities.ClusterData.stemmed_body(post)
    assert res[1] == False
    assert res[2] == 0
    post = Post(data, True)
    res = scikit_utilities.ClusterData.stemmed_body(post)
    assert res[1] == True
    assert res[2] == 0

def StemmedTfidfVectorizer_analyze_test():
    data = ("category categories", False, 0)
    scikit_utilities.Post = Posts(data)
    analyzer = scikit_utilities.StemmedTfidfVectorizer()
    analyze = analyzer.build_analyzer()
    assert analyze(data) == ['categori', 'categori']


if __name__ == "__main__":
    StemmedTfidfVectorizer_analyze_test()
