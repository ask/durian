from durian.models import Listener
from celery.utils import get_full_cls_name
from durian.tasks import WebhookSignal
from durian.forms import HookConfigForm
from functools import partial as curry


class Hook(object):
    name = None
    task_cls = WebhookSignal
    timeout = 4
    async = True
    retry = False
    max_retries = 3
    fail_silently = False
    config_form = HookConfigForm
    provides_args = []
    match_form = None

    def __init__(self, name=None, task_cls=None, timeout=None,
            async=None, retry=None, max_retries=None, fail_silently=False,
            config_form=None, provides_args=None, match_form=None, **kwargs):
        self.name = name or self.name or get_full_cls_name(self.__class__)
        self.task_cls = task_cls or self.task_cls
        self.timeout = timeout or self.timeout
        self.async = async or self.async
        self.retry = retry or self.retry
        self.max_retries = max_retries or self.max_retries
        self.fail_silently = fail_silently or self.fail_silently
        self.provides_args = provides_args or self.provides_args
        self.config_form = config_form or self.config_form
        self.match_form = match_form or self.match_form or \
                            gen_match_form(self.provides_args)

    def send(self, sender, **payload):
        payload = prepare_payload(sender, payload)
        apply_ = curry(self._send_signal, sender, payload)
        return map(apply_, self.get_listeners(sender, payload))

    def _send_signal(self, sender, payload, target):
        applier = self.get_applier()
        return applier(args=[target.url, payload], kwargs=self.task_keywords)

    def event_filter(self, sender, payload, match):
        if not match:
            return True
        return deepmatch(match, payload)

    def get_listeners(self, sender, payload):
        possible_targets = Listener.objects.filter(hook=self.name)
        return [target for target in possible_targets
                    if self.event_filter(sender, payload, target.match)]

    def get_applier(self, async=None):
        async = async or self.async
        method = "apply_async" if async else "apply"
        sender = getattr(self.task_cls, method)
        return sender

    def prepare_payload(self, sender, payload):
        return payload

    def add_listener_by_form(self, form, match=None):
        return Listener.objects.create(match, **form.cleaned_data)

    def add_listener(self, url, match={}, **config):
        return Listener.objects.create(url=url, match=match, **dict(config))
    
    def listener(self, form):
        return IntermediateListener(self, form)

    @property
    def task_keywords(self):
        return {"retry": self.retry,
                "max_retries": self.max_retries,
                "fail_silently": self.fail_silently,
                "timeout": self.timeout}


class ModelHook(Hook):
    """
        >>> from django.db import signals
        >>> from django.contrib.auth.models import User

        >>> hook = ModelHook(User, signals.post_save,
        ...                  name="user-post-save",
        ...                  provides_args=["username", "is_admin"])
        >>> joe = User.objects.get(username="joe")
        >>> joe.is_admin = True
        >>> joe.save()

    """
    model = None
    signal = None

    def __init__(self, model=None, signal=None, **kwargs):
        self.model = model or self.model
        self.signal = signal or self.signal
        if not model:
            raise NotImplementedError("ModelHooks requires a model.")
        if self.signal:
            self.connect(model)
        if not self.provides_args:
            self.provides_args = self.get_model_default_fields()
        super(ModelHook, self).__init__(**kwargs)

    def get_model_default_fields(self):
        return [field.name
                    for field in self.model._meta.fields
                        if field.name != self.model._meta.pk.name]

    def prepare_payload(self, sender, payload):
        model_data = dict((field_name, getattr(sender, field_name, None))
                                for field_name in self.provides_args)
        payload.update(model_data)
        return payload

    def connect(self, model):
        self.signal.connect(self.send, sender=model)


class IntermediateListener(object):

    def __init__(self, hook, form):
        self.hook = hook
        self.form = form
        self.match = None

    def match(self, **match):
        self.match = match
        return self

    def save(self):
        return self.hook.add_listener_by_form(self.form, self.match)

