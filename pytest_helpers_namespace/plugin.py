# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2016-2019 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    pytest_helpers_namespace.plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pytest Helpers Namespace Plugin
'''

# Import python libs
from functools import partial, wraps

# Import 3rd-party libs
import pytest


class FuncWrapper(object):

    def __init__(self, func):
        self.func = func

    def register(self, func):
        '''
        This function will just raise a RuntimeError in case a function
        registration, which also sets a nested namespace, tries to override
        a known helper function with that nested namespace.
        This will just make the raised error make more sense.

        Instead of "AttributeError: 'function' object has no attribute 'register'",
        we will raise the excption below.
        '''
        raise RuntimeError(
            'A namespace is already registered under the name: {0}'.format(
                func.__name__
            )
        )

    def __call__(self, *args, **kwargs):
        '''
        This wrapper will just call the actual helper function
        '''
        __tracebackhide__ = True
        return self.func(*args, **kwargs)


class HelpersRegistry(object):
    '''
    Helper functions registrar which supports namespaces
    '''

    __slots__ = ('_registry',)

    def __init__(self):
        self._registry = {}

    def register(self, func, name=None):
        '''
        Register's a new function as a helper
        '''
        if isinstance(func, str):
            return partial(self.register, name=func)

        if name is None:
            name = func.__name__
        if name in self._registry:
            raise RuntimeError(
                'A helper function is already registered under the name: {0}'.format(
                    name
                )
            )
        self._registry[name] = wraps(func)(FuncWrapper(func))
        return func

    def __getattribute__(self, name):
        if name in ('__class__', '_registry', 'register'):
            return object.__getattribute__(self, name)
        return self._registry.setdefault(name, self.__class__())

    def __repr__(self):
        return '{0} {1!r}>'.format(self.__class__.__name__, self._registry)

    def __call__(self, *args, **kwargs):
        raise RuntimeError(
            'The helper being called was not registred'
        )


if tuple([int(part) for part in pytest.__version__.split('.') if part.isdigit()]) < (4, 1):
    # PyTest < 4.1
    def pytest_namespace():
        '''
        Register our own namespace with pytest
        '''
        return {'helpers': HelpersRegistry()}
else:
    # PyTest >= 4.1
    # This now uses the stop gap provided in:
    #   https://docs.pytest.org/en/latest/deprecations.html#pytest-namespace
    #
    # We however use `pytest_load_initial_conftests` because we need to "patch"
    # pytest before any conftest is loaded.
    def pytest_load_initial_conftests(early_config, parser, args):
        try:
            pytest.helpers
        except AttributeError:
            pytest.helpers = HelpersRegistry()

    def pytest_unconfigure():
        try:
            delattr(pytest, 'helpers')
        except AttributeError:
            pass
