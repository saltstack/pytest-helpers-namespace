Pytest Helpers Namespace
========================

.. image:: https://travis-ci.org/saltstack/pytest-helpers-namespace.svg?branch=master
    :target: https://travis-ci.org/saltstack/pytest-helpers-namespace
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/saltstack/pytest-helpers-namespace?branch=master&svg=true
    :target: https://ci.appveyor.com/project/saltstack-public/pytest-helpers-namespace/branch/master
    :alt: See Build Status on AppVeyor

.. image:: https://codecov.io/github/saltstack/pytest-helpers-namespace/coverage.svg?branch=master
    :target: https://codecov.io/github/saltstack/pytest-helpers-namespace?branch=master
    :alt: Code Coverage

.. image:: https://img.shields.io/pypi/v/pytest-helpers-namespace.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/pytest-helpers-namespace

.. image:: https://img.shields.io/pypi/dm/pytest-helpers-namespace.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/pytest-helpers-namespace

.. image:: https://img.shields.io/pypi/wheel/pytest-helpers-namespace.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/pytest-helpers-namespace

.. image:: https://img.shields.io/pypi/pyversions/pytest-helpers-namespace.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/pytest-helpers-namespace

.. image:: https://img.shields.io/pypi/implementation/pytest-helpers-namespace.svg?style=flat
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/pytest-helpers-namespace


This plugin does not provide any helpers to `pytest`_, it does, however,
provide a helpers namespace in `pytest`_ which enables you to register helper
functions in your ``conftest.py`` to be used within your tests without having
to import them.


Features
--------

* Provides a ``helpers`` `pytest`_ namespace which can be used to register
  helper functions without requiring you to import them on your actual tests to
  use them.


Requirements
------------

* None!


Installation
------------

You can install "pytest-helpers-namespace" via `pip`_ from `PyPI`_::

    $ pip install pytest-helpers-namespace


Usage
-----

Consider the following ``conftest.py`` file:

.. code-block:: python

   pytest_plugins = ['helpers_namespace']

   import pytest

   @pytest.helpers.register
   def foo(bar):
       '''
       this dumb helper function will just return what you pass to it
       '''
       return bar


And now consider the following test case:

.. code-block:: python

   def test_helper_namespace():
       assert pytest.helpers.foo(True) is True


Pretty simple right?!


You can even nest namespaces. Consider the following ``conftest.py`` file:

.. code-block:: python

   pytest_plugins = ['helpers_namespace']

   import pytest

   @pytest.helpers.can.haz.register
   def foo(bar):
       '''
       this dumb helper function will just return what you pass to it
       '''
       return bar


And now consider the following test case:

.. code-block:: python

   def test_helper_namespace():
       assert pytest.helpers.can.haz.foo(True) is True


You can even pass a name to the register function and that will be the helper function name.


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `Apache Software License 2.0`_ license,
"pytest-helpers-namespace" is free and open source software.


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed
description.

Changelog
---------

v2017.11.11
~~~~~~~~~~~

* Allow passing a string to the register function which will be the helper name

v2016.7.10
~~~~~~~~~~

* Allow a registered function to contibue to behave as a regular function. `#4`_.

v2016.4.15
~~~~~~~~~~

* Hide the ``FuncWrapper`` traceback in pytest failures. `#3`_. Thanks Logan Glickfield(`@lsglick`_)

v2016.4.5
~~~~~~~~~

* Use a wrapper class instead of adding an attribute to a function.

v2016.4.3
~~~~~~~~~

* Provide proper errors when helper functions or namespaces are being
  overridden. `#1`_

v2016.3.2
~~~~~~~~~~

* First working release

----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with
`@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/saltstack/pytest-helpers-namespace/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.org/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi

.. _`#1`: https://github.com/saltstack/pytest-helpers-namespace/issues/1
.. _`#3`: https://github.com/saltstack/pytest-helpers-namespace/pull/3
.. _`#4`: https://github.com/saltstack/pytest-helpers-namespace/issues/4

.. _`@lsglick`: https://github.com/lsglick
