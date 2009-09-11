from durian.match.strategy import deepmatch
from durian.match.able import Is, Like, Startswith, Endswith, Contains
from durian.match import mtuplelist_to_matchdict
from durian import match
import unittest


class TestMtuplelist(unittest.TestCase):

    def test_conversion(self):
        mtuplelist = [("name", match.CONDITION_ENDSWITH, "Constanza"),
                      ("zipcode", match.CONDITION_STARTSWITH, "70"),
                      ("address", match.CONDITION_EXACT, "Milkyway"),
                      ("work", match.CONDITION_CONTAINS, "andeley"),
                      ("zoo", match.CONDITION_PASS, "zoo")]
        matchdict = mtuplelist_to_matchdict(mtuplelist)
        self.assertFalse(matchdict.get("zoo"))
        self.assertTrue(isinstance(matchdict.get("name"), Endswith))
        self.assertEquals(matchdict["name"].value, "Constanza")
        self.assertTrue(isinstance(matchdict.get("zipcode"), Startswith))
        self.assertEquals(matchdict["zipcode"].value, "70")
        self.assertTrue(isinstance(matchdict.get("address"), Is))
        self.assertEquals(matchdict["address"].value, "Milkyway")
        self.assertTrue(isinstance(matchdict.get("work"), Contains))
        self.assertEquals(matchdict["work"].value, "andeley")

        matches = {"name": "George Constanza",
                   "zipcode": "70312",
                   "address": "Milkyway",
                   "work": "Vandeley Industries"}

        notmatches = {"name": "Jerry Seinfeld",
                      "zipcode": "70314",
                      "address": "Milkyway",
                      "work": "Comedian"}

        self.assertTrue(deepmatch(matches, matchdict))
        self.assertFalse(deepmatch(notmatches, matchdict))


class TestStrategy(unittest.TestCase):

    def test_deepmatch(self):
        self.assertTrue(deepmatch({"name": Like("Constanza")},
                                  {"name": "George Constanza"}))
        self.assertFalse(deepmatch({"name": Like("Seinfeld")},
                                   {"name": "George Constanza"}))
        self.assertTrue(deepmatch({"name": Startswith("George")},
                                  {"name": "George Constanza"}))
        self.assertFalse(deepmatch({"name": Startswith("Cosmo")},
                                   {"name": "George Constanza"}))
        self.assertTrue(deepmatch({"name": {
                                    "first_name": Startswith("El"),
                                    "last_name": Endswith("es"),
                                  }},
                                  {"name": {
                                    "first_name": "Elaine",
                                    "last_name": "Benes",
                                  }}))
        x = {
            "foo": "xuzzy",
            "baz": "xxx",
            "mooze": {
                "a": "b",
                "c": {
                    "d": "e",
                }
            }
        }
        self.assertTrue(deepmatch(x, x))
        self.assertFalse(deepmatch(x, {"foo": "xuzzy",
                                       "baz": "xxx",
                                       "mooze": {
                                           "a": "b",
                                           "c": {
                                                "x": "y",
                                            }
                                       }
                                  }))
        self.assertTrue(deepmatch({"foo": "bar"}, {"foo": "bar"}))
        self.assertFalse(deepmatch({"foo": 1}, {"foo": "1"}))
        self.assertFalse(deepmatch({"foo": "bar", "baz": {"x": "x"}},
                                   {"foo": "bar"}))
