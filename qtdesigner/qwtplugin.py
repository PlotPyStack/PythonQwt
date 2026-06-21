# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2015 Pierre Raybaut, for the Qt Designer plugin
# (see LICENSE file for more details)

"""
qwtplugin
=========

A :class:`qwt.QwtPlot` widget plugin for Qt Designer.

To make the ``QwtPlot`` widget available in Qt Designer, add the directory
containing this file to the ``PYQTDESIGNERPATH`` environment variable, then
start Qt Designer::

    set PYQTDESIGNERPATH=<path to this directory>    # Windows
    export PYQTDESIGNERPATH=<path to this directory> # Linux/macOS

The ``QwtPlot`` widget then appears in the "PythonQwt" group of the Qt Designer
widget box.

.. note::

    Qt Designer custom widget plugins require PyQt5 or PyQt6 (PySide6 does not
    expose ``QPyDesignerCustomWidgetPlugin``).
"""

from qwt.qtdesigner import create_qtdesigner_plugin

Plugin = create_qtdesigner_plugin(
    group="PythonQwt",
    module_name="qwt.plot",
    class_name="QwtPlot",
    tooltip="2D plotting widget",
    whatsthis="A 2D plotting widget based on PythonQwt",
)
