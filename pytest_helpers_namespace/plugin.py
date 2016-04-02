# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2016 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    pytest_helpers_namespace.plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pytest Helpers Namespace Plugin
'''


# -*- coding: utf-8 -*-


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
        self._registry[func.__name__] = func
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
