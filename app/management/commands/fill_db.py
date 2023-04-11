from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Tag, Question, QuestionLike, Answer, AnswerLike

from django.conf import settings

import random
import string
import datetime


def generate_string(max_length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(max_length))


def generate_text(max_length):
    cur_length = 0
    text = ""
    while cur_length < max_length:
        str_length = random.randint(3, 7)
        text += generate_string(min(str_length, max_length - cur_length))
        cur_length += str_length + 1
        text += " "
    return text


def fill_users(num):
    user_list = []
    used_usernames = []
    i = 0
    while i < num:
        username = generate_string(i % 10 + 5)
        if username in used_usernames:
            i -= 1
            continue
        used_usernames.append(username)
        user_list.append(Profile(username=username,
                                 email=username + '@mail.ru',
                                 password='password',
                                 first_name=username,
                                 avatar='uploads/avatars/user' + str(i % 4 + 1) + '.jpg'))
        i += 1

    Profile.objects.bulk_create(user_list)


def fill_tags(num):
    tags_list = []
    used_tags = []
    i = 0
    while i < num:
        tag = generate_string(i % 7 + 3)
        if tag in used_tags:
            i -= 1
            continue
        used_tags.append(tag)
        tags_list.append(Tag(name=tag))
        i += 1

    Tag.objects.bulk_create(tags_list)


def fill_questions(num):
    questions_list = []
    tags_count = len(Tag.objects.all())
    profiles_count = len(Profile.objects.all())
    text = generate_text(300)
    title = generate_string(30)
    for user in Profile.objects.all():
        for j in range(int(num / profiles_count)):
            question = Question(user=user,
                                title=str(len(questions_list)) + title,
                                text=text, )
            questions_list.append(question)

    Question.objects.bulk_create(questions_list)

    for question in questions_list:
        tags_left_ind = random.randint(0, tags_count - 1)
        question.tags.set(Tag.objects.all()[tags_left_ind: min(tags_count, tags_left_ind + 3)])


def fill_answers(num):
    answers_list = []
    text = generate_text(200)
    for user in Profile.objects.all():
        for question in Question.objects.all():
            answers_list.append(
                Answer(user=user,
                       question=question,
                       text=text,
                       is_right=False))
            num -= 1
            if num <= 0:
                break
        if num <= 0:
            break

    Answer.objects.bulk_create(answers_list)


def fill_likes(num):
    i = num
    answers_like_list = []
    for user in Profile.objects.all():
        for answer in Answer.objects.all():
            answers_like_list.append(AnswerLike(user=user, answer=answer))
            i -= 1
            if i <= 0:
                break
            if len(answers_like_list) == 100000:
                AnswerLike.objects.bulk_create(answers_like_list)
                answers_like_list = []
        if i <= 0:
            break

    AnswerLike.objects.bulk_create(answers_like_list)

    i = num
    questions_like_list = []
    for user in Profile.objects.all():
        for question in Question.objects.all():
            questions_like_list.append(QuestionLike(user=user, question=question))
            i -= 1
            if i <= 0:
                break
            if len(questions_like_list) == 100000:
                QuestionLike.objects.bulk_create(questions_like_list)
                questions_like_list = []
        if i <= 0:
            break

    QuestionLike.objects.bulk_create(questions_like_list)


def fill_db_with_ratio(ratio):
    fill_users(ratio)
    fill_tags(ratio)
    fill_questions(ratio * 10)
    fill_answers(ratio * 100)
    fill_likes(ratio * 200)


class Command(BaseCommand):
    help = 'fill in the database'

    def handle(self, *args, **options):
        ratio = options['ratio']
        fill_db_with_ratio(ratio)

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help='Введите коэффициент')
