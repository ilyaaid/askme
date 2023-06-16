from django import template

register = template.Library()

@register.filter
def count_rating(evals):
    return evals.filter(is_like=True).count() - evals.filter(is_like=False).count()

@register.filter
def get_page_obj(paginator, request):
    return paginator.get_page(request.GET.get('page'))

@register.inclusion_tag('inc/paginator.html')
def show_paginator(paginator, request):
    page_obj = paginator.get_page(request.GET.get('page'))
    return {'page_obj': page_obj,}

