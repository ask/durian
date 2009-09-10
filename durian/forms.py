from django import forms
from django.utils.translation import ugettext_lazy as _
from durian.match import mtuplelist_to_matchdict, MATCHABLE_CHOICES


class HookConfigForm(forms.Form):
    url = forms.URLField(_(u"destination URL"), required=True)

    def save(self):
        return dict(self.cleaned_data)


class BaseMatchForm(forms.Form):
    _provides_args = []

    def __init__(self, *args, **kwargs):
        self._provides_args = kwargs.pop("provides_args", self._provides_args)
        super(BaseMatchForm, self).__init__(*args, **kwargs)

    def to_mtuplelist(self):
        return map(self.field_to_mtuple, self._provides_args)

    def field_to_mtuple(self, field):
        return (field,
                self.cleaned_data("%s_cond" % field),
                self.cleaned_data("%s_query" % field))

    def save(self):
        return self.to_mtuplelist() 


def gen_match_form(name, provides_args):
    def gen_field_for_name(name):
        return {name: forms.CharField(required=True, default=name),
                "%s_cond": forms.ChoiceField(choices=MATCHABLE_CHOICES,
                                              widget=forms.Select(),
                                              label=_("condition")),
                "%s_query": forms.CharField(required=True, default="")}
    dict_ = dict(_provides_args=provides_args)
    [dict_.extend(gen_field_for_name(name)) for name in provides_args]
        
    return type(name, (BaseMatchForm, ), dict_)
