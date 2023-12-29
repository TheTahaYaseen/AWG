from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Feedback(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    given_by = models.ForeignKey(User, on_delete=models.CASCADE)
    dealt_with = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Word(models.Model):
    word = models.CharField(max_length=255, unique=True)
    definition = models.TextField()

class WordUsageExample(models.Model):
    associated_word = models.ForeignKey(Word, on_delete=models.CASCADE)
    sentence = models.TextField()

class Trivia(models.Model):
    name = models.CharField(max_length=255)

class Acheivement(models.Model):
    name = models.CharField(max_length=255)
    associated_trivia = models.ForeignKey(Trivia, on_delete=models.CASCADE, null=True)
    points_required = models.IntegerField(null=True)