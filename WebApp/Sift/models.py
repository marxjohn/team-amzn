# Create your models here.
from django.db import models


class Notification(models.Model):
    notificationid = models.IntegerField(db_column='notificationId', primary_key=True)  # Field name made lowercase.
    sentimentvalue = models.FloatField(db_column='sentimentValue')  # Field name made lowercase.
    email = models.CharField(max_length=45, blank=True)
    clusterN = models.ForeignKey('Cluster', db_column='cluster')

    class Meta:
        managed = False
        db_table = 'Notification'
        app_label = 'z'




class Cluster(models.Model):
    clusterid = models.IntegerField(db_column='clusterId', primary_key=True)  # Field name made lowercase.
    name = models.CharField(unique=True, max_length=32)
    ispinned = models.IntegerField(db_column='isPinned')  # Field name made lowercase.
    # notificationC = models.ForeignKey(Notification, db_column='notification', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Cluster'
        app_label = 'x'

    def __str__(self):
        return '\nId: ' + self.clusterid.__str__() + '\nName: ' + self.name


class ClusterWord(models.Model):
    id = models.IntegerField(db_column='Id', primary_key=True)  # Field name made lowercase.
    word = models.CharField(max_length=45)
    clusterid = models.ForeignKey(Cluster, db_column='clusterId', blank=True, null=True)  # Field name made lowercase.
    count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ClusterWord'
        app_label = 'cw'


class Post(models.Model):
    post_id = models.IntegerField(db_column='postId', primary_key=True)  # Field name made lowercase.
    thread_id = models.IntegerField(db_column='threadId')  # Field name made lowercase.
    message_id = models.IntegerField(db_column='messageId')  # Field name made lowercase.
    forum_id = models.IntegerField(db_column='forumId')  # Field name made lowercase.
    user_id = models.IntegerField(db_column='userId')  # Field name made lowercase.
    category_id = models.IntegerField(db_column='categoryId')  # Field name made lowercase.
    subject = models.CharField(max_length=512, blank=True)
    body = models.TextField(blank=True)
    posted_by_moderator = models.IntegerField(db_column='postedByModerator')  # Field name made lowercase.
    resolution_state = models.IntegerField(db_column='resolutionState')  # Field name made lowercase.
    helpful_answer = models.IntegerField(db_column='helpfulAnswer')  # Field name made lowercase.
    correct_answer = models.IntegerField(db_column='correctAnswer')  # Field name made lowercase.
    username = models.CharField(db_column='userName', max_length=64)  # Field name made lowercase.
    user_points = models.IntegerField(db_column='userPoints')  # Field name made lowercase.
    creation_date = models.DateField(db_column='creationDate')  # Field name made lowercase.
    modification_date = models.DateField(db_column='modificationDate')  # Field name made lowercase.
    locale = models.CharField(max_length=64, blank=True)
    cluster = models.ForeignKey(Cluster, db_column='cluster', blank=True, null=True, on_delete=models.SET_NULL)
    stemmed_body = models.TextField(db_column='stemmedBody', blank=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'Post'
        app_label = 'y'

    def __str__(self):
        return self.subject + self.body


class StopWord(models.Model):
    id = models.IntegerField(db_column='Id', primary_key=True)  # Field name made lowercase.
    word = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'StopWord'
        app_label = 'sw'

    def __str__(self):
        return self.word


class ClusterRun(models.Model):
    id = models.IntegerField(db_column='Id', primary_key=True)  # Field name made lowercase.
    run_date = models.DateTimeField(db_column='RunDate')  # Field name made lowercase.
    normalized_inertia = models.DecimalField(db_column='NormalizedInertia', max_digits=16, decimal_places=8)  # Field name made lowercase.
    start_date = models.DateTimeField(db_column='StartDate')  # Field name made lowercase.
    end_date = models.DateTimeField(db_column='EndDate')  # Field name made lowercase.
    num_clusters = models.IntegerField(db_column='NumClusters')  # Field name made lowercase.
    num_features = models.IntegerField(db_column='NumFeatures', blank=True, null=True)  # Field name made lowercase.
    n_init = models.IntegerField(db_column='NInit')  # Field name made lowercase.
    batch_size = models.IntegerField(db_column='BatchSize')  # Field name made lowercase.
    sample_size = models.IntegerField(db_column='SampleSize')  # Field name made lowercase.
    max_df = models.DecimalField(db_column='MaxDf', max_digits=2, decimal_places=2)  # Field name made lowercase.
    total_inertia = models.IntegerField(db_column='TotalInertia')  # Field name made lowercase.
    num_posts = models.IntegerField(db_column='NumPosts')  # Field name made lowercase.
    batch_size_ratio = models.DecimalField(db_column='BatchSizeRatio', max_digits=3, decimal_places=3)  # Field name made lowercase.
    sample_size_ratio = models.DecimalField(db_column='SampleSizeRatio', max_digits=3, decimal_places=3)  # Field name made lowercase.
    silo_score = models.DecimalField(db_column='SiloScore', max_digits=8, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ClusterRun'
        app_label = 'cr'


class Sentiment(models.Model):
    postid = models.ForeignKey(Post, db_column='postId', primary_key=True)  # Field name made lowercase.
    probnegative = models.DecimalField(db_column='probNegative', max_digits=21, decimal_places=20, blank=True, null=True)  # Field name made lowercase.
    probneutral = models.DecimalField(db_column='probNeutral', max_digits=21, decimal_places=20, blank=True, null=True)  # Field name made lowercase.
    probpositive = models.DecimalField(db_column='probPositive', max_digits=21, decimal_places=20, blank=True, null=True)  # Field name made lowercase.
    label = models.CharField(max_length=45, blank=True)

    class Meta:
        managed = False
        db_table = 'Sentiment'
        app_label = 's'