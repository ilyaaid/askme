from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from app.models import Profile, Question, Answer, Tag, QuestionRating, AnswerRating

from random import choice, randint
from string import ascii_lowercase

lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ' \
        'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. ' \
        'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. ' \
        'Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'


def random_string(n):
    return ''.join(choice(ascii_lowercase) for i in range(n))


def fill_users(size):
    profiles = []
    usernames = set()
    password = make_password('password')
    for i in range(size):
        username = random_string(5)
        if username in usernames:
            size += 1
            continue
        usernames.add(username)

        profiles.append(Profile(username=username, password=password,
                                avatar='avatars/default' + str(i % 3) + '.jpg'))

    Profile.objects.bulk_create(profiles)


def fill_tags(size):
    tags_models = []
    tags = set()
    for i in range(size):
        tag = random_string(4)
        if tag in tags:
            size += 1
            continue
        tags.add(tag)

        tags_models.append(Tag(name=tag))

    Tag.objects.bulk_create(tags_models)


def fill_questions(size):
    profiles = list(Profile.objects.all())
    tags = list(Tag.objects.all())

    questions = []
    question_tag = []
    for i in range(size):
        q = Question(title='title_' + str(i), body=lorem,
                     user=profiles[i % len(profiles)])
        i_tags = i % len(tags)
        for tag_obj in [tags[i_tags], tags[i_tags - 1], tags[i_tags - 2]]:
            question_tag.append(Question.tags.through(question_id=i + 1, tag_id=tag_obj.id))
        questions.append(q)

    Question.objects.bulk_create(questions)
    Question.tags.through.objects.bulk_create(question_tag)


def fill_answers(size):
    profiles = list(Profile.objects.all())
    questions = list(Question.objects.all())

    cur_size = 0
    answers = []
    used_questions = set()
    while len(used_questions) < len(questions):
        q_rand_i = randint(0, len(questions) - 1)
        if q_rand_i in used_questions:
            continue
        used_questions.add(q_rand_i)
        n = randint(0, 30)
        for j in range(n):
            rand_user = randint(0, len(profiles) - 1)
            answers.append(Answer(user=profiles[rand_user], question=questions[q_rand_i],
                                  body=lorem, is_right=(j == 0)))
        cur_size += n
        if cur_size >= size:
            break

    Answer.objects.bulk_create(answers)


def fill_question_evals(size):
    profiles = list(Profile.objects.all())
    questions = list(Question.objects.all())

    cur_size = 0
    question_evals = []
    is_like = True
    used_questions = set()
    while len(used_questions) < len(questions):
        q_rand_i = randint(0, len(questions) - 1)
        if q_rand_i in used_questions:
            continue
        used_questions.add(q_rand_i)
        n = randint(0, 30)
        profile_ind = randint(0, len(profiles) - 1)
        for j in range(n):
            question_evals.append(QuestionRating(user=profiles[profile_ind],
                                                 question=questions[q_rand_i],
                                                 is_like=is_like))
            k = randint(0, 3)
            if k == 0:
                is_like = not is_like
            profile_ind = (profile_ind + 1) % len(profiles)
        cur_size += n
        if cur_size >= size:
            break

    QuestionRating.objects.bulk_create(question_evals)


def fill_answer_evals(size):
    profiles = list(Profile.objects.all())
    answers = list(Answer.objects.all())

    cur_size = 0
    answer_evals = []
    is_like = True
    used_answers = set()
    while len(used_answers) < len(answers):
        ans_rand_i = randint(0, len(answers) - 1)
        if ans_rand_i in used_answers:
            continue
        used_answers.add(ans_rand_i)
        n = randint(0, 10)
        profile_ind = randint(0, len(profiles) - 1)
        for j in range(n):
            answer_evals.append(AnswerRating(user=profiles[profile_ind],
                                             answer=answers[ans_rand_i],
                                             is_like=is_like))
            k = randint(0, 3)
            if k == 0:
                is_like = not is_like
            profile_ind = (profile_ind + 1) % len(profiles)
        cur_size += n
        if cur_size >= size:
            break

    AnswerRating.objects.bulk_create(answer_evals)


def fill_with_ratio(ratio):
    fill_users(ratio)
    # fill_tags(ratio)
    # fill_questions(ratio * 10)
    # fill_answers(ratio * 100)
    # fill_question_evals(ratio * 100)
    # fill_answer_evals(ratio * 100)


class Command(BaseCommand):
    help = "Filling the database"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help="Введите коэффициент заполнения")

    def handle(self, *args, **options):
        ratio = options.get('ratio')
        self.stdout.write("Коэффициент: " + str(ratio))
        fill_with_ratio(ratio)
