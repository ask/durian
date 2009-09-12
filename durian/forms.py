from django import forms
from django.utils.translation import ugettext_lazy as _
from durian.match import mtuplelist_to_matchdict, MATCHABLE_CHOICES
from durian.registry import hooks


class HookConfigForm(forms.Form):
    """Form for the default hook config.

    By default listeners only needs an URL, if you want custom configuration
    keys you can subclass this form and use that as the hooks
    :attr:`durian.event.Hook.config_form` attribute.

    """
    url = forms.URLField(label=_(u"Listener URL"), required=True)

    def save(self):
        return dict(self.cleaned_data)


def create_select_hook_form(*args, **kwargs):
    """Dynamically create a form that has a ``ChoiceField`` listing all the
    hook types registered in the hook registry."""

    class SelectHookForm(forms.Form):
        type = forms.ChoiceField(choices=hooks.as_choices())

    return SelectHookForm(*args, **kwargs)


class BaseMatchForm(forms.Form):
    """Base class for match forms.

    Supports converting the form to a match tuple.

    """
    _condition_for = None

    def __init__(self, *args, **kwargs):
        self._condition_for = kwargs.pop("condition_for", self._condition_for)
        super(BaseMatchForm, self).__init__(*args, **kwargs)

    def field_to_mtuple(self):
        """Convert the form to a match tuple."""
        if not hasattr(self, "cleaned_data"):
            if not self.is_valid():
                # FIXME
                raise Exception("FORM IS NOT VALID: %s" % self.errors)

        field = self._condition_for
        return (field,
                self.cleaned_data["%s_cond" % field],
                self.cleaned_data["%s_query" % field])

    def save(self):
        return self.field_to_mtuple()


def create_match_forms(name, provides_args):
    """With a list of supported arguments, generate a list of match
    forms for these.

    E.g. if the supported arguments is ``["name", "address"]``, it will
    generate forms like these::

        Name: SELECT:[any|exact|starts with|ends with|contains] [ query ]
        Address: SELECT:[any|exact|starts with|ends with|contains] [ query ]

    When these form are feeded with data they can be converted to a match
    dict like:

        >>> {"name": Startswith("foo"), "address": Endswith("New York")}

    """
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
