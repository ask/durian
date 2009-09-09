from django import forms
from django.utils.translation import ugettext_lazy as _


class HookConfigForm(forms.Form):
    url = forms.URLField(_(u"destination URL"), required=True)

    def save(self):
        return dict(self.cleaned_data)
