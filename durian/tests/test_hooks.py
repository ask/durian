import unittest
from durian.event import Hook, ModelHook, IntermediateListener
from durian.registry import hooks
from durian.forms import BaseMatchForm
from durian.models import Listener
from celery.registry import tasks
from durian.tasks import WebhookSignal
from durian import match
from django.contrib.auth.models import User
from django.db.models import signals


class TestWebhookSignal(WebhookSignal):
    name = "__durian__.unittest.TestWebhookSignal"
    ignore_result = True
    scratchpad = {}

    def run(self, url, payload, **kwargs):
        self.__class__.scratchpad[url] = payload


testhook = Hook(name="__durian__.unittest.testhook",
                provides_args=["name", "address", "phone", "email"],
                task_cls=TestWebhookSignal,
                async=False)
hooks.register(testhook)

testmhook = ModelHook(model=User, signal=signals.post_save,
                name="__durian__.unittest.testmhook",
                provides_args=["username", "email", "first_name",
                               "last_name"],
                task_cls=TestWebhookSignal,
                async=False)
hooks.register(testmhook)


class TestHook(unittest.TestCase):

    def test_in_registry(self):
        in_reg = hooks.get("__durian__.unittest.testhook")
        self.assertTrue(in_reg)
        self.assertTrue(isinstance(in_reg, Hook))

    def test_match_forms(self):
        mforms = testhook.match_forms
        for field in testhook.provides_args:
            self.assertTrue(field in mforms)
            mform = mforms[field]()
            self.assertTrue(isinstance(mform, BaseMatchForm))
            self.assertTrue("%s_cond" % field in mform.base_fields)
            self.assertTrue("%s_query" % field in mform.base_fields)

        matchdict = testhook.apply_match_forms({
                    "name_cond": match.CONDITION_EXACT,
                    "name_query": "George Constanza",
                    "address_cond": match.CONDITION_ENDSWITH,
                    "address_query": "New York City",
                    "phone_cond": match.CONDITION_STARTSWITH,
                    "phone_query": "212",
                    "email_cond": match.CONDITION_CONTAINS,
                    "email_query": "@vandelay"})

        self.assertTrue(isinstance(matchdict.get("name"), match.Is))
        self.assertTrue(isinstance(matchdict.get("address"), match.Endswith))
        self.assertTrue(isinstance(matchdict.get("phone"), match.Startswith))
        self.assertTrue(isinstance(matchdict.get("email"), match.Contains))

        self.assertTrue(match.deepmatch(matchdict, {
            "name": "George Constanza",
            "address": "Border Lane, New York City",
            "phone": "212 555 88 23",
            "email": "george@vandelay.com",
        }))

    def test_trigger_event(self):
        url = "http://where.joe/listens"
        form = testhook.config_form({"url": url})
        listener = testhook.listener(form).match(name="Joe").save()
        self.assertTrue(isinstance(listener, Listener))

        lis = Listener.objects.filter(url=url)
        self.assertTrue(lis.count())
        self.assertTrue(lis[0].url == url)

        testhook.send(sender=self,
                        name="Joe", address="foo", phone="123",
                        email="joe@example.com")

        self.assertTrue(TestWebhookSignal.scratchpad.get(url))
        del(TestWebhookSignal.scratchpad[url])

        testhook.send(sender=self,
                        name="Simon", address="bar", phone="456",
                        email="simon@example.com")
        self.assertFalse(TestWebhookSignal.scratchpad.get(url))


class TestModelHook(unittest.TestCase):

    def test_trigger_event(self):
            url = "http://where.joe/mlistens"
            form = testmhook.config_form({"url": url})
            self.assertTrue(testmhook)
            a = testmhook.listener(form)
            self.assertTrue(isinstance(a, IntermediateListener))
            self.assertTrue(callable(a.match))
            self.assertTrue(testmhook.listener(form).match(username="joe"))
            listener = testmhook.listener(form).match(username="joe").save()
            self.assertTrue(isinstance(listener, Listener))

            lis = Listener.objects.filter(url=url)
            self.assertTrue(lis.count())
            self.assertTrue(lis[0].url == url)

            u = User.objects.create_user(username="joe",
                    email="joe@example.com", password="joe")

            scratch = TestWebhookSignal.scratchpad.get(url)
            self.assertTrue(scratch)
            self.assertTrue(scratch["created"])
            self.assertEquals(scratch["username"], "joe")
            self.assertEquals(scratch["email"], "joe@example.com")
            self.assertFalse(scratch.get("password"))
            del(TestWebhookSignal.scratchpad[url])

            u.last_name = "Example"
            u.save()

            scratch = TestWebhookSignal.scratchpad.get(url)
            self.assertTrue(scratch)
            self.assertEquals(scratch["created"], False)
            self.assertEquals(scratch["username"], "joe")
            self.assertEquals(scratch["email"], "joe@example.com")
            self.assertEquals(scratch["last_name"], "Example")
            self.assertFalse(scratch.get("password"))
            del(TestWebhookSignal.scratchpad[url])
