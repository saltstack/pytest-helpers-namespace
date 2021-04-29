"""
pytest_helpers_namespace.plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pytest Helpers Namespace Plugin
"""
from functools import partial
from functools import wraps

import pytest

try:  # pragma: no cover
    import importlib.metadata

    PYTEST_61 = importlib.metadata.version("pytest") >= "6.1.0"
except ImportError:  # pragma: no cover
    try:
        import importlib_metadata

        PYTEST_61 = importlib_metadata.version("pytest") >= "6.1.0"
    except ImportError:  # pragma: no cover
        import pkg_resources

        PYTEST_61 = pkg_resources.get_distribution("pytest").version >= "6.1.0"


class FuncWrapper:
    def __init__(self, func):
        self.func = func

    @staticmethod
    def register(func):
        """
        This function will just raise a RuntimeError in case a function
        registration, which also sets a nested namespace, tries to override
        a known helper function with that nested namespace.
        This will just make the raised error make more sense.

        Instead of "AttributeError: 'function' object has no attribute 'register'",
        we will raise the exception below.
        """
        raise RuntimeError(
            "A namespace is already registered under the name: {}".format(func.__name__)
        )

    def __call__(self, *args, **kwargs):
        """
        This wrapper will just call the actual helper function
        """
        __tracebackhide__ = True
        return self.func(*args, **kwargs)


class HelpersRegistry:
    """
    Helper functions registrar which supports namespaces
    """

    __slots__ = ("_registry",)

    def __init__(self):
        self._registry = {}

    def register(self, func, name=None):
        """
        Register's a new function as a helper
        """
        if isinstance(func, str):
            return partial(self.register, name=func)

        if name is None:
            name = func.__name__
        if name in self._registry:
            raise RuntimeError(
                "A helper function is already registered under the name: {}".format(name)
            )
        self._registry[name] = wraps(func)(FuncWrapper(func))
        return func

    def __getattribute__(self, name):
        if name in ("__class__", "_registry", "register"):
            return object.__getattribute__(self, name)
        return self._registry.setdefault(name, self.__class__())

    def __repr__(self):
        return "{} {!r}>".format(self.__class__.__name__, self._registry)

    def __call__(self, *_, **__):
        raise RuntimeError("The helper being called was not registred")

    def __contains__(self, key):
        return key in self._registry

    if PYTEST_61 is False:  # pragma: no cover

        def __fspath__(self):
            # Compatibility with PyTest 6.0.x
            return __file__


def pytest_load_initial_conftests(*_):
    try:
        pytest.helpers  # pragma: no cover
    except AttributeError:
        pytest.helpers = HelpersRegistry()


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session):
    session.config.pluginmanager.register(pytest.helpers, "helpers-namespace")


def pytest_unconfigure():  # pragma: no cover
    try:
        delattr(pytest, "helpers")
    except AttributeError:
        pass
