from django.db import models
from django.utils.translation import ugettext_lazy as _
from celery.fields import PickledObjectField
from celery.serialization import pickle


class Listener(models.Model):
    hook = models.CharField(_("hook"), max_length=255,
                            help_text=_("Connects to hook"))
    url = models.URLField(verify_exists=False,
                          help_text=_("The URL I'm listening at."))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    config = PickledObjectField(_("configuration"), default=pickle.dumps({}),
                                help_text=_("Hook specific configuration."))
    match = PickledObjectField(_(u"conditions"), default=pickle.dumps({}),
                                help_text=_("Hook specific event filter"))

    class Meta:
        verbose_name = _("listener")
        verbose_name_plural = _("listeners")
    
    def __unicode__(self):
        return "%s match:%s config:%s" % (
                self.url, self.match, self.config)
