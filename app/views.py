from django.shortcuts import render
from app import models
from django.http import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator


def paginate(objects_list, request, per_page=10):
    p = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    return page_obj


def index(request):
    context = {
        'questions': models.QUESTIONS,
        'page_obj': paginate(models.QUESTIONS, request),
    }
    return render(request, 'index.html', context=context)


def hot(request):
    context = {
        'questions': models.QUESTIONS,
        'page_obj': paginate(models.QUESTIONS, request),
    }
    return render(request, 'hot.html', context=context)


def tag(request, tag_name):
    context = {
        'questions': models.QUESTIONS,
        'page_obj': paginate(models.QUESTIONS, request),
        'tag_name': tag_name,
    }
    return render(request, 'tag.html', context=context)


def question(request, question_id: int):
    if question_id >= len(models.QUESTIONS):
        return HttpResponseNotFound()
    context = {
        'question': models.QUESTIONS[question_id],
        'page_obj': paginate(models.QUESTIONS[question_id]['answers'], request),
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



