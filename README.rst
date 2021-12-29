.. image:: https://github.com/saltstack/pytest-helpers-namespace/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/saltstack/pytest-helpers-namespace/actions/workflows/testing.yml
    :alt: See Build Status

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

..
   include-starts-here


Pytest Helpers Namespace
========================

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

   import pytest


   @pytest.helpers.register
   def foo(bar):
       """
       this dumb helper function will just return what you pass to it
       """
       return bar


And now consider the following test case:

.. code-block:: python

   def test_helper_namespace():
       assert pytest.helpers.foo(True) is True


Pretty simple right?!


You can even nest namespaces. Consider the following ``conftest.py`` file:

.. code-block:: python

   pytest_plugins = ["helpers_namespace"]

   import pytest


   @pytest.helpers.can.haz.register
   def foo(bar):
       """
       this dumb helper function will just return what you pass to it
       """
       return bar


And now consider the following test case:

.. code-block:: python

   def test_helper_namespace():
       assert pytest.helpers.can.haz.foo(True) is True


You can even pass a name to the register function and that will be the helper function name.


----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with
`@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi

..
   include-ends-here

Documentation
=============

The full documentation can be seen `here <https://pytest-helpers-namespace.readthedocs.io>`_.
