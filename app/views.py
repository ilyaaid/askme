from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.forms import model_to_dict

from app import models
from app import forms


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
    questions = models.Question.objects.get_by_tag(tag_name).order_by('-date')
    print("\t---count of questions with tag " + tag_name + ": " + str(questions.count()))
    context = {
        'paginator': paginate(questions, request),
        'tag_name': tag_name,
    }
    return render(request, 'tag.html', context=context)

@require_http_methods(['POST', 'GET'])
def question(request, question_id: int):
    try:
        q_obj = models.Question.objects.get(id=question_id)
    except models.Question.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'GET':
        form = forms.NewAnswer()
    if request.method == 'POST':
        form = forms.NewAnswer(request.POST, request=request, question=q_obj)
        if form.is_valid():
            ans = form.save()
            if ans:
                return redirect(request.path)
            else:
                form.add_error(field=None, error="Error in submitting answer")
                return redirect(request.path)

    context = {
        'question': q_obj,
        'paginator': paginate(q_obj.answers.order_by("-date", "-is_right"), request),
        'form': form,
    }
    return render(request, 'question.html', context=context)


@require_http_methods(['POST', 'GET'])
def login(request):
    if request.user.is_authenticated:
        return redirect(reverse('settings'))
    if request.method == 'GET':
        form = forms.LoginForm()
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            login_user = auth.authenticate(request, **form.cleaned_data)
            if login_user:
                auth.login(request, login_user)
                if "next" in request.POST:
                    return redirect(request.POST['next'])
                else:
                    return redirect(reverse('index'))
            else:
                form.add_error(field=None, error="User logining error!")

    return render(request, 'login.html', {
        'form': form,
    })


@require_http_methods(['POST', 'GET'])
def signup(request):
    if request.method == 'GET':
        form = forms.NewUserForm()
    if request.method == 'POST':
        form = forms.NewUserForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            if new_user:
                return redirect(reverse('index'))
            else:
                form.add_error(field=None, error="User creating error!")

    return render(request, 'signup.html', {
        'form': form,
    })


@require_http_methods(['GET'])
@login_required
def logout(request):
    auth.logout(request)
    if "next" in request.GET:
        return redirect(request.GET['next'])
    return redirect(reverse('index'))


@require_http_methods(['GET', 'POST'])
@login_required
def settings(request):
    if request.method == 'GET':
        form = forms.SettingForm(initial=model_to_dict(request.user))
    if request.method == 'POST':
        form = forms.SettingForm(request.POST, request.FILES,
                                 initial=model_to_dict(request.user), instance=request.user)
        if form.is_valid():
            user = form.save()
            if user:
                return redirect(reverse('settings'))
            else:
                form.add_error(field=None, error="User saving error!")
    return render(request, 'settings.html', {
        'form': form,
    })

@require_http_methods(['GET', 'POST'])
@login_required
def ask(request):
    if request.method == 'GET':
        form = forms.NewQuestionForm()
    if request.method == 'POST':
        form = forms.NewQuestionForm(request.POST, request=request)
        if form.is_valid():
            q = form.save()
            if q:
                return redirect('question', question_id=q.id)
            else:
                form.add_error(field=None, error="Error in question form!")
    return render(request, 'ask.html', {
        "form": form
    })
