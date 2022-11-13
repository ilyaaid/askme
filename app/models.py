from django.db import models
from django.contrib.auth.models import User

# Create your models here.

QUESTIONS = [
    {
        'id': i,
        'avatar': str(i % 3 + 1),
        'title': 'title' + str(i + 1),
        'text': 'question' * 10,
        'answers_num': i + 1,
        'likes': (i + 10) % 6,
        'answers': [
            {
                'avatar': str(j % 3 + 1),
                'text': 'answer' * 10,
                'likes': (j + 10) % 6,
                'is_right': True if j == 0 else False,
            } for j in range(i + 1)
        ],
        'tags': ['python', 'c++', 'go', 'javascript']
    } for i in range(100)
]


class Profile(User):
    avatar = models.ImageField()


class Tag(models.Model):
    name = models.CharField(max_length=20)


class Question(models.Model):
    user = models.ForeignKey(Profile, models.CASCADE)
    date = models.DateTimeField()
    title = models.CharField(max_length=50)
    text = models.TextField()
    tag = models.ManyToManyField(Tag)


class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, models.PROTECT)
    question = models.ForeignKey(Question, models.CASCADE)


class Answer(models.Model):
    user = models.ForeignKey(Profile, models.PROTECT)
    question = models.ForeignKey(Question, models.CASCADE)
    date = models.DateTimeField()
    text = models.TextField()


class AnswerLike(models.Model):
    user = models.ForeignKey(Profile, models.PROTECT)
    answer = models.ForeignKey(Answer, models.CASCADE)
