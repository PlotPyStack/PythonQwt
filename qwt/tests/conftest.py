# -*- coding: utf-8 -*-

"""pytest configuration for PythonQwt package tests."""

import os
from qwt.tests.utils import TestEnvironment

# Set the unattended environment variable to 1 to avoid any user interaction
os.environ[TestEnvironment.UNATTENDED_ENV] = "1"
