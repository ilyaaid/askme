from django.shortcuts import render
from app.models import Question, Answer, Tag, AnswerLike, QuestionLike
from django.http import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator


def paginate(objects_list, request, per_page=10):
    p = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    return page_obj


def index(request):
    questions = Question.objects.get_new_questions()
    context = {
        'questions': questions,
        'page_obj': paginate(questions, request),
    }
    return render(request, 'index.html', context=context)


def hot(request):
    questions = Question.objects.get_hot_questions()
    context = {
        'questions': questions,
        'page_obj': paginate(questions, request),
    }
    return render(request, 'hot.html', context=context)


def tag(request, tag_name):
    questions = Question.objects.get_questions_by_tag(tag_name)
    context = {
        'questions': questions,
        'page_obj': paginate(questions, request),
        'tag': tag_name,
    }
    return render(request, 'tag.html', context=context)


def question(request, question_id: int):
    try:
        q = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponseNotFound()

    context = {
        'question': q,
        'page_obj': paginate(q.answers.all(), request),
    }
    return render(request, 'question.html', context=context)


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def settings(request):
    return render(request, 'settings.html')


def ask(request):
    return render(request, 'ask.html')
