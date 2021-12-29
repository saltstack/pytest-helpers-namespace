# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Pytest Helpers Namespace Plugin.
"""
from functools import partial
from functools import wraps
from typing import Any
from typing import Callable
from typing import cast
from typing import Optional
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

import pytest

if TYPE_CHECKING:
    from typing import Dict

    # pylint: disable=import-error,unused-import,no-name-in-module
    from _pytest.main import Session

    # pylint: enable=import-error,unused-import,no-name-in-module

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


F = TypeVar("F", bound=Callable[..., Any])


class FuncWrapper:
    """
    Wrapper class for helper functions and namespaces.
    """

    def __init__(self, func: F):
        self.func = func

    @staticmethod
    def register(func: F) -> F:
        """
        Register a helper function.

        This function will just raise a RuntimeError in case a function
        registration, which also sets a nested namespace, tries to override
        a known helper function with that nested namespace.
        This will just make the raised error make more sense.

        Instead of "AttributeError: 'function' object has no attribute 'register'",
        we will raise the exception below.
        """
        raise RuntimeError(
            "Helper functions cannot be used to register new helper functions. "
            "Register and use a namespace for that."
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        This wrapper will just call the actual helper function.
        """
        __tracebackhide__ = True
        return self.func(*args, **kwargs)


class HelpersRegistry:
    """
    Helper functions registrar which supports namespaces.
    """

    __slots__ = ("_registry",)

    def __init__(self) -> None:
        self._registry = {}  # type: "Dict[str, Union[FuncWrapper, HelpersRegistry]]"

    def register(self, func: Union[F, str], name: Optional[str] = None) -> F:
        """
        Register's a new function as a helper.
        """
        if isinstance(func, str):
            return cast(F, partial(self.register, name=func))

        if name is None:
            name = func.__name__
        if name in self._registry:
            raise RuntimeError(
                "A helper function is already registered under the name: {}".format(name)
            )
        self._registry[name] = wraps(func)(FuncWrapper(func))
        return func

    def __getattribute__(self, name: str) -> Any:
        """
        Return an attribute from the registry or register a new namespace.
        """
        if name in ("__class__", "_registry", "register"):
            return object.__getattribute__(self, name)
        return self._registry.setdefault(name, self.__class__())

    def __repr__(self) -> str:
        """
        Return a string representation of the class.
        """
        return "{} {!r}>".format(self.__class__.__name__, self._registry)

    def __call__(self, *_: Any, **__: Any) -> Any:
        """
        Show a warning when calling an unregistered helper function.
        """
        raise RuntimeError("The helper being called was not registered")

    def __contains__(self, key: str) -> bool:
        """
        Check for the presence of a helper name in the registry.
        """
        return key in self._registry

    if PYTEST_61 is False:  # pragma: no cover

        def __fspath__(self) -> str:
            """
            Compatibility method against newer Pytest versions.
            """
            # Compatibility with PyTest 6.0.x
            return __file__


def pytest_load_initial_conftests(*_: Any) -> None:
    """
    Hook into pytest to inject our custom ``helpers`` registry.
    """
    try:
        pytest.helpers  # pragma: no cover
    except AttributeError:
        pytest.helpers = HelpersRegistry()


@pytest.hookimpl(trylast=True)  # type: ignore[misc]
def pytest_sessionstart(session: "Session") -> None:
    """
    Register our plugin with pytest.
    """
    session.config.pluginmanager.register(pytest.helpers, "helpers-namespace")


def pytest_unconfigure() -> None:  # pragma: no cover
    """
    Delete our custom ``helpers`` registry from the ``pytest`` module namespace.
    """
    try:
        delattr(pytest, "helpers")
    except AttributeError:
        pass


if TYPE_CHECKING:
    setattr(pytest, "helpers", HelpersRegistry())
