"""durian.registry"""
from celery.exceptions import NotRegistered, AlreadyRegistered
from UserDict import UserDict


class HookRegistry(UserDict):
    """Global hook registry."""

    AlreadyRegistered = AlreadyRegistered
    NotRegistered = NotRegistered

    def __init__(self):
        self.data = {}

    def register(self, hook):
        """Register a hook in the hook registry.

        :param hook: The hook to register.

        :raises AlreadyRegistered: if the task is already registered.

        """
        name = hook.name
        if name in self.data:
            raise self.AlreadyRegistered(
                    "Hook with name %s is already registered." % name)

        self.data[name] = hook

    def unregister(self, name):
        """Unregister hook by name.

        :param name: name of the hook to unregister, or a
            :class:`durian.hooks.Hook` class with a valid ``name`` attribute.

        :raises celery.exceptions.NotRegistered: if the hook has not
            been registered.

        """
        if hasattr(name, "name"):
            name = name.name
        if name not in self.data:
            raise self.NotRegistered(
                    "Hook with name %s is not registered." % name)
        del self.data[name]

    def get_all(self):
        """Get all hooks."""
        return self.data

    def get_hook(self, name):
        """Get hook by name."""
        return self.data[name]

"""
.. data:: hooks

    The global hook registry.

"""
hooks = HookRegistry()
