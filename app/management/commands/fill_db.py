from django.core.management.base import BaseCommand
from app.models import Profile, Tag, Question, QuestionLike, Answer, AnswerLike, User
import random
import string


def generate_username(max_length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(max_length))


def fill_db_with_ratio(ratio):
    user_list = []
    used_usernames = []
    i = 0
    while i < ratio:
        username = generate_username(i % 10 + 5)
        if username in used_usernames:
            i -= 1
            continue
        used_usernames.append(username)
        user_list.append(Profile(username=username,
                                 email=username + '@mail.ru',
                                 password='password',
                                 first_name=username))
        i += 1

    Profile.objects.bulk_create(user_list)


class Command(BaseCommand):
    help = 'fill in the database'

    def handle(self, *args, **options):
        ratio = options['ratio']
        fill_db_with_ratio(ratio)

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help='Введите коэффициент')
