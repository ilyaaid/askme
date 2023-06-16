from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models


# Register your models here.

admin.site.register(models.Profile)
admin.site.register(models.Question)
admin.site.register(models.Answer)
admin.site.register(models.QuestionRating)
admin.site.register(models.AnswerRating)
admin.site.register(models.Tag)

