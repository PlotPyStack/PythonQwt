# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""Curve benchmark example"""

SHOW = True # Show test in GUI-based test launcher

import time
import numpy as np

from qwt.qt.QtGui import (QApplication, QPen, QBrush, QMainWindow, QGridLayout,
                          QTabWidget, QWidget, QTextEdit, QLineEdit, QFont,
                          QFontDatabase)
from qwt.qt.QtCore import QSize
from qwt.qt.QtCore import Qt
from qwt import QwtPlot, QwtSymbol, QwtPlotCurve


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
        curve = QwtPlotCurve()
        curve.setPen(QPen(get_curve_color()))
        curve.setStyle(style)
        curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
        if symbol is not None:
            curve.setSymbol(symbol)
        curve.attach(self)
        curve.setData(xdata, ydata)
        self.replot()


class BMWidget(QWidget):
    def __init__(self, points, *args):
        super(BMWidget, self).__init__()
        self.setup(points, *args)
    
    def params(self, *args):
        return (
                ('Lines', None),
                ('Dots', None),
                )
    
    def setup(self, points, *args):
        x = np.linspace(.001, 20., points)
        y = (np.sin(x)/x)*np.cos(20*x)
        layout = QGridLayout()
        nbcol, col, row = 2, 0, 0
        for style, symbol in self.params(*args):
           layout.addWidget(BMPlot(style, x, y, getattr(QwtPlotCurve, style),
                                   symbol=symbol), row, col)
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
    def __init__(self, parent=None):
        super(BMText, self).__init__(parent)
        self.setReadOnly(True)
        self.setText("""\
<b>Curve benchmark example:</b><br><br>
Click on each tab to test if plotting performance is acceptable in terms of 
GUI response time (switch between tabs, resize main windows, ...).<br>
<br><br>
<b>Benchmarks results:</b>
""")


class BMDemo(QMainWindow):
    def __init__(self, max_n, parent=None, **kwargs):
        super(BMDemo, self).__init__(parent=parent)
        self.setWindowTitle('Curve benchmark')
        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        contents = BMText()
        tabs.addTab(contents, 'Contents')
        self.resize(1000, 600)

        # Force window to show up and refresh (for test purpose only)
        self.show()
        QApplication.processEvents()

        t0g = time.time()
        for idx in range(4, -1, -1):
            points = max_n/10**idx
            t0 = time.time()
            widget = BMWidget(points)
            title = '%d points' % points
            tabs.addTab(widget, title)
            tabs.setCurrentWidget(widget)

            # Force widget to refresh (for test purpose only)
            QApplication.processEvents()

            time_str = "Elapsed time: %d ms" % ((time.time()-t0)*1000)
            widget.text.setText(time_str)
            contents.append("<br><i>%s:</i><br>%s" % (title, time_str))
        dt = time.time()-t0g
        contents.append("<br><br><u>Total elapsed time</u>: %d ms" % (dt*1000))
        tabs.setCurrentIndex(0)


if __name__ == '__main__':
    app = QApplication([])
    for name in ('Calibri', 'Verdana', 'Arial'):
        if name in QFontDatabase().families():
            app.setFont(QFont(name))
            break
    demo = BMDemo(1000000)
    app.exec_()
