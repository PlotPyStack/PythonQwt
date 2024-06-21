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
