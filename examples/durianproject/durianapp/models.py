from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from durian.event import ModelHook
from durian.registry import hooks


class Person(models.Model):
    name = models.CharField(_(u"name"), blank=False, max_length=200)
    address = models.CharField(_(u"address"), max_length=200)
    secret = models.CharField(_(u"secret"), max_length=200)


class PersonHook(ModelHook):
    name = "person"
    model = Person
    signal = signals.post_save
    provides_args = ["name", "address"]
    async = False
hooks.register(PersonHook)
