from celeryhooks.models import Listener
from celery.utils import get_full_cls_name
from celeryhooks.tasks import WebhookSignal
from functools import partial as curry


class Hook(object):
    name = None
    task_cls = WebhookSignal
    timeout = 4
    async = True
    retry = False
    max_retries = 3
    fail_silently = False

    def __init__(self, name=None, task_cls=None, timeout=None,
            async=None, retry=None, max_retries=None, fail_silently=False,
            **kwargs):
        self.name = name or self.name or get_full_cls_name(self.__class__)
        self.task_cls = task_cls or self.task_cls
        self.timeout = timeout or self.timeout
    
    def send(self, sender, **payload):
        apply_ = curry(self._send_signal, sender, payload)
        return map(apply_, self.get_listeners(sender, payload))

    def _send_signal(self, sender, payload, target):
        applier = self.get_applier()
        return applier(args=[target.url, payload], kwargs=self.task_keywords)

    def get_listeners(self, sender, payload):
        possible_targets = Listener.objects.filter(hook=self.name)
        return [target for target in possible_targets
                    if target.match(sender, **payload)]

    def get_applier(self, async=None):
        async = async or self.async
        method = "apply_async" if async else "apply"
        sender = getattr(self.task_cls, method)
        return sender

    @property
    def task_keywords(self):
        return {"retry": self.retry,
                "max_retries": self.max_retries,
                "fail_silently": self.fail_silently,
                "timeout": self.timeout}


class SignalHook(Hook):

    def __init__(self, signal, signal_sender=None, **kwargs):
        self.signal = signal
        self.signal_sender = signal_sender
        signal.connect(self.send, sender=signal_sender or self)
        super(SignalHook, self).__init__(**kwargs)
