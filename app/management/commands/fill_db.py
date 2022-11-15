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
    for i in range(num):
        tag = generate_string(i % 7 + 3)
        if tag in used_tags:
            i -= 1
            continue
        used_tags.append(tag)
        tags_list.append(Tag(name=tag))

    Tag.objects.bulk_create(tags_list)


def fill_questions(num):
    questions_list = []
    for user in Profile.objects.all():
        for j in range(int(num / len(Profile.objects.all()))):
            question = Question(user=user,
                                title=generate_string(30),
                                text=generate_text(300),)
            questions_list.append(question)

    Question.objects.bulk_create(questions_list)

    for question in questions_list:
        tags_list = list(Tag.objects.all())
        left_ind = random.randint(0, len(tags_list) - 1)
        for i in range(left_ind, min(len(tags_list), left_ind + random.randint(1, 5))):
            question.tags.add(tags_list[i])


def fill_answers(num):
    answers_list = []
    user_list = list(Profile.objects.all())
    for question in Question.objects.all():
        for j in range(int(num / len(Question.objects.all()))):
            answer = Answer(user=user_list[random.randint(0, len(user_list) - 1)],
                            question=question,
                            text=generate_text(200),)
            answers_list.append(answer)

    Answer.objects.bulk_create(answers_list)


def fill_likes(num):
    answers_like_list = []
    user_list = list(Profile.objects.all())
    for answer in Answer.objects.all():
        left_ind = random.randint(0, len(user_list) - 1)
        for i in range(left_ind, min(len(user_list), left_ind + random.randint(0, 2))):
            answers_like_list.append(AnswerLike(user=user_list[i], answer=answer))

    questions_like_list = []
    user_list = list(Profile.objects.all())
    for question in Question.objects.all():
        left_ind = random.randint(0, len(user_list) - 1)
        for i in range(left_ind, min(len(user_list), left_ind + random.randint(0, 3))):
            questions_like_list.append(QuestionLike(user=user_list[i], question=question))

    AnswerLike.objects.bulk_create(answers_like_list)
    QuestionLike.objects.bulk_create(questions_like_list)


def fill_db_with_ratio(ratio):
    fill_users(ratio)
    fill_tags(ratio)
    fill_questions(ratio * 10)
    fill_answers(ratio * 100)
    fill_likes(ratio*200)


class Command(BaseCommand):
    help = 'fill in the database'

    def handle(self, *args, **options):
        ratio = options['ratio']
        fill_db_with_ratio(ratio)

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help='Введите коэффициент')
