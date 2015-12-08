# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""Curve benchmark example"""

SHOW = True # Show test in GUI-based test launcher

import time
import numpy as np
import sys

from qwt.qt.QtGui import (QApplication, QPen, QMainWindow, QGridLayout,
                          QTabWidget, QWidget, QTextEdit, QLineEdit, QFont,
                          QFontDatabase)
from qwt.qt.QtCore import Qt

import os
if os.environ.get('USE_PYQWT5', False):
    USE_PYQWT5 = True
    from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve
else:
    USE_PYQWT5 = False
    from qwt import QwtPlot, QwtPlotCurve  # analysis:ignore


COLOR_INDEX = None

def get_curve_color():
    global COLOR_INDEX
    colors = (Qt.blue, Qt.red, Qt.green, Qt.yellow, Qt.magenta, Qt.cyan)
    if COLOR_INDEX is None:
        COLOR_INDEX = 0
    else:
        COLOR_INDEX = (COLOR_INDEX + 1) % len(colors)
    return colors[COLOR_INDEX]


class BMPlot(QwtPlot):
    def __init__(self, title, xdata, ydata, style, symbol=None, *args):
        super(BMPlot, self).__init__(*args)
        self.setMinimumSize(200, 200)
        self.setTitle(title)
        self.setAxisTitle(QwtPlot.xBottom, 'x')
        self.setAxisTitle(QwtPlot.yLeft, 'y')
        self.curve_nb = 0
        for idx in range(1, 11):
            self.curve_nb += 1
            curve = QwtPlotCurve()
            curve.setPen(QPen(get_curve_color()))
            curve.setStyle(style)
            curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
            if symbol is not None:
                curve.setSymbol(symbol)
            curve.attach(self)
            curve.setData(xdata, ydata*idx, finite=False)
#        self.setAxisScale(self.yLeft, -1.5, 1.5)
#        self.setAxisScale(self.xBottom, 9.9, 10.)
        self.replot()


class BMWidget(QWidget):
    def __init__(self, points, *args, **kwargs):
        super(BMWidget, self).__init__()
        self.plot_nb = 0
        self.curve_nb = 0
        self.setup(points, *args, **kwargs)
    
    def params(self, *args, **kwargs):
        if kwargs.get('only_lines', False):
            return (('Lines', None),)
        else:
            return (
                    ('Lines', None),
                    ('Dots', None),
                    )
    
    def setup(self, points, *args, **kwargs):
        x = np.linspace(.001, 20., points)
        y = (np.sin(x)/x)*np.cos(20*x)
        layout = QGridLayout()
        nbcol, col, row = 2, 0, 0
        for style, symbol in self.params(*args, **kwargs):
           plot = BMPlot(style, x, y, getattr(QwtPlotCurve, style),
                         symbol=symbol)
           layout.addWidget(plot, row, col)
           self.plot_nb += 1
           self.curve_nb += plot.curve_nb
           col += 1
           if col >= nbcol:
               row +=1
               col = 0
        self.text = QLineEdit()
        self.text.setReadOnly(True)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setText("Rendering plot...")
        layout.addWidget(self.text, row+1, 0, 1, 2)
        self.setLayout(layout)           


class BMText(QTextEdit):
    def __init__(self, parent=None, title=None):
        super(BMText, self).__init__(parent)
        self.setReadOnly(True)
        library = 'PyQwt5' if USE_PYQWT5 else 'PythonQwt'
        wintitle = self.parent().windowTitle()
        if not wintitle:
            wintitle = "Benchmark"
        if title is None:
            title = '%s example' % wintitle
        self.parent().setWindowTitle('%s [%s]' % (wintitle, library))
        self.setText("""\
<b>%s:</b><br>
(base plotting library: %s)<br><br>
Click on each tab to test if plotting performance is acceptable in terms of 
GUI response time (switch between tabs, resize main windows, ...).<br>
<br><br>
<b>Benchmarks results:</b>
""" % (title, library))


class BMDemo(QMainWindow):
    TITLE = 'Curve benchmark'
    SIZE = (1000, 800)
    def __init__(self, max_n, parent=None, **kwargs):
        super(BMDemo, self).__init__(parent=parent)
        title = self.TITLE
        if kwargs.get('only_lines', False):
            title = '%s (%s)' % (title, 'only lines')
        self.setWindowTitle(title)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.text = BMText(self)
        self.tabs.addTab(self.text, 'Contents')
        self.resize(*self.SIZE)

        # Force window to show up and refresh (for test purpose only)
        self.show()
        QApplication.processEvents()
        
        t0g = time.time()
        self.run_benchmark(max_n, **kwargs)
        dt = time.time()-t0g
        self.text.append("<br><br><u>Total elapsed time</u>: %d ms" % (dt*1e3))
        self.tabs.setCurrentIndex(0)
        
    def process_iteration(self, title, description, widget, t0):
        self.tabs.addTab(widget, title)
        self.tabs.setCurrentWidget(widget)

        # Force widget to refresh (for test purpose only)
        QApplication.processEvents()

        time_str = "Elapsed time: %d ms" % ((time.time()-t0)*1000)
        widget.text.setText(time_str)
        self.text.append("<br><i>%s:</i><br>%s" % (description, time_str))

    def run_benchmark(self, max_n, **kwargs):
        for idx in range(4, -1, -1):
            points = max_n/10**idx
            t0 = time.time()
            widget = BMWidget(points, **kwargs)
            title = '%d points' % points
            description = '%d plots with %d curves of %d points' % (
                          widget.plot_nb, widget.curve_nb, points)
            self.process_iteration(title, description, widget, t0)


if __name__ == '__main__':
    app = QApplication([])
    for name in ('Calibri', 'Verdana', 'Arial'):
        if name in QFontDatabase().families():
            app.setFont(QFont(name))
            break
    kwargs = {}
    for arg in sys.argv[1:]:
        kwargs[arg] = True
    demo = BMDemo(1000000, **kwargs)
    app.exec_()
