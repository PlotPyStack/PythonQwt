# -*- coding: utf-8 -*-

"""pytest configuration for PythonQwt package tests."""

import os

import qtpy

import qwt
from qwt.tests.utils import TestEnvironment

# Set the unattended environment variable to 1 to avoid any user interaction
os.environ[TestEnvironment.UNATTENDED_ENV] = "1"


def pytest_report_header(config):
    """Add additional information to the pytest report header."""
    qtbindings_version = qtpy.PYSIDE_VERSION
    if qtbindings_version is None:
        qtbindings_version = qtpy.PYQT_VERSION
    return [
        f"PythonQwt {qwt.__version__} [closest Qwt version: {qwt.QWT_VERSION_STR}]",
        f"{qtpy.API_NAME} {qtbindings_version} [Qt version: {qtpy.QT_VERSION}]",
    ]


def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    # See this StackOverflow answer for more information: https://t.ly/9anqz
    parser.addoption(
        "--repeat", action="store", help="Number of times to repeat each test"
    )


def pytest_generate_tests(metafunc):
    """Generate tests for the given metafunc."""
    # See this StackOverflow answer for more information: https://t.ly/9anqz
    if metafunc.config.option.repeat is not None:
        count = int(metafunc.config.option.repeat)

        # We're going to duplicate these tests by parametrizing them,
        # which requires that each test has a fixture to accept the parameter.
        # We can add a new fixture like so:
        metafunc.fixturenames.append("tmp_ct")

        # Now we parametrize. This is what happens when we do e.g.,
        # @pytest.mark.parametrize('tmp_ct', range(count))
        # def test_foo(): pass
        metafunc.parametrize("tmp_ct", range(count))
