from django.db import models


class User(models.Model):
    username = models.CharField(max_length=30)
    passwordmd5 = models.CharField(max_length=33)
    sess = models.TextField()


class News(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    content = models.TextField()
    url = models.URLField()
    deleted = models.BooleanField(default=False)
