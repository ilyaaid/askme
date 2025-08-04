from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings

from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image

# Create your models here.
from datetime import datetime

def user_directory_path(instance, filename):
    now = datetime.now()
    return 'avatars/{2}/{3}/{4}/user_{0}/{1}'.format(instance.username, filename,
                                                     now.year, now.month, now.day)

def get_default_image():
    image = Image.open(settings.MEDIA_ROOT + '/default.png')
    bytes_io = BytesIO()
    image.save(bytes_io, format='PNG')
    file = InMemoryUploadedFile(bytes_io, None, 'default.png', 'image/png', bytes_io.getbuffer().nbytes, None)
    return file

class Profile(AbstractUser):
    avatar = models.ImageField(blank=True, null=True,
        upload_to=user_directory_path,
        default=get_default_image)


class QuestionManager(models.Manager):
    def get_last(self):
        return self.get_queryset().order_by('-date')

    def get_hot(self):
        return self.get_queryset().all().annotate(
            like_count=models.Count(models.Case(models.When(evals__is_like=True, then=1)))
                       - models.Count(models.Case(models.When(evals__is_like=False, then=1)))) \
            .order_by('-like_count', '-date')

    def get_by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).order_by('-date')


class Question(models.Model):
    user = models.ForeignKey(Profile,
                             related_name='questions',
                             on_delete=models.PROTECT)

    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField()
    body = models.TextField()
    tags = models.ManyToManyField('Tag')
    objects = QuestionManager()

    def __str__(self):
        return self.title


class AnswerManager(models.Manager):
    def get_list(self, question):
        return self.get_queryset().filter(question=question).order_by("-is_right", "date")

    def get_page(self, answer, question, per_page):
        answers = self.get_list(question)
        page = 1
        for i, item in enumerate(answers):
            if item == answer:
                page = i // per_page + 1
                break
        return page

class Answer(models.Model):
    user = models.ForeignKey(Profile,
                             related_name='answers',
                             on_delete=models.PROTECT)
    question = models.ForeignKey(Question,
                                 related_name='answers',
                                 on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    is_right = models.BooleanField(default=False)

    objects = AnswerManager()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.body[:15]+"..."


class Tag(models.Model):
    name = models.CharField(unique=True)

    def __str__(self):
        return self.name


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
