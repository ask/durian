from celery.task.base import Task
from celery.registry import tasks
from celery.exceptions import MaxRetriesExceededError
from anyjson import serialize


class WebhookSignal(Task):
    name = "durian.tasks.WebhookSignal"
    ignore_result = True

    def run(self, url, payload, **kwargs):
        import urllib2
        import socket

        orig_timeout = socket.getdefaulttimeout()
        retry = kwargs.get("retry", False)
        fail_silently = kwargs.get("fail_silently", False)
        self.max_retries = kwargs.get("max_retries", self.max_retries)
        timeout = kwargs.get("timeout", orig_timeout)

        socket.setdefaulttimeout(timeout)
        try:
            urllib2.urlopen(url, serialize(payload))
        except urllib2.URLError, exc:
            if self.retry:
                try:
                    self.retry(args=[url, payload], kwargs=kwargs, exc=exc)
                except MaxRetriesExceededError:
                    if self.fail_silently:
                        return
                    raise
            else:
                if fail_silently:
                    return
                raise
        finally:
            socket.setdefaulttimeout(orig_timeout)
