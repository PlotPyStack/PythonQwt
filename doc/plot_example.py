import os.path as osp

import numpy as np
from qtpy import QtWidgets as QW

import qwt
from qwt import qthelpers as qth

app = QW.QApplication([])
x = np.linspace(-10, 10, 500)
plot = qwt.QwtPlot("Trigonometric functions")
plot.insertLegend(qwt.QwtLegend(), qwt.QwtPlot.BottomLegend)
qwt.QwtPlotCurve.make(x, np.cos(x), "Cosine", plot, linecolor="red", antialiased=True)
qwt.QwtPlotCurve.make(x, np.sin(x), "Sine", plot, linecolor="blue", antialiased=True)
qth.take_screenshot(
    plot,
    osp.join(osp.abspath(osp.dirname(__file__)), "_static", "QwtPlot_example.png"),
    size=(600, 300),
)
