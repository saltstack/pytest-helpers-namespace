# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=import-error,protected-access,line-too-long
import datetime
import json
import os
import pathlib
import shutil
import sys
import tempfile

import nox
from nox.command import CommandFailed


COVERAGE_VERSION_REQUIREMENT = "coverage==5.5"
PYTEST_VERSION_REQUIREMENT = os.environ.get("PYTEST_VERSION_REQUIREMENT") or None
IS_WINDOWS = sys.platform.lower().startswith("win")
IS_DARWIN = sys.platform.lower().startswith("darwin")

if IS_WINDOWS:
    COVERAGE_FAIL_UNDER_PERCENT = 96
elif IS_DARWIN:
    COVERAGE_FAIL_UNDER_PERCENT = 96
else:
    COVERAGE_FAIL_UNDER_PERCENT = 96

# Be verbose when running under a CI context
PIP_INSTALL_SILENT = (os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS")) is None
CI_RUN = PIP_INSTALL_SILENT is False
SKIP_REQUIREMENTS_INSTALL = "SKIP_REQUIREMENTS_INSTALL" in os.environ
EXTRA_REQUIREMENTS_INSTALL = os.environ.get("EXTRA_REQUIREMENTS_INSTALL")

# Paths
REPO_ROOT = pathlib.Path(__file__).resolve().parent
# Change current directory to REPO_ROOT
os.chdir(str(REPO_ROOT))

ARTIFACTS_DIR = REPO_ROOT / "artifacts"
# Make sure the artifacts directory exists
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
RUNTESTS_LOGFILE = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "runtests-{}.log".format(
    datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")
)
COVERAGE_REPORT_DB = REPO_ROOT / ".coverage"
COVERAGE_REPORT_PROJECT = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "coverage-project.xml"
COVERAGE_REPORT_TESTS = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "coverage-tests.xml"
JUNIT_REPORT = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "junit-report.xml"

# Nox options
#  Reuse existing virtualenvs
nox.options.reuse_existing_virtualenvs = True
#  Don't fail on missing interpreters
nox.options.error_on_missing_interpreters = False


def pytest_version(session):
    try:
        return session._runner._pytest_version_info
    except AttributeError:
        session_pytest_version = session_run_always(
            session,
            "python",
            "-c",
            'import sys, pkg_resources; sys.stdout.write("{}".format(pkg_resources.get_distribution("pytest").version))',
            silent=True,
            log=False,
        )
        session._runner._pytest_version_info = tuple(
            int(part) for part in session_pytest_version.split(".") if part.isdigit()
        )
    return session._runner._pytest_version_info


def session_run_always(session, *command, **kwargs):
    try:
        # Guess we weren't the only ones wanting this
        # https://github.com/theacodes/nox/pull/331
        return session.run_always(*command, **kwargs)
    except AttributeError:
        old_install_only_value = session._runner.global_config.install_only
        try:
            # Force install only to be false for the following chunk of code
            # For additional information as to why see:
            #   https://github.com/theacodes/nox/pull/181
            session._runner.global_config.install_only = False
            return session.run(*command, **kwargs)
        finally:
            session._runner.global_config.install_only = old_install_only_value


@nox.session(python=("3", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10"))
def tests(session):
    """
    Run tests.
    """
    env = {}
    if SKIP_REQUIREMENTS_INSTALL is False:
        # Always have the wheel package installed
        session.install("--progress-bar=off", "wheel", silent=PIP_INSTALL_SILENT)
        session.install(
            "--progress-bar=off", COVERAGE_VERSION_REQUIREMENT, silent=PIP_INSTALL_SILENT
        )
        pytest_version_requirement = PYTEST_VERSION_REQUIREMENT
        if pytest_version_requirement:
            if not pytest_version_requirement.startswith("pytest"):
                pytest_version_requirement = "pytest{}".format(pytest_version_requirement)
            session.install(
                "--progress-bar=off", pytest_version_requirement, silent=PIP_INSTALL_SILENT
            )
        session.install("--progress-bar=off", "-e", ".[tests]", silent=PIP_INSTALL_SILENT)

        if EXTRA_REQUIREMENTS_INSTALL:
            session.log(
                "Installing the following extra requirements because the EXTRA_REQUIREMENTS_INSTALL "
                "environment variable was set: EXTRA_REQUIREMENTS_INSTALL='%s'",
                EXTRA_REQUIREMENTS_INSTALL,
            )
            install_command = ["--progress-bar=off"]
            install_command += [req.strip() for req in EXTRA_REQUIREMENTS_INSTALL.split()]
            session.install(*install_command, silent=PIP_INSTALL_SILENT)

    session.run("coverage", "erase")

    env.update(
        {
            # The full path to the .coverage data file. Makes sure we always write
            # them to the same directory
            "COVERAGE_FILE": str(COVERAGE_REPORT_DB),
            # Instruct sub processes to also run under coverage
            "COVERAGE_PROCESS_START": str(REPO_ROOT / ".coveragerc"),
        }
    )

    args = [
        "--rootdir",
        str(REPO_ROOT),
        "--log-file={}".format(RUNTESTS_LOGFILE),
        "--log-file-level=debug",
        "--show-capture=no",
        "--junitxml={}".format(JUNIT_REPORT),
        "--showlocals",
        "--strict-markers",
        "-ra",
        "-s",
    ]
    if pytest_version(session) > (6, 2):
        args.append("--lsof")
    if session._runner.global_config.forcecolor:
        args.append("--color=yes")
    if not session.posargs:
        args.append("tests/")
    else:
        for arg in session.posargs:
            if arg.startswith("--color") and session._runner.global_config.forcecolor:
                args.remove("--color=yes")
            args.append(arg)

    try:
        session.run("coverage", "run", "-m", "pytest", *args, env=env)
    finally:
        # Always combine and generate the XML coverage report
        try:
            session.run("coverage", "combine")
        except CommandFailed:
            # Sometimes some of the coverage files are corrupt which would
            # trigger a CommandFailed exception
            pass
        # Generate report for project code coverage
        session.run(
            "coverage",
            "xml",
            "-o",
            str(COVERAGE_REPORT_PROJECT),
            "--omit=tests/*",
            "--include=src/pytest_helpers_namespace/*",
        )
        # Generate report for tests code coverage
        session.run(
            "coverage",
            "xml",
            "-o",
            str(COVERAGE_REPORT_TESTS),
            "--omit=src/pytest_helpers_namespace/*",
            "--include=tests/*",
        )
        try:
            cmdline = [
                "coverage",
                "report",
                "--show-missing",
                "--include=src/pytest_helpers_namespace/*,tests/*",
            ]
            session.run(*cmdline)
            if pytest_version(session) >= (6, 2):
                cmdline.append("--fail-under={}".format(COVERAGE_FAIL_UNDER_PERCENT))
        finally:
            if COVERAGE_REPORT_DB.exists():
                shutil.copyfile(str(COVERAGE_REPORT_DB), str(ARTIFACTS_DIR / ".coverage"))


def _lint(session, rcfile, flags, paths):
    session.install("--progress-bar=off", "-e", ".[lint]", silent=PIP_INSTALL_SILENT)
    session.run("pylint", "--version")
    pylint_report_path = os.environ.get("PYLINT_REPORT")

    cmd_args = ["pylint", "--rcfile={}".format(rcfile)] + list(flags) + list(paths)

    stdout = tempfile.TemporaryFile(mode="w+b")
    try:
        session.run(*cmd_args, stdout=stdout)
    finally:
        stdout.seek(0)
        contents = stdout.read()
        if contents:
            contents = contents.decode("utf-8")
            sys.stdout.write(contents)
            sys.stdout.flush()
            if pylint_report_path:
                # Write report
                with open(pylint_report_path, "w", encoding="utf-8") as wfh:
                    wfh.write(contents)
                session.log("Report file written to %r", pylint_report_path)
        stdout.close()


@nox.session(python="3")
def lint(session):
    """
    Run PyLint against Salt and it's test suite. Set PYLINT_REPORT to a path to capture output.
    """
    session.notify("lint-code-{}".format(session.python))
    session.notify("lint-tests-{}".format(session.python))


@nox.session(python="3", name="lint-code")
def lint_code(session):
    """
    Run PyLint against the code. Set PYLINT_REPORT to a path to capture output.
    """
    flags = ["--disable=I"]
    if session.posargs:
        paths = session.posargs
    else:
        paths = ["setup.py", "noxfile.py", "src/pytest_helpers_namespace/"]
    _lint(session, ".pylintrc", flags, paths)


@nox.session(python="3", name="lint-tests")
def lint_tests(session):
    """
    Run PyLint against Salt and it's test suite. Set PYLINT_REPORT to a path to capture output.
    """
    flags = ["--disable=I"]
    if session.posargs:
        paths = session.posargs
    else:
        paths = ["tests/"]
    _lint(session, ".pylintrc", flags, paths)


@nox.session(python="3")
def docs(session):
    """
    Build Docs.
    """
    session.install("--progress-bar=off", "-e", ".[docs]", silent=PIP_INSTALL_SILENT)
    os.chdir("docs/")
    session.run("make", "clean", external=True)
    # session.run("make", "linkcheck", "SPHINXOPTS=-W", external=True)
    session.run("make", "coverage", "SPHINXOPTS=-W", external=True)
    docs_coverage_file = os.path.join("_build", "html", "python.txt")
    if os.path.exists(docs_coverage_file):
        with open(docs_coverage_file, encoding="utf-8") as rfh:
            contents = rfh.readlines()[2:]
            if contents:
                session.error("\n" + "".join(contents))
    session.run("make", "html", "SPHINXOPTS=-W", external=True)
    os.chdir("..")


@nox.session(name="docs-dev", python="3")
def docs_dev(session):
    """
    Build Docs.
    """
    session.install("--progress-bar=off", "-e", ".[docs]", silent=PIP_INSTALL_SILENT)
    os.chdir("docs/")
    session.run("make", "html", "SPHINXOPTS=-W", external=True, env={"LOCAL_DEV_BUILD": "1"})
    os.chdir("..")


@nox.session(name="docs-crosslink-info", python="3")
def docs_crosslink_info(session):
    """
    Report intersphinx cross links information.
    """
    session.install("--progress-bar=off", "-e", ".[docs]", silent=PIP_INSTALL_SILENT)
    os.chdir("docs/")
    intersphinx_mapping = json.loads(
        session.run(
            "python",
            "-c",
            "import json; import conf; print(json.dumps(conf.intersphinx_mapping))",
            silent=True,
            log=False,
        )
    )
    try:
        mapping_entry = intersphinx_mapping[session.posargs[0]]
    except IndexError:
        session.error(
            "You need to pass at least one argument whose value must be one of: {}".format(
                ", ".join(list(intersphinx_mapping))
            )
        )
    except KeyError:
        session.error(
            "Only acceptable values for first argument are: {}".format(
                ", ".join(list(intersphinx_mapping))
            )
        )
    session.run(
        "python", "-m", "sphinx.ext.intersphinx", mapping_entry[0].rstrip("/") + "/objects.inv"
    )
    os.chdir("..")


@nox.session(name="gen-api-docs", python="3")
def gen_api_docs(session):
    """
    Generate API Docs.
    """
    session.install("--progress-bar=off", "-e", ".[docs]", silent=PIP_INSTALL_SILENT)
    shutil.rmtree("docs/ref", ignore_errors=True)
    session.run(
        "sphinx-apidoc", "--module-first", "-o", "docs/ref/", "src/pytest_helpers_namespace/"
    )


@nox.session(name="twine-check", python="3")
def twine_check(session):
    """
    Run ``twine-check`` against the source distribution package.
    """
    session.install("--progress-bar=off", "twine", silent=PIP_INSTALL_SILENT)
    session.run(
        "python",
        "setup.py",
        "sdist",
        silent=True,
        log=False,
    )
    session.run("twine", "check", "dist/*")


@nox.session(name="changelog", python="3")
@nox.parametrize("draft", [False, True])
def changelog(session, draft):
    """
    Generate changelog.
    """
    session.install("--progress-bar=off", "-e", ".[changelog]", silent=PIP_INSTALL_SILENT)
    version = session.run(
        "python",
        "setup.py",
        "--version",
        silent=True,
        log=False,
        stderr=None,
    )

    town_cmd = ["towncrier", "build", "--version={}".format(version.strip())]
    if draft:
        town_cmd.append("--draft")
    session.run(*town_cmd)


@nox.session(name="release")
def release(session):
    """
    Create a release tag.
    """
    if not session.posargs:
        session.error(
            "Forgot to pass the version to release? For example `nox -e release -- 1.1.0`"
        )
    if len(session.posargs) > 1:
        session.error(
            "Only one argument is supported by the `release` nox session. "
            "For example `nox -e release -- 1.1.0`"
        )
    version = session.posargs[0]
    try:
        session.log("Generating temporary %s tag", version)
        session.run("git", "tag", "-as", version, "-m", "Release {}".format(version), external=True)
        changelog(session, draft=False)
    except CommandFailed:
        session.error("Failed to generate the temporary tag")
    # session.notify("changelog(draft=False)")
    try:
        session.log("Generating the release changelog")
        session.run(
            "git",
            "commit",
            "-a",
            "-m",
            "Generate Changelog for version {}".format(version),
            external=True,
        )
    except CommandFailed:
        session.error("Failed to generate the release changelog")
    try:
        session.log("Overwriting temporary %s tag", version)
        session.run(
            "git", "tag", "-fas", version, "-m", "Release {}".format(version), external=True
        )
    except CommandFailed:
        session.error("Failed to overwrite the temporary tag")
    session.warn("Don't forget to push the newly created tag")
