from django.contrib import admin
from app.models import Profile, Tag, Question, QuestionLike, Answer, AnswerLike
# Register your models here.
admin.site.register([Profile, Tag, Question, QuestionLike, Answer, AnswerLike])

