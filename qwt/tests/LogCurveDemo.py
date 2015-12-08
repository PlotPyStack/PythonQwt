# -*- coding: utf-8 -*-
#
# Licensed under the terms of the PyQwt License
# Copyright (C) 2003-2009 Gerard Vermeulen, for the original PyQwt example
# Copyright (c) 2015 Pierre Raybaut, for the PyQt5/PySide port and further 
# developments (e.g. ported to PythonQwt API)
# (see LICENSE file for more details)

SHOW = True # Show test in GUI-based test launcher

import numpy as np

np.seterr(all='raise')

from qwt.qt.QtGui import QApplication, QPen
from qwt.qt.QtCore import Qt
from qwt import QwtPlot, QwtPlotCurve, QwtLogScaleEngine


def create_log_plot():
    plot = QwtPlot('LogCurveDemo.py (or how to handle -inf values)')
    plot.enableAxis(QwtPlot.xBottom)
    plot.setAxisScaleEngine(QwtPlot.yLeft, QwtLogScaleEngine())
    curve = QwtPlotCurve()
    curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
    pen = QPen(Qt.magenta)
    pen.setWidth(1.5)
    curve.setPen(pen)
    curve.attach(plot)
    x = np.arange(0.0, 10.0, 0.1)
    y = 10*np.cos(x)**2-.1
    print("y<=0:", y<=0)
    curve.setData(x, y)
    plot.replot()
    return plot


if __name__ == '__main__':
    app = QApplication([])
    plot = create_log_plot()
    plot.resize(800, 500)
    plot.show()
    app.exec_()
