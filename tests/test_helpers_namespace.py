# -*- coding: utf-8 -*-
# pragma: no cover

def test_namespace(testdir):
    testdir.makeconftest(
        '''
        pytest_plugins = ['helpers_namespace']
        import pytest

        @pytest.helpers.register
        def foo(bar):
            return bar
        '''
    )

    testdir.makepyfile('''
        import pytest

        def test_helpers():
            assert pytest.helpers.foo(True) is True
            print('PASSED')
    ''')

    result = testdir.runpytest('-s')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'test_namespace.py PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_nested_namespace(testdir):
    testdir.makeconftest(
        '''
        pytest_plugins = ['helpers_namespace']
        import pytest

        @pytest.helpers.foo.bar.register
        def foo(bar):
            return bar
        '''
    )

    testdir.makepyfile('''
        import pytest

        def test_helpers():
            assert pytest.helpers.foo.bar.foo(True) is True
            print('PASSED')
    ''')

    result = testdir.runpytest('-s')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'test_nested_namespace.py PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_unregistered_namespace(testdir):
    testdir.makepyfile('''
        import pytest

        def test_helpers():
            with pytest.raises(RuntimeError) as exc:
                assert pytest.helpers.foo(True) is True
            assert 'The helper being called was not registred' in str(exc)
            print('PASSED')
    ''')

    result = testdir.runpytest('-s')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'test_unregistered_namespace.py PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_namespace_override(testdir):
    testdir.makeconftest(
        '''
        pytest_plugins = ['helpers_namespace']
        import pytest

        @pytest.helpers.foo.register
        def bar(bar):
            return bar

        @pytest.helpers.register
        def foo(bar):
            return bar
        '''
    )
    testdir.makepyfile('''
        import pytest

        def test_helpers():
            with pytest.raises(RuntimeError) as exc:
                assert pytest.helpers.foo(True) is True
            assert 'The helper being called was not registred' in str(exc)
            print('PASSED')
    ''')

    result = testdir.runpytest('-s')

    # fnmatch_lines does an assertion internally
    result.stderr.fnmatch_lines([
        '*RuntimeError: A helper function is already registered under the name: foo'
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret != 0


def test_namespace_override_2(testdir):
    testdir.makeconftest(
        '''
        pytest_plugins = ['helpers_namespace']
        import pytest

        @pytest.helpers.register
        def foo(bar):
            return bar

        @pytest.helpers.foo.register
        def bar(bar):
            return bar
        '''
    )
    testdir.makepyfile('''
        import pytest

        def test_helpers():
            with pytest.raises(RuntimeError) as exc:
                assert pytest.helpers.foo(True) is True
            assert 'The helper being called was not registred' in str(exc)
            print('PASSED')
    ''')

    result = testdir.runpytest('-s')

    # fnmatch_lines does an assertion internally
    result.stderr.fnmatch_lines([
        '*RuntimeError: A namespace is already registered under the name: bar'
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret != 0


def test_helper_override(testdir):
    testdir.makeconftest(
        '''
        import pytest
        pytest_plugins = ['helpers_namespace']

        @pytest.helpers.register
        def foo(bar):
            return bar

        @pytest.helpers.register
        def foo(bar):
            return bar
        '''
    )
    testdir.makepyfile('''
        import pytest

        def test_helpers():
            with pytest.raises(RuntimeError) as exc:
                assert pytest.helpers.foo(True) is True
            assert 'The helper being called was not registred' in str(exc)
            print('PASSED')
    ''')

    result = testdir.runpytest('-s')

    # fnmatch_lines does an assertion internally
    result.stderr.fnmatch_lines([
        '*RuntimeError: A helper function is already registered under the name: foo'
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret != 0


def test_helper_as_regular_function(testdir):
    testdir.makepyfile('''
        import pytest

        @pytest.helpers.register
        def foo():
            return 'bar'

        def test_helpers():
            assert pytest.helpers.foo() == 'bar'
            assert foo() == 'bar'
            print('PASSED')
    ''')

    result = testdir.runpytest('-s')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'test_helper_as_regular_function.py PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_helper_with_custom_name(testdir):
    testdir.makepyfile('''
        import pytest

        @pytest.helpers.register('jump')
        def foo():
            return 'bar'

        def test_helpers():
            assert pytest.helpers.jump() == 'bar'
            assert foo() == 'bar'
            print('PASSED')
    ''')

    result = testdir.runpytest('-s')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'test_helper_with_custom_name.py PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
