import unittest
from durian.hook import Hook, ModelHook, IntermediateListener
from durian.registry import hooks
from durian.forms import BaseMatchForm
from durian.models import Listener
from celery.registry import tasks
from durian.tasks import WebhookSignal
from durian import match


class TestWebhookSignal(WebhookSignal):
    name = "__durian__.unittest.TestWebhookSignal"
    ignore_result = True
    scratchpad = {}
    
    def run(self, url, payload, **kwargs):
        self.__class__.scratchpad["url"] = payload

    

testhook = Hook(name="__durian__.unittest.testhook",
                provides_args=["name", "address", "phone", "email"],
                task_cls=TestWebhookSignal,
                async=False)
hooks.register(testhook)


class TestHook(unittest.TestCase):

    def test_in_registry(self):
        in_reg = hooks.get("__durian__.unittest.testhook")
        self.assertTrue(in_reg)
        self.assertTrue(isinstance(in_reg, Hook))

    def test_match_form(self):
        mform = testhook.match_form()
        self.assertTrue(isinstance(mform, BaseMatchForm))
        for field in testhook.provides_args:
            self.assertTrue(field in mform.base_fields)
            self.assertTrue("%s_cond" % field in mform.base_fields)
            self.assertTrue("%s_query" % field in mform.base_fields)
        mform = testhook.match_form({
                    "name": "name",
                    "name_cond": match.CONDITION_EXACT,
                    "name_query": "George Constanza",
                    "address": "address",
                    "address_cond": match.CONDITION_ENDSWITH,
                    "address_query": "New York City",
                    "phone": "phone",
                    "phone_cond": match.CONDITION_STARTSWITH,
                    "phone_query": "212",
                    "email": "email",
                    "email_cond": match.CONDITION_CONTAINS,
                    "email_query": "@vandelay"})
        self.assertTrue(mform.is_valid())

        matchdict = match.mtuplelist_to_matchdict(mform.save())
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

            lis = Listener.objects.filter(url="http://where.joe/listens")
            self.assertTrue(lis.count())
            self.assertTrue(lis[0] is listener)

            testhook.send(sender=self,
                          name="Joe", address="foo", phone="123",
                          email="joe@example.com")

            self.assertTrue(TestWebhookSignal.scratchpad.get(url))
            del(TestWebhookSignal.scratchpad["url"])

            testhook.send(sender=self,
                          name="Simon", address="bar", phone="456",
                          email="simon@example.com")
            self.assertFalse(TestWebHookSignal.scratchpad.get(url))
