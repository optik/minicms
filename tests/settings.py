# -*- coding: utf-8
import django

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "33333333333333333333333333333333333333333333333333"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "minicms",
]

SITE_ID = 1
