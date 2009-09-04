from django.db import models
from django.utils.translation import ugettext_lazy as _
from celery.fields import PickledObjectField
from celery.serialization import pickle

def everything(sender, **payload):
    return True


class Listener(models.Model):
    hook = models.CharField(_("hook"), max_length=255,
                            help_text=_("Connects to hook"))
    url = models.URLField(verify_exists=False,
                          help_text=_("The URL I'm listening at."))
    predicate = PickledObjectField(default=pickle.dumps(everything))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def match(self, sender, **arguments):
        return bool(self.predicate(sender, **arguments))