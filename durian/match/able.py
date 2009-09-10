import re
import operator


class Matchable(object):
    """Base matchable class.

    :param value: See :attr:`value`.
    
    Matchables are used to modify the way a value is tested for equality.

    Subclasses of :class:`Matchable` must implement the :meth:`__eq__` method.

    .. attribute:: value

        The value to match against.

    """
    
    def __init__(self, value):
        self.value = value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        raise NotImplementedError("Matchable objects must define __eq__")

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.value)


class Is(Matchable):
    """Matchable checking for strict equality.
    
    That is, the values must be identical.
    (same as the regular ``==`` operator.)

    """

    def __eq__(self, other):
        return operator.eq(self.value, other)


class Startswith(Matchable):
    """Matchable checking if the matched string starts with the matchee.
   
    Same as ``other.startswith(value)``.
    
    """

    def __eq__(self, other):
        return other.startswith(self.value)


class Endswith(Matchable):
    """Matchable checking if the matched string ends with the matchee.

    Same as ``other.endswith(value)``.

    """
    def __eq__(self, other):
        return other.endswith(self.value)


class Contains(Matchable):
    """Matchable checking if the matched string contains the matchee.

    Same as ``other.find(value)``.

    """

    def __eq__(self, other):
        return other.find(self.value) != -1


class Like(Matchable):
    """Matchable checking if the matched string matches a regular
    expression."""

    def __init__(self, value):
        super(Like, self).__init__(value)
        self.pattern = re.compile(self.value)

    def __eq__(self, other):
        return bool(self.pattern.search(other))
