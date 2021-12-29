.. _changelog:

=========
Changelog
=========

Versions follow `Semantic Versioning <https://semver.org>`_ (`<major>.<minor>.<patch>`).

Backward incompatible (breaking) changes will only be introduced in major versions with advance notice in the
**Deprecations** section of releases.

.. towncrier-draft-entries::

.. towncrier release notes start


v2021.3.24
==========

* Switched project to a ``src`` layout.
* Switched project to a declarative setuptools approach
* Added support to check if a helper has been registered
* Pytest >= 6.1.1 is now required

v2019.1.8
=========

* Patch PyTest before any ``conftest.py`` file is processed.

v2019.1.7
=========

* Support PyTest >= 4.1

v2019.1.6.post1
===============

* No changes were made besides locking to PyTest < 4.0

v2019.1.6
=========

* No changes were made besides locking to PyTest < 4.1

v2017.11.11
===========

* Allow passing a string to the register function which will be the helper name

v2016.7.10
==========

* `#4`_: Allow a registered function to contibue to behave as a regular function.

v2016.4.15
==========

* `#3`_: Hide the ``FuncWrapper`` traceback in pytest failures. Thanks Logan Glickfield(`@lsglick`_)

v2016.4.5
=========

* Use a wrapper class instead of adding an attribute to a function.

v2016.4.3
=========

* `#1`_: Provide proper errors when helper functions or namespaces are being
  overridden.

v2016.3.2
==========

* First working release

.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/saltstack/pytest-helpers-namespace/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`nox`: https://nox.thea.codes/en/stable/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi

.. _`#1`: https://github.com/saltstack/pytest-helpers-namespace/issues/1
.. _`#3`: https://github.com/saltstack/pytest-helpers-namespace/pull/3
.. _`#4`: https://github.com/saltstack/pytest-helpers-namespace/issues/4

.. _`@lsglick`: https://github.com/lsglick
