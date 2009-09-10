============================================================================
durian - Webhooks for Django
============================================================================

:Version: 0.0.1

Introduction
============

**NOTE** This software is just in the planning stage and is going to
change drastically. You can follow what is happening here, and is welcome to
help out making it happen, but you should probably not use it for anything
until it has reached an alpha version.

    >>> from django.db import signals
    >>> from django.contrib.auth.models import User
    >>> from durian.hook import ModelHook

    >>> userhook = ModelHook(name="user-post-save",
    ...                      model=User,
    ...                      signal=signals.post_save,
    ...                      provides_args=["username", "is_admin"])

    >>> # send event when Joe is changed
    >>> userhook.listener(
    ...     url="http://where.joe/is/listening").match(
    ...     username="joe").save()

    >>> # send event when any user is changed.
    >>> userhook.listener(url="http://where.joe/is/listening").save()

    >>> # Send event when Joe is admin
    >>> userhook.listener(
    ...     url="http://where.joe/is/listening").match(
    ...         username="joe", is_admin=True).save()

    >>> joe = User.objects.get(username="joe")
    >>> joe.is_admin = True
    >>> joe.save()

View for listening URL:

    >>> from django.http import HttpResponse
    >>> from anyjson import deserialize

    >>> def listens(request):
    ...     payload = deserialize(request.raw_post_data)
    ...     print(payload["what"])
    ...     return HttpResponse("thanks!")


Installation
============

You can install ``durian`` either via the Python Package Index (PyPI)
or from source.

To install using ``pip``,::

    $ pip install durian


To install using ``easy_install``,::

    $ easy_install durian


If you have downloaded a source tarball you can install it
by doing the following,::

    $ python setup.py build
    # python setup.py install # as root

Examples
========

.. Please write some examples using your package here.


License
=======

BSD License


Contact
=======

Ask Solem <askh@opera.com>
