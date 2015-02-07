# Create your models here.
from django.db import models

class Cluster(models.Model):
    name = models.CharField(max_length=32)
    pinned = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class Post(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    cluster = models.ForeignKey(Cluster)
    created_date = models.DateTimeField('date created')
    def __str__(self):
        return self.body



