# -*- coding: utf-8 -*-
#
# Licensed under the terms of the PyQwt License
# Copyright (C) 2003-2009 Gerard Vermeulen, for the original PyQwt example
# Copyright (c) 2015 Pierre Raybaut, for the PyQt5/PySide port and further
# developments (e.g. ported to PythonQwt API)
# (see LICENSE file for more details)

SHOW = True  # Show test in GUI-based test launcher

from qtpy import QtWidgets as QW
from qtpy.QtCore import Qt

import qwt
from qwt.tests import utils


class RelativeMarginDemo(QW.QWidget):
    def __init__(self, *args):
        QW.QWidget.__init__(self, *args)
        layout = QW.QGridLayout(self)
        x = [1, 2, 3, 4]
        y = [1, 500, 1000, 1500]
        for i_row, log_scale in enumerate((False, True)):
            for i_col, relative_margin in enumerate((0.0, None, 0.2)):
                plot = qwt.QwtPlot(self)
                qwt.QwtPlotGrid.make(
                    plot, color=Qt.lightGray, width=0, style=Qt.DotLine
                )
                def_margin = plot.axisMargin(qwt.QwtPlot.yLeft)
                scale_str = "lin/lin" if not log_scale else "log/lin"
                if relative_margin is None:
                    margin_str = f"default ({def_margin*100:.0f}%)"
                else:
                    margin_str = f"{relative_margin*100:.0f}%"
                plot.setTitle(f"{scale_str}, margin: {margin_str}")
                if relative_margin is not None:
                    plot.setAxisMargin(qwt.QwtPlot.yLeft, relative_margin)
                    plot.setAxisMargin(qwt.QwtPlot.xBottom, relative_margin)
                color = "red" if i_row == 0 else "blue"
                qwt.QwtPlotCurve.make(x, y, "", plot, linecolor=color)
                layout.addWidget(plot, i_row, i_col)
                if log_scale:
                    engine = qwt.QwtLogScaleEngine()
                    plot.setAxisScaleEngine(qwt.QwtPlot.yLeft, engine)


def test_relative_margin():
    """Test relative margin."""
    utils.test_widget(RelativeMarginDemo, size=(400, 300), options=False)


if __name__ == "__main__":
    test_relative_margin()
