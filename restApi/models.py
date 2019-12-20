from django.db import models

# Create your models here.


class WordsStats(models.Model):
    word = models.CharField(max_length=30)
    freq = models.IntegerField()
