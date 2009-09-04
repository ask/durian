============================================================================
celery-hooks - Webhooks using Celery
============================================================================

:Version: 0.0.1

Introduction
============


    >>> from celeryhooks.hooks import Hook, Listener

    >>> myhook = Hook(name="my-simple-hook", retry=True, async=True)

    >>> def predicate_username_matches(sender, **kwargs):
    ...     if sender.username == "ask":
    ...         return True

    >>> def install_listener():
    ...     Listener.objects.create(url="http://where/ask/listens",
    ...                             predicate=predicate_username_matches,
    ...                             hook=myhook.name)
    ...

    >>> if __name__ = "__main__":
    ...     install_listener()
    ...     from django.contrib.auth.models import User
    ...     ask = User.objects.get(username="ask")
    ...     myhook.send(ask, what="changed")


view:

    >>> from django.http import HttpResponse
    >>> from anyjson import deserialize

    >>> def listens(request):
    ...     payload = deserialize(request.raw_post_data)
    ...     print(payload["what"])
    ...     return HttpResponse("thanks!")


Installation
============

You can install ``celeryhooks`` either via the Python Package Index (PyPI)
or from source.

To install using ``pip``,::

    $ pip install celeryhooks


To install using ``easy_install``,::

    $ easy_install celeryhooks


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
