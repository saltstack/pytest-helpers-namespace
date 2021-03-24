# pylint: disable=missing-module-docstring
import pathlib

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent
try:
    from .version import __version__
except ImportError:  # pragma: no cover
    __version__ = "0.0.0.not-installed"
    try:
        from importlib.metadata import version, PackageNotFoundError

        try:
            __version__ = version(__name__)
        except PackageNotFoundError:
            # package is not installed
            pass
    except ImportError:
        try:
            from pkg_resources import get_distribution, DistributionNotFound

            try:
                __version__ = get_distribution(__name__).version
            except DistributionNotFound:
                # package is not installed
                pass
        except ImportError:
            # pkg resources isn't even available?!
            pass
