# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""
PythonQwt
=========

Qt plotting widgets for Python
"""

import os
import os.path as osp
from distutils.core import setup

import setuptools  # analysis:ignore

LIBNAME = "PythonQwt"
PACKAGE_NAME = "qwt"
from qwt import __version__ as version

DESCRIPTION = "Qt plotting widgets for Python"
LONG_DESCRIPTION = """\
PythonQwt: Qt plotting widgets for Python
=========================================

.. image:: https://raw.githubusercontent.com/PierreRaybaut/PythonQwt/master/qwt/tests/data/testlauncher.png

The ``PythonQwt`` package is a 2D-data plotting library using Qt graphical
user interfaces for the Python programming language. It is compatible with
``PyQt4``, ``PyQt5``, ``PyQt6`` and ``PySide6``.

The ``PythonQwt`` project was initiated to solve -at least temporarily- the
obsolescence issue of `PyQwt` (the Python-Qwt C++ bindings library) which is
no longer maintained. The idea was to translate the original Qwt C++ code to
Python and then to optimize some parts of the code by writing new modules
based on NumPy and other libraries.

The ``PythonQwt`` package consists of a single Python package named `qwt`
which is a pure Python implementation of Qwt C++ library with some
limitations: efforts were concentrated on basic plotting features, leaving
higher level features to the `guiqwt` library.

See `README`_ and documentation (`online`_ or `PDF`_) for more details on the library and `changelog`_ for recent history of changes.

The following example is a good starting point to see how to set up a simple plot widget::

    from qtpy import QtWidgets as QW
    import qwt
    import numpy as np

    app = QW.QApplication([])
    x = np.linspace(-10, 10, 500)
    plot = qwt.QwtPlot("Trigonometric functions")
    plot.insertLegend(qwt.QwtLegend(), qwt.QwtPlot.BottomLegend)
    qwt.QwtPlotCurve.make(x, np.cos(x), "Cosinus", plot, linecolor="red", antialiased=True)
    qwt.QwtPlotCurve.make(x, np.sin(x), "Sinus", plot, linecolor="blue", antialiased=True)
    plot.resize(600, 300)
    plot.show()
    app.exec_()

.. image:: https://raw.githubusercontent.com/PierreRaybaut/PythonQwt/master/doc/_static/QwtPlot_example.png

.. _README: https://github.com/PlotPyStack/PythonQwt/blob/master/README.md
.. _online: https://pythonqwt.readthedocs.io/en/latest/
.. _PDF: https://pythonqwt.readthedocs.io/_/downloads/en/latest/pdf/
.. _changelog: https://github.com/PlotPyStack/PythonQwt/blob/master/CHANGELOG.md
"""
KEYWORDS = ""
CLASSIFIERS = []
if "beta" in version or "b" in version:
    CLASSIFIERS += ["Development Status :: 4 - Beta"]
elif "alpha" in version or "a" in version:
    CLASSIFIERS += ["Development Status :: 3 - Alpha"]
else:
    CLASSIFIERS += ["Development Status :: 5 - Production/Stable"]


def get_package_data(name, extlist):
    """Return data files for package *name* with extensions in *extlist*"""
    flist = []
    # Workaround to replace os.path.relpath (not available until Python 2.6):
    offset = len(name) + len(os.pathsep)
    for dirpath, _dirnames, filenames in os.walk(name):
        for fname in filenames:
            if not fname.startswith(".") and osp.splitext(fname)[1] in extlist:
                flist.append(osp.join(dirpath, fname)[offset:])
    return flist


def get_subpackages(name):
    """Return subpackages of package *name*"""
    splist = []
    for dirpath, _dirnames, _filenames in os.walk(name):
        if osp.isfile(osp.join(dirpath, "__init__.py")):
            splist.append(".".join(dirpath.split(os.sep)))
    return splist


setup(
    name=LIBNAME,
    version=version,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=get_subpackages(PACKAGE_NAME),
    package_data={
        PACKAGE_NAME: get_package_data(PACKAGE_NAME, (".png", ".svg", ".mo"))
    },
    install_requires=["NumPy>=1.5", "QtPy>=1.3"],
    extras_require={
        "doc": ["Sphinx>=1.1"],
        "test": ["coverage", "pytest", "pytest-qt", "pytest-cov"],
    },
    entry_points={
        "gui_scripts": [
            "PythonQwt = qwt.tests:run [Tests]",
        ],
        "console_scripts": [
            "PythonQwt-tests = qwt.tests:run [Tests]",
        ],
    },
    author="Pierre Raybaut",
    author_email="pierre.raybaut@gmail.com",
    url="https://github.com/PlotPyStack/%s" % LIBNAME,
    platforms="Any",
    classifiers=CLASSIFIERS
    + [
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Widget Sets",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
    ],
)
