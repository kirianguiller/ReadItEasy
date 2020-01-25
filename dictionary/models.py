from django.db import models


class MandarinWord(models.Model):
    simplified = models.CharField(max_length=20)
    traditional = models.CharField(max_length=20)
    pronunciation = models.CharField(max_length=80)
    definitions = models.TextField()
    similar_words = models.TextField()
