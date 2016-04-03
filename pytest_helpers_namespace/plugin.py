# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2016 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    pytest_helpers_namespace.plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pytest Helpers Namespace Plugin
'''

# Import python libs
from functools import wraps


class HelpersRegistry(object):
    '''
    Helper functions registrar which supports namespaces
    '''

    __slots__ = ('_registry',)

    def __init__(self):
        self._registry = {}

    def register(self, func):
        '''
        Register's a new function as a helper
        '''
        if func.__name__ in self._registry:
            raise RuntimeError(
                'A {0} helper function is already registered under the name: {1}'.format(
                    self.__class__.__name__,
                    func.__name__
                )
            )

        # Instead of setting the register attribute on the actual function, thus
        # changing the function, we define a decorator wrapper and set the register
        # attribute on it.
        @wraps(func)
        def wrapper(*args, **kwargs):
            '''
            This wrapper will just call the actual helper function
            '''
            return func(*args, **kwargs)

        def wrapper_register(func):
            '''
            This function will just raise a RuntimeError in case a function
            registration, which also sets a nested namespace, tries to override
            a known helper function with that nested namespace.
            This will just make the raised error make more sense.

            Instead of "AttributeError: 'function' object has no attribute 'register'",
            we will raise the excption below.
            '''
            raise RuntimeError(
                'A {0} namespace is already registered under the name: {1}'.format(
                    self.__class__.__name__,
                    func.__name__
                )
            )
        wrapper.register = wrapper_register
        self._registry[func.__name__] = wrapper
        return self

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


def pytest_namespace():
    '''
    Register our own namespace with pytest
    '''
    return {'helpers': HelpersRegistry()}
