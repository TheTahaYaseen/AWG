from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Feedback(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    given_by = models.ForeignKey(User, on_delete=models.CASCADE)
    dealt_with = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

class Word(models.Model):
    word = models.CharField(max_length=255, unique=True)
    definition = models.TextField()

class WordUsageExample(models.Model):
    associated_word = models.ForeignKey(Word, on_delete=models.CASCADE)
    sentence = models.TextField()

class Trivia(models.Model):
    name = models.CharField(max_length=255)

class TriviaQuestion(models.Model):
    question = models.CharField(max_length=255)
    answer_a = models.CharField(max_length=255)
    answer_b = models.CharField(max_length=255)
    answer_c = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    worth_in_points = models.IntegerField()
    associated_trivia = models.ForeignKey(Trivia, on_delete=models.CASCADE)

class Acheivement(models.Model):
    name = models.CharField(max_length=255)
    associated_trivia = models.ForeignKey(Trivia, on_delete=models.SET_NULL, null=True)
    points_required = models.IntegerField(null=True)

class AcheivementsUnlocked(models.Model):
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE)
    associated_acheivement = models.ForeignKey(Acheivement, on_delete=models.CASCADE)

class PointsRecord(models.Model):
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE)
    associated_trivia = models.ForeignKey(Trivia, on_delete=models.SET_NULL, null=True)    
    points = models.IntegerField()