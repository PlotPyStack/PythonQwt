# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""
PythonQwt test package
======================
"""

import os
import os.path as osp
import sys
import subprocess


def run_test(fname, wait=False):
    """Run test"""
    os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)
    args = " ".join([sys.executable, '"'+fname+'"'])
    print(args)
    if wait:
        subprocess.call(args, shell=True)
    else:
        subprocess.Popen(args, shell=True)


def get_tests(package):
    """Return list of test filenames"""
    test_package_name = '%s.tests' % package.__name__
    _temp = __import__(test_package_name)
    test_package = sys.modules[test_package_name]
    tests = []
    test_path = osp.dirname(osp.realpath(test_package.__file__))
    for fname in sorted([name for name in os.listdir(test_path)
                         if name.endswith(('.py', '.pyw')) and\
                         not name.startswith('_')]):
        module_name = osp.splitext(fname)[0]
        _temp = __import__(test_package.__name__, fromlist=[module_name])
        module = getattr(_temp, module_name)
        if hasattr(module, 'SHOW') and module.SHOW:
            tests.append(osp.abspath(osp.join(test_path, fname)))
    return tests


def run():
    """Run PythonQwt tests or test launcher (requires `guidata`)"""
    import qwt
    if os.environ.get("TEST_UNATTENDED") is None:
        try:
            from guidata.guitest import run_testlauncher
            run_testlauncher(qwt)
            return
        except ImportError:
            pass
    for fname in get_tests(qwt):
        run_test(fname, wait=True)


def test_widget(widget_class, size=None, title=None):
    """Test widget"""
    from qwt.qt.QtGui import QApplication
    app = QApplication([])
    widget = widget_class()
    if title is None:
        from qwt import __version__
        title = 'Test "%s" - PythonQwt %s' % (widget_class.__name__,
                                              __version__)
    widget.setWindowTitle(title)
    if size is not None:
        width, height = size
        widget.resize(width, height)
    widget.show()
    if os.environ.get("TEST_UNATTENDED") is None:
        app.exec_()
    return app


if __name__ == '__main__':
    run()
    