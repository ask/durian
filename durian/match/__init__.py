from durian.match.able import Any, Is, Startswith, Endswith, Contains, Like
from durian.match.strategy import deepmatch
from django.utils.translation import ugettext_lazy as _

CONDITION_PASS = 0x0
CONDITION_EXACT = 0x1
CONDITION_STARTSWITH = 0x2
CONDITION_ENDSWITH = 0x3
CONDITION_CONTAINS = 0x4

MATCHABLE_CHOICES = (
    (CONDITION_PASS, (_("anything"))),
    (CONDITION_EXACT, (_("exact"))),
    (CONDITION_STARTSWITH, (_("starts with"))),
    (CONDITION_ENDSWITH, (_("ends with"))),
    (CONDITION_CONTAINS, (_("contains"))),
)

CONST_TO_MATCHABLE = {
	CONDITION_PASS: Any,
    CONDITION_EXACT: Is,
    CONDITION_STARTSWITH: Startswith,
    CONDITION_ENDSWITH: Endswith,
    CONDITION_CONTAINS: Contains,
}

def const_to_matchable(const_kind, what):
    return CONST_TO_MATCHABLE[int(const_kind)](what)


def mtuplelist_to_matchdict(mtuplelist):
    """Converts a list of ``(name, kind, what)`` tuples to a match dict.
    Where name is the field to match, kind is a matchable number mapping to
    ``CONST_TO_MATCHABLE``.

    Possible types are: ``CONDITION_EXACT``, ``CONDITION_STARTSWITH``,
                        ``CONDITION_ENDSWITH, ``CONDITION_CONTAINS``.



    Probably best explained by an example:

        >>> mtuplelist = [("name", CONDITION_ENDSWITH, "Constanza"),
        ...               ("zipcode", CONDITION_STARTSWITH, "70")]
        >>> mtuplelist_to_matchdict(mtuplelist)
        {"name": Endswith("Constanza"), "zipcode": Startswith("70")}

    """
    return dict((name, const_to_matchable(kind, what) or what)
                    for name, kind, what in mtuplelist
                        if int(kind) != CONDITION_PASS)
