from django.db import models

from django.contrib.auth.models import User, AbstractUser

# Create your models here.

class Profile(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


class QuestionManager(models.Manager):
    def get_last(self):
        return self.get_queryset().order_by('-date')

    def get_hot(self):
        return self.get_queryset().all().annotate(
            like_count=models.Count(models.Case(models.When(evals__is_like=True, then=1)))
                       - models.Count(models.Case(models.When(evals__is_like=False, then=1))))\
            .order_by('-like_count')

    def get_by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).order_by('-date')


class Question(models.Model):
    user = models.ForeignKey(Profile,
                             related_name='questions',
                             on_delete=models.PROTECT)

    date = models.DateTimeField(auto_now_add=True)
    title = models.TextField()
    body = models.TextField()
    tags = models.ManyToManyField('Tag')
    objects = QuestionManager()


class Answer(models.Model):
    user = models.ForeignKey(Profile,
                             related_name='answers',
                             on_delete=models.PROTECT)
    question = models.ForeignKey(Question,
                                 related_name='answers',
                                 on_delete=models.PROTECT)

    body = models.TextField()
    is_right = models.BooleanField()


class Tag(models.Model):
    name = models.TextField(unique=True)


class QuestionRating(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='evals', on_delete=models.CASCADE)
    is_like = models.BooleanField()

    class Meta:
        unique_together = ['user', 'question']


class AnswerRating(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name='evals', on_delete=models.CASCADE)
    is_like = models.BooleanField()

    class Meta:
        unique_together = ['user', 'answer']
