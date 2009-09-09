import re
from collections import deque


class Matchable(object):
    
    def __init__(self, value):
        self.value = value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        raise NotImplementedError("Matchable objects must define __eq__")
    
    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.value)


class Startswith(Matchable):

    def __eq__(self, other):
        return other.startswith(self.value)


class Endswith(Matchable):

    def __eq__(self, other):
        return other.endswith(self.value)


class Find(Matchable):

    def __eq__(self, other):
        return other.find(self.value) != -1


class Like(Matchable):

    def __init__(self, value):
        super(Like, self).__init__(value)
        self.pattern = re.compile(self.value)

    def __eq__(self, other):
        return bool(self.pattern.search(other))


def deepmatch(needle, haystack):
    stream = deque([(needle, haystack)])

    while True:
        atom_left, atom_right = stream.pop()
        for k,v in atom_left.items():
            if isinstance(v, dict):
                if k not in atom_right:
                    return False
                stream.append((v, atom_right[k]))
            else:
                if atom_right.get(k) != v:
                    return False
        if not stream:
            break
    return True


assert deepmatch({"name": Like("Constanza")}, {"name": "George Constanza"})
assert not deepmatch({"name": Like("Seinfeld")}, {"name": "George Constanza"})
assert deepmatch({"name": Startswith("George")}, {"name": "George Constanza"})
assert not deepmatch({"name": Startswith("Cosmo")}, {"name": "George Constanza"})
assert deepmatch({"name": {
                            "first_name": Startswith("El"),
                            "last_name": Endswith("es"),
                     }},
                     {"name": {
                            "first_name": "Elaine",
                            "last_name": "Benes",
                     }})
x = {
    "foo": "xuzzy",
    "baz": "xxx",
    "mooze": {
        "a": "b",
        "c": {
            "d": "e"
        }
    }
}
assert deepmatch(x, x)
assert not deepmatch(x, {"foo": "xuzzy",
                         "baz": "xxx",
                         "mooze": {
                            "a": "b",
                            "c": {
                                "x": "y"}
                                }
                        })
assert deepmatch({"foo": "bar"}, {"foo": "bar"})
assert not deepmatch({"foo": 1}, {"foo": "1"})
assert not deepmatch({"foo": "bar", "baz": {"x": "x"}}, {"foo": "bar"})
