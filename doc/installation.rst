Installation
============

Dependencies
------------

Requirements:
    * Python 2.x (x>=6) or 3.x (x>=2)
    * PyQt4 4.x (x>=4) or PyQt5 5.x (x>=5) or PySide2 (still experimental, see below)
    * QtPy >= 1.3
    * NumPy 1.x (x>=5)
    * Sphinx 1.x (x>=1) for documentation generation

Installation
------------

From the source package:

    `python setup.py install`

Why PySide2 support is still experimental
-----------------------------------------

.. image:: /images/pyqt5_vs_pyside2.png

Try running the `curvebenchmark1.py` test with PyQt5 and PySide: you will notice a 
huge performance issue with PySide2 (see screenshot above). This is due to the fact 
that PyQt5 (and PyQt4) allows an efficient way of filling a QPolygonF object from a 
Numpy array, and PySide2 is not (see code below).

.. literalinclude:: /../qwt/plot_curve.py
   :pyobject: series_to_polyline

As a consequence, until an equivalent feature is implemented in PySide2, we strongly 
recommend using PyQt5 instead of PySide2.

Help and support
----------------

External resources:

    * Bug reports and feature requests: `GitHub`_

.. _GitHub: https://github.com/PierreRaybaut/PythonQwt
