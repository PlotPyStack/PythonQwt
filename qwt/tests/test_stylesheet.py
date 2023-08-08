# -*- coding: utf-8 -*-

SHOW = True  # Show test in GUI-based test launcher

import numpy as np
from qtpy.QtCore import Qt

import qwt
from qwt.tests import utils


class StyleSheetPlot(qwt.QwtPlot):
    def __init__(self):
        super().__init__()
        self.setTitle("Stylesheet test (Issue #63)")
        self.setStyleSheet("background-color: #19232D; color: #E0E1E3;")
        qwt.QwtPlotGrid.make(self, color=Qt.white, width=0, style=Qt.DotLine)
        x = np.arange(-5.0, 5.0, 0.1)
        qwt.QwtPlotCurve.make(x, np.sinc(x), "y = sinc(x)", self, linecolor="green")


def test_stylesheet():
    """Stylesheet test"""
    utils.test_widget(StyleSheetPlot, size=(600, 400))


if __name__ == "__main__":
    test_stylesheet()
