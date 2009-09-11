from durian.models import Listener
from django import forms
from durian.forms import HookConfigForm
from durian.hook import Hook
from durian.registry import hooks


            
# SIMPLE HOOK 

class MyHook(Hook):
    name = "myhook"
hooks.register(MyHook())



def install_listener():
    l = Listener(url="http://localhost:8000/durian/debug/",
             hook=MyHook.name)
    l.save()

# HOOK SENT EVERY TIME USER "ask" COMMITS A CHANGE


# This form is needed to add a listener, so the correct username/password
# is sent when sending updates to twitter.
class TwitterCommitHookConfigForm(HookConfigForm):
    username = forms.CharField(label=_(u"username"))
    password = forms.CharField(label=_(u"password"), required=True, 
                               widget=forms.PasswordInput())
    digest = forms.BooleanField(widget=forms.CheckboxInput())
    active = forms.BooleanField(widget=forms.CheckboxInput())


# This is the hook itself.
class TwitterCommitHook(Hook):
    name = "myuserhook"
    config_form = TwitterCommitHookConfigForm
    providing_args = ["username", "password", "digest", "active"]
hooks.register(TwitterCommitHook)



# This is the function triggering the hook
def commit_change(self, commit_msg, user, revision):

    # ...Do what happens regularly at a commit...

    TwitterCommitHook().send(sender=commit_change, user=user, revision=revision,
                             commit_msg=commit_msg)



# Now let's register a listener.

from celeryhook.match import Startswith
hook = TwitterCommitHook()
form = hook.config_form({"username": "ask", "password": "foo"})
hook.listener(form).match(commit_msg=Startswith("Important change"),
                          username="ask").save()






# A Django view registering a listener.
def add_twitter_hook(request, template_name="myapp/twitterhook.html"):
    hook = TwitterCommitHook()
    context = RequestContext()
    if request.method == "POST":
        form = hook.config_form(request.POST)
        if form.is_valid():
            hook.add_listener_by_form(form)
    else:
        form = hook.config_form()

    context["form"] = form

    return render_to_response(template_name, context_instance=context)


# ### MODEL HOOK


from django.db import signals
from django.contrib.auth.models import User
from durian.hook import ModelHook


userhook = ModelHook(name="user-post-save",
                     model=User,
                     signal=signals.post_save,
                     provides_args=["username", "is_admin"])

# send event when Joe is changed
userhook.listener(
    url="http://where.joe/is/listening").match(
        username="joe").save()

# send event when any user is changed.
userhook.listener(url="http://where.joe/is/listening").save()

# Send event when Joe is admin
userhook.listener(
    url="http://where.joe/is/listening").match(
        username="joe", is_admin=True).save()




joe = User.objects.get(username="joe")
joe.is_admin = True
joe.save()
