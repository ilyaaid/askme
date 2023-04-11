from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.aggregates import Count

# Create your models here.


class Profile(AbstractUser):
    avatar = models.ImageField(upload_to='uploads/avatars')


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)


class QuestionManager(models.Manager):
    def get_new_questions(self):
        return self.order_by('date')

    def get_hot_questions(self):
        print(self.annotate(likes_count=Count('likes')).order_by('likes_count').query)
        return self.annotate(likes_count=Count('likes')).order_by('likes_count')

    def get_questions_by_tag(self, tag):
        return self.filter(tags__name=tag)


class Question(models.Model):
    user = models.ForeignKey(Profile, models.PROTECT, related_name='questions')
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    text = models.TextField()
    tags = models.ManyToManyField(Tag)

    objects = QuestionManager()


class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, models.PROTECT, related_name='question_likes')
    question = models.ForeignKey(Question, models.CASCADE, related_name='likes')


class Answer(models.Model):
    user = models.ForeignKey(Profile, models.PROTECT, related_name='answers')
    question = models.ForeignKey(Question, models.CASCADE, related_name='answers')
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    is_right = models.BooleanField(default=False)


class AnswerLike(models.Model):
    user = models.ForeignKey(Profile, models.PROTECT, related_name='answer_likes')
    answer = models.ForeignKey(Answer, models.CASCADE, related_name='likes')
