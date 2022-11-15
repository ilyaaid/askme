from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings

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


class Profile(AbstractUser):
    avatar = models.ImageField(upload_to='uploads/avatars')


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)


class QuestionManager(models.Manager):
    def get_new_questions(self):
        return self.order_by('date')

    def get_hot_questions(self):
        q_list = list(self.all())
        pairs = []
        for q in q_list:
            pairs.append({
                'likes': q.likes.count(),
                'q': q,
            })
        pairs = sorted(pairs, key=lambda d: d['likes'], reverse=True)
        return [d['q'] for d in pairs]

    def get_questions_by_tag(self, tag):
        return self.filter(tags__name=tag)


class Question(models.Model):
    user = models.ForeignKey(Profile, models.CASCADE, related_name='questions')
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


class AnswerLike(models.Model):
    user = models.ForeignKey(Profile, models.PROTECT, related_name='answer_likes')
    answer = models.ForeignKey(Answer, models.CASCADE, related_name='likes')
