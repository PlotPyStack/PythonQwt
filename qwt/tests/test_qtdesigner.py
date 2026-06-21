# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2015 Pierre Raybaut, for the Qt Designer plugin test
# (see LICENSE file for more details)

"""
Testing PythonQwt Qt Designer plugin

This plugin makes the :class:`qwt.QwtPlot` widget available in Qt Designer.
The test loads a ``.ui`` file embedding a ``QwtPlot`` widget, as Qt Designer
would generate it once the plugin is installed.
"""

SHOW = True  # Show test in GUI-based test launcher

import os.path as osp

import numpy as np
import pytest
from qtpy.QtCore import Qt

import qwt
from qwt.qtdesigner import loadui
from qwt.tests import utils

try:
    FormClass = loadui(osp.splitext(__file__)[0] + ".ui")
except Exception as exc:  # pragma: no cover - binding-specific uic limitation
    pytest.skip(
        "Qt Designer .ui loading is not supported by this Qt binding (%s)" % exc,
        allow_module_level=True,
    )


class QtDesignerWindow(FormClass):
    """Window built from the Qt Designer ``.ui`` file"""

    def __init__(self):
        super().__init__()
        plot = self.plotwidget
        plot.setTitle("QtDesigner plugin example")
        x = np.linspace(0.0, 10.0, 500)
        qwt.QwtPlotCurve.make(x, np.sin(x), "y = sin(x)", plot, linecolor="red")
        qwt.QwtPlotGrid.make(plot, color=Qt.lightGray, width=0, style=Qt.DotLine)
        plot.replot()


def test_qtdesigner():
    """Qt Designer plugin example"""
    utils.test_widget(QtDesignerWindow, size=(600, 400))


if __name__ == "__main__":
    test_qtdesigner()
