============
Installation
============

At the command line::

    $ easy_install minicms

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv minicms
    $ pip install minicms


Configuration
=============

MiniCMS uses url internationalization built into django. To be able to access
content pages, make sure you do the following:

Add LocaleMiddleware to the middleware list right after SessionMiddleware and
before CommonMiddleware:

.. code-block:: python

    MIDDLEWARE = [
       'django.contrib.sessions.middleware.SessionMiddleware',
       'django.middleware.locale.LocaleMiddleware',
       'django.middleware.common.CommonMiddleware',
    ]

Append the following to your root urls.py (set **prefix_default_language** according
to your preference):

.. code-block:: python

    # existing url configuration ...

    urlpatterns += i18n_patterns(
        url(r'', include('minicms.urls', namespace='minicms')),
        prefix_default_language=False)


Using CKEditor for content editing
----------------------------------

Install django-ckeditor package::

    $ pip install django-ckeditor

Add ckeditor to your INSTALLED_APPS setting.

Add the editor selection option to your settings.py file:

.. code-block:: python

    CMS_WYSIWYG_EDITOR = 'ckeditor'

For detailed information about installing and configuring CKEditor, refer to
`django-ckeditor project docs <http://https://github.com/django-ckeditor/django-ckeditor/>`_.

Using TinyMCE for content editing
----------------------------------

Install django-tinymce package::

    $ pip install django-tinymce

Add tinymce to your INSTALLED_APPS setting.

Add the editor selection option to your settings.py file:

.. code-block:: python

    CMS_WYSIWYG_EDITOR = 'tinymce'

You may want to configure the default options for the editor right off the bat:

.. code-block:: python

    TINYMCE_DEFAULT_CONFIG = {
        'theme': "simple",
        'relative_urls': False,
        'width': '100%',
        'height': 300
    }

For detailed information about installing and configuring TinyMCE,
refer to `django-tinymce project docs <http://https://github.com/aljosa/django-tinymce/>`_.
