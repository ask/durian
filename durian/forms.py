from django import forms
from django.utils.translation import ugettext_lazy as _
from durian.match import mtuplelist_to_matchdict, MATCHABLE_CHOICES
from durian.registry import hooks


class HookConfigForm(forms.Form):
    url = forms.URLField(label=_(u"Listener URL"), required=True)

    def save(self):
        return dict(self.cleaned_data)


class BaseMatchForm(forms.Form):
    _condition_for = None

    def __init__(self, *args, **kwargs):
        self._condition_for = kwargs.pop("condition_for", self._condition_for)
        super(BaseMatchForm, self).__init__(*args, **kwargs)

    def field_to_mtuple(self):
        if not hasattr(self, "cleaned_data"):
            if not self.is_valid():
                raise Exception("FORM IS NOT VALID: %s" % self.errors)

        field = self._condition_for
        return (field,
                self.cleaned_data["%s_cond" % field],
                self.cleaned_data["%s_query" % field])

    def save(self):
        return self.field_to_mtuple()


def create_select_hook_form(*args, **kwargs):
    """Dynamically create a form that has a ``ChoiceField`` listing all the
    hook types registered in the hook registry."""

    class SelectHookForm(forms.Form):
        type = forms.ChoiceField(choices=hooks.as_choices())

    return SelectHookForm(*args, **kwargs)


def create_match_forms(name, provides_args):

    def gen_field_for_name(name):
        return {"%s_cond" % name: forms.ChoiceField(label=name,
                                              choices=MATCHABLE_CHOICES,
                                              widget=forms.Select()),
                "%s_query" % name: forms.CharField(label="",
                                                   required=False,
                                                   initial=""),
        }

    def gen_form_for_field(field):
        dict_ = gen_field_for_name(field)
        dict_["_condition_for"] = field
        return type(name + field, (BaseMatchForm, ), dict_)

    return dict((field, gen_form_for_field(field))
                    for field in provides_args)
