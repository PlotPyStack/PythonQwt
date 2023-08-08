# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""
PythonQwt test package
======================
"""

from qtpy import QtWidgets as QW
from qtpy import QtCore as QC

from qwt.tests.utils import TestEnvironment, TestLauncher, take_screenshot, run_all_tests, QT_API


def run(wait=True):
    """Run PythonQwt tests or test launcher"""
    app = QW.QApplication([])
    launcher = TestLauncher()
    launcher.show()
    test_env = TestEnvironment()
    if test_env.screenshots:
        print("Running PythonQwt tests and taking screenshots automatically:")
        QC.QTimer.singleShot(100, lambda: take_screenshot(launcher))
    elif test_env.unattended:
        print("Running PythonQwt tests in unattended mode:")
        QC.QTimer.singleShot(0, QW.QApplication.instance().quit)
    if QT_API == "pyside6":
        app.exec()
    else:
        app.exec_()
    launcher.close()
    if test_env.unattended:
        run_all_tests(wait=wait)


if __name__ == "__main__":
    run()
