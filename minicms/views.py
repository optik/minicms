from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render
from django.utils.translation import get_language
from .models import Page


def homepage(request):
    homepage = Page.objects.get(is_homepage=True)
    return page(request, homepage.path, page=homepage)


def page(request, path, page=None):
    page = page or Page.objects.get(path=path)
    template = page.template or 'content/page.html'
    return render(request, template, {'page': page})
