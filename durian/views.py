import sys
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from anyjson import deserialize
from durian.forms import create_select_hook_form
from durian.registry import hooks


def select(request, template_name="durian/select_hook.html"):
    context = RequestContext(request)
    context["title"] = _("Select event")
    context["select_hook_form"] = create_select_hook_form()
    return render_to_response(template_name, context_instance=context)

def get_hook(hook_type):
    if hook_type not in hooks:
        raise Http404(_("Unknown hook type: %s" % hook_type))
    return hooks[hook_type]

def create(request, template_name="durian/create_hook.html"):
    context = RequestContext(request)
    if request.method == "POST":
        hook = get_hook(request.POST["type"])
        config_form = hook.config_form(request.POST)
        if config_form.is_valid():
            matchdict = hook.apply_match_forms(request.POST)
            hook.add_listener_by_form(config_form, match=matchdict)
            return HttpResponse("Listener Created!")
    else:
        hook = get_hook(request.GET["type"])
        config_form = hook.config_form()

    match_forms = hook.get_match_forms()
    context["title"] = " ".join([
                _("Create"), hook.name.capitalize(), _("Listener")])
    context["hook_type"] = hook.name
    context["hook_name"] = hook.name
    context["match_forms"] = match_forms
    context["config_form"] = config_form
    return render_to_response(template_name, context_instance=context)


def debug(request):
    sys.stderr.write(str(request.get_full_path()) + "\n")
    sys.stderr.write(str(request.raw_post_data) + "\n")
    sys.stderr.write(str(request.POST) + "\n")
    sys.stderr.write(str(deserialize(request.raw_post_data)) + "\n")
    return HttpResponse("Thanks!")
