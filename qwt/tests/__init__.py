# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""
PythonQwt test package
======================
"""

from __future__ import print_function

import os
import os.path as osp
import sys
import subprocess
import platform
from qwt.qt.QtGui import (QWidget, QMainWindow, QVBoxLayout, QFormLayout,
                          QCheckBox, QGroupBox, QGridLayout, QToolButton,
                          QStyle, QToolBar, QAction, QIcon, QMessageBox)
from qwt.qt.QtCore import Qt, QSize
from qwt import QwtPlot


TEST_PATH = osp.abspath(osp.dirname(__file__))


def run_test(fname, wait=False):
    """Run test"""
    os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)
    args = " ".join([sys.executable, '"'+fname+'"'])
    if os.environ.get("TEST_UNATTENDED") is not None:
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


def run_all_tests(wait):
    """Run all PythonQwt tests"""
    import qwt
    for fname in get_tests(qwt):
        run_test(fname, wait=wait)


class TestLauncher(QMainWindow):
    """PythonQwt Test Launcher main window"""
    ROWS = 5
    def __init__(self, parent=None):
        super(TestLauncher, self).__init__(parent)
        from qwt import __version__
        self.setWindowIcon(self.get_std_icon("FileDialogListView"))
        self.setWindowTitle("PythonQwt %s - Test Launcher" % __version__)
        self.setCentralWidget(QWidget())
        self.grid_layout = QGridLayout()
        self.centralWidget().setLayout(self.grid_layout)
        self.test_nb = None
        self.fill_layout()
        self.statusBar().show()
        self.setStatusTip("Click on any button to run a test")

    def get_std_icon(self, name):
        """Return Qt standard icon"""
        return self.style().standardIcon(getattr(QStyle, "SP_" + name))

    def fill_layout(self):
        """Fill grid layout"""
        import qwt
        for fname in get_tests(qwt):
            self.add_test(fname)
        toolbar = QToolBar(self)
        all_act = QAction(self.get_std_icon("DialogYesButton"), "", self)
        all_act.setIconText("Run all tests")
        all_act.triggered.connect(lambda checked: run_all_tests(wait=False))
        folder_act = QAction(self.get_std_icon("DirOpenIcon"), "", self)
        folder_act.setIconText("Open tests folder")
        open_test_folder = lambda checked: os.startfile(TEST_PATH)
        folder_act.triggered.connect(open_test_folder)
        about_act = QAction(self.get_std_icon("FileDialogInfoView"), "", self)
        about_act.setIconText("About")
        about_act.triggered.connect(self.about)
        for action in (all_act, folder_act, None, about_act):
            if action is None:
                toolbar.addSeparator()
            else:
                toolbar.addAction(action)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

    def add_test(self, fname):
        """Add new test"""
        if self.test_nb is None:
            self.test_nb = 0
        self.test_nb += 1
        row = (self.test_nb-1) % self.ROWS
        column = (self.test_nb-1) // self.ROWS
        bname = osp.basename(fname)
        button = QToolButton(self)
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        shot = osp.join(TEST_PATH, "data", bname.replace(".py", ".png"))
        if osp.isfile(shot):
            button.setIcon(QIcon(shot))
        else:
            button.setIcon(self.get_std_icon("DialogYesButton"))
        button.setText(bname)
        button.setToolTip(fname)
        button.setIconSize(QSize(130, 80))
        button.clicked.connect(lambda checked, fname=fname: run_test(fname))
        self.grid_layout.addWidget(button, row, column)
        
    def about(self):
        """About test launcher"""
        from qwt.qt.QtCore import __version__ as qt_version
        QMessageBox.about( self, "About "+self.windowTitle(),
              """<b>%s</b><p>Developped by Pierre Raybaut
              <br>Copyright &copy; 2020 Pierre Raybaut
              <p>Python %s, Qt %s on %s""" % \
              (self.windowTitle(), platform.python_version(),
               qt_version, platform.system()) )


def run(wait=True):
    """Run PythonQwt tests or test launcher (requires `guidata`)"""
    if os.environ.get("TEST_UNATTENDED") is None:
        from qwt.qt.QtGui import QApplication
        app = QApplication([])
        launcher = TestLauncher()
        launcher.show()
        app.exec_()
    else:
        run_all_tests(wait=wait)


class TestOptions(QGroupBox):
    """Test options groupbox"""
    def __init__(self, parent=None):
        super(TestOptions, self).__init__("Test options", parent)
        self.setLayout(QFormLayout())
        self.hide()

    def add_checkbox(self, title, label, slot):
        """Add new checkbox to option panel"""
        widget = QCheckBox(label, self)
        widget.stateChanged.connect(slot)
        self.layout().addRow(title, widget)
        self.show()
        return widget


class TestCentralWidget(QWidget):
    """Test central widget"""
    def __init__(self, parent=None):
        super(TestCentralWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.options = TestOptions(self)
        self.add_widget(self.options)

    def add_widget(self, widget):
        """Add new sub-widget"""
        self.layout().addWidget(widget)
        if isinstance(widget, QwtPlot):
            plots = [widget]
        else:
            plots = widget.findChildren(QwtPlot)
        for index, plot in enumerate(plots):
            plot_name = plot.objectName()
            if not plot_name:
                plot_name = "Plot #%d" % (index + 1)
            widget = self.options.add_checkbox(plot_name,
                            "Enable new flat style option", plot.setFlatStyle)
            widget.setChecked(plot.flatStyle())


class TestWindow(QMainWindow):
    """Test main window"""
    def __init__(self):
        super(TestWindow, self).__init__()
        self.setCentralWidget(TestCentralWidget())

    def add_widget(self, widget):
        """Add new sub-widget to central widget"""
        self.centralWidget().add_widget(widget)


def test_widget(widget_class, size=None, title=None, options=True):
    """Test widget"""
    from qwt.qt.QtGui import QApplication
    app = QApplication([])
    window = widget = widget_class()
    if options:
        if isinstance(widget, QMainWindow):
            original_central_widget = window.centralWidget()
            original_central_widget.setParent(None)
            new_central_widget = TestCentralWidget()
            window.setCentralWidget(new_central_widget)
            new_central_widget.add_widget(original_central_widget)
        else:
            window = TestWindow()
            window.add_widget(widget)
    if title is None:
        from qwt import __version__
        title = 'Test "%s" - PythonQwt %s' % (widget_class.__name__,
                                              __version__)
    window.setWindowTitle(title)
    if size is not None:
        width, height = size
        window.resize(width, height)

    window.show()
    if os.environ.get("TEST_UNATTENDED") is None:
        app.exec_()
    return app


if __name__ == '__main__':
    run()
