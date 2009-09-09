from celeryhooks.models import Listener
from celeryhooks.hooks import Hook
from django import forms
from celeryhooks.forms import HookConfigForm


            
# SIMPLE HOOK 

class MyHook(Hook):
    name = "myhook"



def install_listener():
    l = Listener(url="http://localhost:8000/celeryhooks/debug/",
             hook=MyHook.name)
    l.save()

# HOOK SENT EVERY TIME USER "ask" COMMITS A CHANGE


# This form is needed to add a listener, so the correct username/password
# is sent when sending updates to twitter.
class TwitterHookConfigForm(HookConfigForm):
    username = forms.CharField(label=_(u"username"))
    password = forms.CharField(label=_(u"password"), required=True, 
                               widget=forms.PasswordInput())
    digest = forms.BooleanField(widget=forms.CheckboxInput())
    active = forms.BooleanField(widget=forms.CheckboxInput())


# This is the hook itself.
class TwitterHook(Hook):
    name = "myuserhook"
    config_form = TwitterHookConfigForm



# This is the function triggering the hook
def commit_change(self, commit_msg, user, revision):

    # ...Do what happens regularly at a commit...

    TwitterHook().send(sender=commit_change, user=user, revision=revision,
                       commit_msg=commit_msg)



# Now let's register a listener.

from celeryhook.match import Startswith
hook = TwitterHook()
form = hook.config_form({"username": "ask", "password": "foo"})
hook.add_listener_by_form(form=form,
                         match={"commit_msg": Startswith("Important change"))


# A Django view registering a listener.
def add_twitter_hook(request, template_name="myapp/twitterhook.html"):
    hook = TwitterHook()
    context = RequestContext()
    if request.method == "POST":
        form = hook.config_form(request.POST)
        if form.is_valid():
            hook.add_listener_by_form(form)
    else:
        form = hook.config_form()

    context["form"] = form

    return render_to_response(template_name, context_instance=context)
