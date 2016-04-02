# -*- coding: utf-8 -*-

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
