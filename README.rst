============================================================================
durian - Web Hooks for Django
============================================================================

:Version: 0.1.0

.. image:: http://cloud.github.com/downloads/ask/durian/webhooks-logo.png

Introduction
============

We want the web sites we create to communicate with other sites. To enable
this we give the clients an URL they can connect to. This is fine for most
requests, but let's take a look at RSS.

RSS publishes your articles for others to subscribe to. Whenever you have a
new article to publish you add it to the RSS document available at an URL
like::

    http://example.com/articles.rss

The client connects to this URL, say, every 20 minutes to check if there's
something new. And if there is something new, it has to re-download the entire
content, even if it already has some of the articles from before.
We call this communication method `pulling`_.

This is where web hooks (or HTTP callbacks) comes in, instead of giving the
clients an URL they can connect to, the clients *give you an URL* you connect
to every time there is something to update.

By `pushing`_ instead of pulling the updates, both you
and your clients saves bandwidth, sometimes by a lot.

.. image:: http://cloud.github.com/downloads/ask/durian/webhook-callback2.png

You can read more about web hooks at the `Web Hooks Blog`_.
These slides by Jeff Lindsay is a good introduction to the subject:
`Using Web Hooks`_.

.. _`Web Hooks Blog`: http://blog.webhooks.org
.. _`Using Web Hooks`:
    http://www.slideshare.net/progrium/using-web-hooks
.. _`pushing`: http://en.wikipedia.org/wiki/Push_technology
.. _`pulling`: http://en.wikipedia.org/wiki/Pull_technology

**NOTE** This software is just in the planning stage and is going to
change drastically. You can follow what is happening here, and is welcome to
help out making it happen, but you should probably not use it for anything
until it has reached an alpha version.


Examples
========

Creating an event with a model and a signal
-------------------------------------------

In this example we'll be creating a ModelHook.

A ModelHook is a hook which takes a Django model and signal.
So whenever that signal is fired, the hook is also triggered.

You can specify which of the model fields you want to pass on to the listeners
via the ``provides_args`` attribute.


First let's create a simple model of a person storing the persons
name, address and a secret field we don't want to pass on to listeners:

    >>> from django.db import models
    >>> from django.utils.translation import ugettext_lazy as _

    >>> class Person(models.Model):
    ...     name = models.CharField(_(u"name"), blank=False, max_length=200)
    ...     address = models.CharField(_(u"address"), max_length=200)
    ...     secret = models.CharField(_(u"secret"), max_length=200)


Now to the hook itself. We subclass the ModelHook class and register it in
the global webhook registry. For now we'll set ``async`` to False, this means
the tasks won't be sent to ``celeryd`` but executed locally instead. In
production you would certainly want the dispatch to be asynchronous.
    
    >>> from durian.event import ModelHook
    >>> from durian.registry import hooks
    >>> from django.db.models import signals

    
    >>> class PersonHook(ModelHook):
    ...     name = "person"
    ...     model = Person
    ...     signal = signals.post_save
    ...     provides_args = ["name", "address"]
    ...     async = False
    >>> hooks.register(PersonHook)

Now we can create ourselves some listeners. They can be created manually
or by using the web-interface. A listener must have a URL, which is the
destination callback the signal is sent to, and you can optionally filter
events so you only get the events you care about.

    >>> # send event when person with name Joe is changed/added.
    >>> PersonHook().listener(
    ...     url="http://where.joe/is/listening").match(
    ...     name="Joe").save()

    >>> # send event whenever a person with a name that starts with the
    >>> # letter "J" is changed/added:
    >>> from durian.match import Startswith
    >>> PersonHook().listener(
    ...     url="http://where.joe/is/listening").match(
    ...     name=Startswith("J").save()

    >>> # send event when any Person is changed/added.
    >>> PersonHook().listener(url="http://where.joe/is/listening").save()

The filters can use special matching classes, as you see with the
``Startswith`` above. See `Matching classes`_ for a list of these.

In this screenshot you can see the view for selecting the person event:

.. image:: 
    http://cloud.github.com/downloads/ask/durian/durian-shot-select_event.png

and then creating a listener for that event:

.. image::
    http://cloud.github.com/downloads/ask/durian/durian-shot-create_listenerv2.png


Creating custom hooks
---------------------

Sometimes you'd like to create hooks for something else than a model.
If there's already a Django signal you want to bind to there is the
``SignalHook``. Otherwise you can send your own signal by creating a custom
``Hook``.
    
The only required attribute of a hook is the name, so it can be uniquely
identified in the hook registry.

There are two ways of defining a hook, either by instantiation a Hook
class, or by subclassing one. You can register a hook instance, or a hook
class, it doesn't matter as long as the name is different:

    >>> from durian.registry import hooks

    >>> # Defining a hook by instantiating a hook class:
    >>> myhook = Hook(name="myhook")
    >>> hooks.register(myhook)

    >>> # Defining a hook by subclassing a hook class:
    >>> class MyHook(Hook):
    ...     name = "myhook"
    >>> hooks.register(MyHook)


These also supports the ``provides_args`` attribute which can automatically
generate event filter forms.

See the API reference for a complete list of ``Hook`` arguments and
attributes.

Triggering a hook is simple by using the ``send`` method::

    >>> class MyHook(Hook):
    ...    name = "myhook"
    ...    provides_args = ["name", "address"]
    ...    async = False
    >>> hooks.register(MyHook)

    >>> MyHook().send(sender=None,
    ...               name="George Constanza", address="New York City")


View for listening URL
----------------------

    >>> from django.http import HttpResponse
    >>> from anyjson import deserialize

    >>> def listens(request):
    ...     payload = deserialize(request.raw_post_data)
    ...     print(payload["name"])
    ...     return HttpResponse("thanks!")


Matching classes
----------------


    * Any()
        Matches anything. Even if the field is not sent at all.   

    * Is(pattern)
        Strict equality. The values must match precisely.

    * Startswith(pattern)
        Matches if the string starts with the given pattern.

    * Endswith(pattern)
        Matches if the string ends with the given pattern

    * Contains(pattern)
        Matches if the string contains the given pattern.

    * Like(regex)
        Match by a regular expression.



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
