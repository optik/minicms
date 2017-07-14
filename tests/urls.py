# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from minicms.urls import urlpatterns as minicms_urls

# FIXME: should be i18n_patterns?
urlpatterns = [
    url(r'^', include(minicms_urls, namespace='minicms')),
]
