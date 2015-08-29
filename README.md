python-qwt
==========

Purpose and Motivation
----------------------

The ``python-qwt`` project was initiated to solve -at least temporarily-
the obsolescence issue of `PyQwt` (the Python-Qwt C++ bindings library)
which is no longer maintained. The idea was to translate the original
Qwt C++ code to Python and then to optimize some parts of the code by
writing new modules based on NumPy and other libraries.

The ``python-qwt`` package consists of a single Python package named
`qwt` and of a few other files (examples, doc, ...).


Copyrights
----------

### Main code base ###
Copyright (c) 2002 Uwe Rathmann, for the original Qwt C++ code
Copyright (c) 2015 Pierre Raybaut, for the Qwt C++ to Python
translation and optimization
Copyright (c) 2015 Pierre Raybaut, for the python-qwt specific and
exclusive Python material

### PyQt, PySide and Python2/Python3 compatibility modules ###
Copyright (c) 2009-2013 Pierre Raybaut
Copyright (c) 2013-2015 The Spyder Development Team

### Some examples ###
Copyright (C) 2003-2009 Gerard Vermeulen, for the original PyQwt code
Copyright (c) 2015 Pierre Raybaut, for the PyQt5/PySide port and
further developments (e.g. ported to python-qwt API)


License
-------

The `qwt` Python package was partly (>95%) translated from Qwt C++
library: the associated code is distributed under the terms of the LGPL
license. The rest of the code was either wrote from scratch or strongly
inspired from MIT licensed third-party software.
See included LICENSE file for more details about licensing terms.


Overview
--------

The `qwt` package is a pure Python implementation of Qwt C++ library with
the following limitations.

The following `Qwt` classes won't be reimplemented in `qwt` because most
powerful features already exist in `guiqwt`:
- QwtPlotZoomer
- QwtCounter
- QwtEventPattern
- QwtPicker
- QwtPlotPicker

QwtClipper is not implemented yet (and it will probably be very difficult
or impossible to implement it in pure Python without performance issues).
As a consequence, when zooming in a plot curve, the entire curve is still
painted (in other words, when working with large amount of data, there is
no performance gain when zooming in).


Dependencies
------------

### Requirements ###
- Python >=2.6 or Python >=3.0
- PyQt4 >=4.4 or PyQt5 >= 5.5
- NumPy >= 1.5


Installation
------------

From the source package:

    python setup.py install
