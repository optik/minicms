from django.conf.urls import url
from . import views

app_name = 'minicms'
urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^(?P<path>.+)/$', views.page, name='page'),
]
