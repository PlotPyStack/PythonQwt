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
that `QPainter.drawPolyline` is much more efficient in PyQt5 than it is in PySide2 
(see `this bug report <https://bugreports.qt.io/projects/PYSIDE/issues/PYSIDE-1366>`_).

As a consequence, until this bug is fixed in PySide2, we still recommend using PyQt5 
instead of PySide2 when it comes to representing huge data sets.

However, PySide2 support was significatively improved betwen PythonQwt V0.8.0 and 
V0.8.1 thanks to the new `array2d_to_qpolygonf` function (see code below).

.. literalinclude:: /../qwt/plot_curve.py
   :pyobject: array2d_to_qpolygonf

Help and support
----------------

External resources:

    * Bug reports and feature requests: `GitHub`_

.. _GitHub: https://github.com/PierreRaybaut/PythonQwt
