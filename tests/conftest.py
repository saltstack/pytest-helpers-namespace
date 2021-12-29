# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import logging

import pytest

try:  # pragma: no cover
    import importlib.metadata

    pkg_version = importlib.metadata.version
except ImportError:  # pragma: no cover
    try:
        import importlib_metadata

        pkg_version = importlib_metadata.version
    except ImportError:  # pragma: no cover
        import pkg_resources

        def pkg_version(package):
            return pkg_resources.get_distribution(package).version


log = logging.getLogger(__name__)


def pkg_version_info(package):
    """
    Return a version info tuple for the given package.
    """
    return tuple(int(part) for part in pkg_version(package).split(".") if part.isdigit())


if pkg_version_info("pytest") >= (6, 2):
    pytest_plugins = ["pytester"]
else:  # pragma: no cover

    @pytest.fixture
    def pytester():
        pytest.skip("The pytester fixture is not available in Pytest < 6.2.0")
