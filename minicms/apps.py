# -*- coding: utf-8
from django.apps import AppConfig


class MinicmsConfig(AppConfig):
    name = 'minicms'

    def ready(self):
        import minicms.signals  # noqa
