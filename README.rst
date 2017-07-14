=============================
MiniCMS
=============================

.. image:: https://badge.fury.io/py/minicms.svg
    :target: https://badge.fury.io/py/minicms

.. image:: https://travis-ci.org/optik/minicms.svg?branch=master
    :target: https://travis-ci.org/optik/minicms

.. image:: https://codecov.io/gh/optik/minicms/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/optik/minicms

Minimalistic, pluggable, developer-friendly CMS package for Django.

Documentation
-------------

The full documentation is at https://minicms.readthedocs.io.

Quickstart
----------

Install MiniCMS::

    pip install minicms

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'minicms.apps.MinicmsConfig',
        ...
    )

Add MiniCMS's URL patterns:

.. code-block:: python

    from minicms import urls as minicms_urls


    urlpatterns = [
        ...
        url(r'^', include(minicms_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
