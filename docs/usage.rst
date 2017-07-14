=====
Usage
=====

To use MiniCMS in a project, add it to your `INSTALLED_APPS`:

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
