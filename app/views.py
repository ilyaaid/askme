from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.forms import model_to_dict
from django.http import JsonResponse

from app import models
from app import forms

ITEMS_PRE_PAGE = 10


def paginate(objects_list, request, per_page=ITEMS_PRE_PAGE):
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
                return redirect(request.path + "?page=" +
                                str(models.Answer.objects.get_page(ans, q_obj, ITEMS_PRE_PAGE)) +
                                "#answer-" + str(ans.id))
            else:
                form.add_error(field=None, error="Error in submitting answer")

    context = {
        'question': q_obj,
        'paginator': paginate(models.Answer.objects.get_list(q_obj), request),
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


def get_question_cur_rating(question_id):
    return models.QuestionRating.objects.filter(question_id=question_id, is_like=True).count() - \
        models.QuestionRating.objects.filter(question_id=question_id, is_like=False).count()


@login_required
@require_http_methods(['POST'])
def question_eval(request):
    question_id = request.POST.get('question_id', None)
    if not question_id:
        return HttpResponseNotFound()

    try:
        eval = models.QuestionRating.objects.get(user=request.user, question_id=question_id)
    except models.QuestionRating.DoesNotExist:
        eval = None

    if eval:
        if eval.is_like and request.POST['eval_value'] == '+' or \
                (not eval.is_like) and request.POST['eval_value'] == '-':
            return JsonResponse({
                "new_rating": get_question_cur_rating(question_id),
                "question_id": question_id,
            })
        else:
            eval.delete()

    models.QuestionRating.objects.create(user=request.user, question_id=question_id,
                                         is_like=(request.POST['eval_value'] == '+'))

    return JsonResponse({
        "new_rating": get_question_cur_rating(question_id),
        "question_id": question_id,
    })


def get_answer_cur_rating(answer_id):
    return models.AnswerRating.objects.filter(answer_id=answer_id, is_like=True).count() - \
        models.AnswerRating.objects.filter(answer_id=answer_id, is_like=False).count()


@login_required
@require_http_methods(['POST'])
def answer_eval(request):
    answer_id = request.POST.get('answer_id', None)
    if not answer_id:
        return HttpResponseNotFound()

    try:
        eval = models.AnswerRating.objects.get(user=request.user, answer_id=answer_id)
    except models.AnswerRating.DoesNotExist:
        eval = None

    if eval:
        if eval.is_like and request.POST['eval_value'] == '+' or \
                (not eval.is_like) and request.POST['eval_value'] == '-':
            return JsonResponse({
                "new_rating": get_answer_cur_rating(answer_id),
                "answer_id": answer_id,
            })
        else:
            eval.delete()

    models.AnswerRating.objects.create(user=request.user, answer_id=answer_id,
                                       is_like=(request.POST['eval_value'] == '+'))

    return JsonResponse({
        "new_rating": get_answer_cur_rating(answer_id),
        "answer_id": answer_id,
    })


@login_required
@require_http_methods(['POST'])
def answer_is_right(request):
    try:
        answer = models.Answer.objects.get(id=request.POST["answer_id"])
    except models.Answer.DoesNotExist:
        answer = None
    if not answer:
        return HttpResponseNotFound()

    if request.user != answer.question.user:
        return JsonResponse({
            "answer_id": request.POST["answer_id"],
            "is_checked": answer.is_right,
        })

    answer.is_right = (request.POST["is_checked"] == "true")
    answer.save()

    return JsonResponse({
        "answer_id": request.POST["answer_id"],
        "is_checked": answer.is_right,
    })
