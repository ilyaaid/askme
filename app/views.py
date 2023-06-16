from django.shortcuts import render
from app import models
from django.http import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator


def paginate(objects_list, request, per_page=10):
    p = Paginator(objects_list, per_page)
    return p


def index(request):
    questions = models.Question.objects.get_last()
    print("\t---count of new questions: " + str(questions.count()))
    context = {
        'paginator': paginate(questions, request),
    }
    return render(request, 'index.html', context=context)


def hot(request):
    questions = models.Question.objects.get_hot()
    print("\t---count of popular questions: " + str(questions.count()))
    context = {
        'paginator': paginate(questions, request),
    }
    return render(request, 'hot.html', context=context)


def tag(request, tag_name):
    questions = models.Question.objects.get_by_tag(tag_name)
    print("\t---count of questions with tag " + tag_name + ": "+ str(questions.count()))
    context = {
        'paginator': paginate(questions, request),
        'tag_name': tag_name,
    }
    return render(request, 'tag.html', context=context)


def question(request, question_id: int):
    q = models.Question.objects.get(id=question_id)
    context = {
        'question': q,
        'paginator': paginate(q.answers.all(), request),
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



