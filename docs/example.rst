=====================
Using example project
=====================

The package includes an example project that you can use for contributing
and testing the features of MiniCMS.

Preparing the example project
-----------------------------

This guide assumes that you have pip and virtualenv installed on your system.

Create and activate the virtual environment::

    $ cd minicms/example
    $ pip install -r requirements.txt
    $ virtualenv env -p=python3
    $ source env/bin/activate

Fire up the Django shell::

    $ python manage.py shell

From the shell, create an admin user:

.. code-block:: python

    from django.contrib.auth.models import User
    user = User.objects.create_user(username="demo", password="demo")
    user.is_superuser = True
    user.is_staff = True
    user.save()
