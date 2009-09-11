from durian.models import Listener
from celery.utils import get_full_cls_name, gen_unique_id
from durian.tasks import WebhookSignal
from durian.forms import HookConfigForm, create_match_forms
from durian.match.strategy import deepmatch
from durian.match import mtuplelist_to_matchdict
from functools import partial as curry


class Hook(object):
    """A Web Hook Event.

    :keyword name: See :attr:`name`.
    :keyword provides_args: See :attr:`provides_args`.
    :keyword config_form: See :attr:`config_form`.
    :keyword timeout: See :attr:`timeout`.
    :keyword async: See :attr:`async`.
    :keyword retry: See :attr:`retry`.
    :keyword max_retries: See :attr:`max_retries`.
    :keyword fail_silently: See :attr:`fail_silently`.
    :keyword task_cls: See :attr:`task_cls`.
    :keyword match_forms: See :attr:`match_forms`

    .. attribute:: name

        The name of the hook.
        
        If not provided this will be automatically generated using the class
        module and name, if you want to use this feature you can't use
        relative imports.

    .. attribute:: provides_args

        The list of arguments the event provides. This is the standard
        list of arguments you are going to pass on to :meth:`send`, used to
        generate the filter events form (:attr:`match_forms`).

    .. attribute:: config_form

        A Django form to save configuration for listeners attaching to this
        form. The default form is :class:`durian.forms.HookConfigForm`, which
        has the URL field.
    
    .. attribute:: timeout

        The timeout in seconds before we give up trying to dispatch the
        event to a listener URL.

    .. attribute:: async

        If ``True``, signals are dispatched to celery workers via a mesage.
        Otherwise dispatch happens locally (not a good idea in production).

    .. attribute:: retry

        Retry the task if it fails.

    .. attribute:: max_retries

        Maximum number of retries before we give up.

    .. attribute:: fail_silently

        Fail silently if the dispatch gives an HTTP error.

    .. attribute:: task_cls

        The :class:`celery.task.base.Task` class to use for dispatching
        the event.

    .. attribute:: match_forms

        A list of forms to create an event filter. This is automatically
        generated based on the :attr:`provides_args` attribute.

    """

    name = None
    task_cls = WebhookSignal
    timeout = 4
    async = True
    retry = False
    max_retries = 3
    fail_silently = False
    config_form = HookConfigForm
    provides_args = []
    match_forms = None

    def __init__(self, name=None, task_cls=None, timeout=None,
            async=None, retry=None, max_retries=None, fail_silently=False,
            config_form=None, provides_args=None, match_forms=None, **kwargs):
        self.name = name or self.name or get_full_cls_name(self.__class__)
        self.task_cls = task_cls or self.task_cls
        if timeout is not None:
            self.timeout = timeout
        if async is not None:
            self.async = async
        if retry is not None:
            self.retry = retry
        if max_retries is not None:
            self.max_retries = max_retries
        if fail_silently is not None:
            self.fail_silently = fail_silently
        self.provides_args = provides_args or self.provides_args
        self.config_form = config_form or self.config_form
        form_name = "%sConfigForm" % self.name
        self.match_forms = match_forms or self.match_forms or \
                            create_match_forms(form_name, self.provides_args)

    def send(self, sender, **payload):
        """Send signal and dispatch to all listeners.

        :param sender: The sender of the signal. Either a specific object
            or ``None``.

        :param payload: The data to pass on to listeners. Usually the keys
            described in :attr:`provides_args` and any additional keys you'd
            want to provide.

        """
        payload = self.prepare_payload(sender, payload)
        apply_ = curry(self._send_signal, sender, payload)
        return map(apply_, self.get_listeners(sender, payload))

    def _send_signal(self, sender, payload, target):
        applier = self.get_applier()
        return applier(args=[target.url, payload], kwargs=self.task_keywords)

    def event_filter(self, sender, payload, match):
        """How we filter events.

        :param sender: The sender of the signal.

        :param payload: The signal data.

        :param match: The match dictionary, or ``None``.

        """
        if not match:
            return True
        return deepmatch(match, payload)

    def get_match_forms(self, **kwargs):
        """Initialize the match forms with data recived by a request.
       
        :returns: A list of instantiated match forms.

        """
        return [match_form(**kwargs)
                    for match_form in self.match_forms.values()]

    def apply_match_forms(self, data):
        """With data recieved by request, convert to a list of match
        tuples."""
        mtuplelist = [match_form(data).field_to_mtuple()
                         for match_form in self.match_forms.values()]
        return mtuplelist_to_matchdict(mtuplelist)

    def get_listeners(self, sender, payload):
        """Get a list of all the listeners who wants this signal."""
        possible_targets = Listener.objects.filter(hook=self.name)
        return [target for target in possible_targets
                    if self.event_filter(sender, payload, target.match)]

    def get_applier(self, async=None):
        """Get the current apply method. Asynchronous or synchronous."""
        async = async or self.async
        method = "apply_async" if async else "apply"
        sender = getattr(self.task_cls, method)
        return sender

    def prepare_payload(self, sender, payload):
        """Prepare the payload for dispatching.

        You can add any additional formatting of the payload here.

        """
        return payload

    def add_listener_by_form(self, form, match=None):
        """Add listener with an instantiated :attr:`config_form`.
        
        :param form: An instance of :attr:`config_form`.
        :param match: Optional event filter match dict.

        """
        if not hasattr(form, "cleaned_data"):
            form.is_valid()
        config = dict(form.cleaned_data)
        url = config.pop("url")
        return Listener.objects.create(hook=self.name, url=url,
                                       match=match, config=config)

    def add_listener(self, url, match={}, **config):
        """Add listener for this signal.

        :param url: The url the listener is listening on.
        :keyword match: The even filter match dict.
        :keyword \*\*config: Hook specific listener configuration.

        """
        return Listener.objects.create(hook=self, url=url, match=match,
                                       **dict(config))

    def listener(self, form):
        """Create a new listener."""
        return IntermediateListener(self, form)

    @property
    def task_keywords(self):
        """The keyword arguments sent to the celery task."""
        return {"retry": self.retry,
                "max_retries": self.max_retries,
                "fail_silently": self.fail_silently,
                "timeout": self.timeout}


class SignalHook(Hook):
    """Hook attached to a Django signal."""
    signal = None
    _dispatch_uid = None

    def __init__(self, signal=None, **kwargs):
        self.signal = signal
        
        # Signal receivers must have a unique id, by default
        # they're generated by the reciver name and the sender,
        # but since it's possible to have different recieves for the
        # same instance, we need to generate our own unique id.
        if not self.__class__._dispatch_uid:
            self.__class__._dispatch_uid = gen_unique_id()

        super(SignalHook, self).__init__(**kwargs)

    def connect(self, sender):
        self.signal.connect(self.send, sender=sender,
                            dispatch_uid=self.__class__._dispatch_uid)
    
    def disconnect(self, sender):
        self.signal.disconnect(self.send, sender=sender,
                               dispatch_uid=self.__class__._dispatch_uid)


class ModelHook(SignalHook):
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

    def __init__(self, model=None, **kwargs):
        super(ModelHook, self).__init__(**kwargs)
        self.model = model or self.model
        if not self.model:
            raise NotImplementedError("ModelHook requires a model.")
        if self.signal:
            self.connect()
        if not self.provides_args:
            self.provides_args = self.get_model_default_fields()


    def get_model_default_fields(self):
        return [field.name
                    for field in self.model._meta.fields
                        if field.name != self.model._meta.pk.name]

    def prepare_payload(self, sender, payload):
        instance = payload.pop("instance")
        payload.pop("signal", None)
        model_data = dict((field_name, getattr(instance, field_name, None))
                                for field_name in self.provides_args)
        model_data.update(payload)
        return model_data

    def connect(self):
        super(ModelHook, self).connect(self.model)

    def disconnect(self):
        super(ModelHook, self).disconnect(self.model)


class IntermediateListener(object):

    def __init__(self, hook, form):
        self.hook = hook
        self.form = form
        self.conditions = None

    def match(self, **match):
        self.conditions = match
        return self

    def save(self):
        return self.hook.add_listener_by_form(self.form, self.conditions)
