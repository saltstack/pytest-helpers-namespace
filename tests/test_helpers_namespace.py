# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import pytest


@pytest.fixture(autouse=True)
def reset_helpers_namespace(request):
    try:
        yield
    finally:
        plugin = request.config.pluginmanager.get_plugin("helpers-namespace")
        plugin._registry.clear()


def test_namespace(pytester):
    pytester.makeconftest(
        """
        import pytest

        @pytest.helpers.register
        def foo(bar):
            return bar
        """
    )

    pytester.makepyfile(
        """
        import pytest

        def test_helpers():
            assert pytest.helpers.foo(True) is True
            print('PASSED')
    """
    )

    result = pytester.runpytest("-s")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "test_namespace.py PASSED",
        ]
    )

    # make sure that that we get a '0' exit code for the test suite
    assert result.ret == 0


def test_nested_namespace(pytester):
    pytester.makeconftest(
        """
        import pytest

        @pytest.helpers.foo.bar.register
        def foo(bar):
            return bar
        """
    )

    pytester.makepyfile(
        """
        import pytest

        def test_helpers():
            assert pytest.helpers.foo.bar.foo(True) is True
            print('PASSED')
    """
    )

    result = pytester.runpytest("-s")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "test_nested_namespace.py PASSED",
        ]
    )

    # make sure that that we get a '0' exit code for the test suite
    assert result.ret == 0


def test_unregistered_namespace(pytester):
    pytester.makepyfile(
        """
        import pytest

        def test_helpers():
            with pytest.raises(RuntimeError) as exc:
                assert pytest.helpers.foo(True) is True
            strexc = str(exc)
            assert 'The helper being called was not registered' in strexc
            print('PASSED')
    """
    )

    result = pytester.runpytest("-s")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "test_unregistered_namespace.py PASSED",
        ]
    )

    # make sure that that we get a '0' exit code for the test suite
    assert result.ret == 0


def test_namespace_override(pytester):
    pytester.makeconftest(
        """
        import pytest

        @pytest.helpers.foo.register
        def bar(bar):
            return bar

        @pytest.helpers.register
        def foo(bar):
            return bar
        """
    )
    pytester.makepyfile(
        """
        import pytest

        def test_helpers():
            with pytest.raises(RuntimeError) as exc:
                assert pytest.helpers.foo(True) is True
            assert 'The helper being called was not registered' in str(exc)
            print('PASSED')
    """
    )

    result = pytester.runpytest("-s")

    # fnmatch_lines does an assertion internally
    result.stderr.fnmatch_lines(
        ["*RuntimeError: A helper function is already registered under the name: foo"]
    )

    # make sure that that we get a '0' exit code for the test suite
    assert result.ret != 0


def test_helper_override(pytester):
    pytester.makeconftest(
        """
        import pytest

        @pytest.helpers.register
        def foo(bar):
            return bar

        @pytest.helpers.register
        def foo(bar):
            return bar
        """
    )
    pytester.makepyfile(
        """
        import pytest

        def test_helpers():
            with pytest.raises(RuntimeError) as exc:
                assert pytest.helpers.foo(True) is True
            assert 'The helper being called was not registered' in str(exc)
            print('PASSED')
    """
    )

    result = pytester.runpytest("-s")

    # fnmatch_lines does an assertion internally
    result.stderr.fnmatch_lines(
        ["*RuntimeError: A helper function is already registered under the name: foo"]
    )

    # make sure that that we get a '0' exit code for the test suite
    assert result.ret != 0


def test_helper_as_regular_function(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.helpers.register
        def foo2():
            return 'bar'

        def test_helpers():
            assert pytest.helpers.foo2() == 'bar'
            assert foo2() == 'bar'
        """
    )

    result = pytester.runpytest("-svv", "--log-cli-level=debug")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["test_helper_as_regular_function.py::test_helpers PASSED"])

    # make sure that that we get a '0' exit code for the test suite
    assert result.ret == 0


def test_helper_with_custom_name(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.helpers.register('jump')
        def foo():
            return 'bar'

        def test_helpers():
            assert pytest.helpers.jump() == 'bar'
            assert foo() == 'bar'
            print('PASSED')
    """
    )

    result = pytester.runpytest("-s")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "test_helper_with_custom_name.py PASSED",
        ]
    )

    # make sure that that we get a '0' exit code for the test suite
    assert result.ret == 0


def test_helper_contains_method(pytester):
    pytester.makeconftest(
        """
        import pytest

        assert "bar" not in pytest.helpers

        @pytest.helpers.register
        def bar():
            return True
        """
    )
    pytester.makepyfile(
        """
        import pytest

        def test_it():
            assert "bar" in pytest.helpers
            assert pytest.helpers.bar() is True
        """
    )

    result = pytester.runpytest("-vv")
    result.assert_outcomes(passed=1)


def test_call_register_on_helper_function(pytester):
    pytester.makeconftest(
        """
        import pytest

        @pytest.helpers.register
        def foo(bar):
            return bar

        @pytest.helpers.foo.register
        def blah(blah):
            return bar
        """
    )
    pytester.makepyfile(
        """
        import pytest

        def test_helpers():
            with pytest.raises(RuntimeError) as exc:
                assert pytest.helpers.foo(True) is True
    """
    )

    result = pytester.runpytest("-s")

    # fnmatch_lines does an assertion internally
    result.stderr.fnmatch_lines(
        [
            "*RuntimeError: Helper functions cannot be used to register new helper functions. "
            "Register and use a namespace for that.*",
        ]
    )
    # make sure that that we get a '0' exit code for the test suite
    assert result.ret != 0
