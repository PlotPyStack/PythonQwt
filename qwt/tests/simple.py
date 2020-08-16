# -*- coding: utf-8 -*-
#
# Licensed under the terms of the PyQwt License
# Copyright (C) 2003-2009 Gerard Vermeulen, for the original PyQwt example
# Copyright (c) 2015 Pierre Raybaut, for the PyQt5/PySide port and further
# developments (e.g. ported to PythonQwt API)
# (see LICENSE file for more details)

SHOW = True  # Show test in GUI-based test launcher

import numpy as np

from qwt.qt.QtGui import QPen
from qwt.qt.QtCore import Qt
from qwt import QwtPlot, QwtPlotMarker, QwtLegend, QwtPlotCurve, QwtText


class SimplePlot(QwtPlot):
    def __init__(self):
        QwtPlot.__init__(self)
        self.setTitle("ReallySimpleDemo.py")
        self.insertLegend(QwtLegend(), QwtPlot.RightLegend)
        self.setAxisTitle(QwtPlot.xBottom, "X-axis")
        self.setAxisTitle(QwtPlot.yLeft, "Y-axis")
        self.enableAxis(self.xBottom)

        x = np.arange(0.0, 10.0, 0.1)

        # insert a few curves
        QwtPlotCurve.make(x, np.sin(x), "y = sin(x)", self, linecolor=Qt.red)
        QwtPlotCurve.make(x, np.cos(x), "y = cos(x)", self, linecolor=Qt.blue)

        # insert a horizontal marker at y = 0
        QwtPlotMarker.make(
            label="y = 0",
            align=Qt.AlignRight | Qt.AlignTop,
            linestyle=QwtPlotMarker.HLine,
            plot=self,
        )

        # insert a vertical marker at x = 2 pi
        QwtPlotMarker.make(
            xvalue=2 * np.pi,
            label="x = 2 pi",
            align=Qt.AlignRight | Qt.AlignTop,
            linestyle=QwtPlotMarker.VLine,
            plot=self,
        )

        self.replot()


if __name__ == "__main__":
    from qwt.tests import test_widget

    app = test_widget(SimplePlot, size=(800, 500))
