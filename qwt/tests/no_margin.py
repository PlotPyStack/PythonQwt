# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""Simple plot without margins"""

SHOW = True # Show test in GUI-based test launcher

import numpy as np

from qwt.qt.QtGui import QApplication, QFont, QPen, QPalette, QColor
from qwt.qt.QtCore import Qt

import os
if os.environ.get('USE_PYQWT5', True):
    USE_PYQWT5 = True
    from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtPlotMarker, QwtText
else:
    USE_PYQWT5 = False
    from qwt import QwtPlot, QwtPlotCurve, QwtPlotMarker, QwtText  # analysis:ignore


class TestPlot(QwtPlot):
    def __init__(self, parent=None):
        super(TestPlot, self).__init__(parent)
        self.setWindowTitle("PyQwt" if USE_PYQWT5 else "PythonQwt")
        self.enableAxis(self.xTop, True)
        self.enableAxis(self.yRight, True)
        y = np.linspace(0, 10, 500)
        curve1 = QwtPlotCurve('Test Curve 1')
        curve1.setData(np.sin(y), y)
        curve2 = QwtPlotCurve('Test Curve 2')
        curve2.setData(y**3, y)
        if USE_PYQWT5:
            curve2.setAxis(self.xTop, self.yRight)
        else:
            # PythonQwt
            curve2.setAxes(self.xTop, self.yRight)

        for item, col, xa, ya in ((curve1, Qt.green, self.xBottom, self.yLeft),
                                  (curve2, Qt.red, self.xTop, self.yRight)):
            if not USE_PYQWT5:
                # PythonQwt
                item.setOrientation(Qt.Vertical)
            item.attach(self)
            item.setPen(QPen(col))
            for axis_id in xa, ya:
                palette = self.axisWidget(axis_id).palette()
                palette.setColor(QPalette.WindowText, QColor(col))
                palette.setColor(QPalette.Text, QColor(col))
                self.axisWidget(axis_id).setPalette(palette)
                ticks_font = self.axisFont(axis_id)
                self.setAxisFont(axis_id, ticks_font)
        
        self.canvas().setFrameStyle(0)#QFrame.Panel|QFrame.Sunken)
        self.plotLayout().setCanvasMargin(0)
        self.axisWidget(QwtPlot.yLeft).setMargin(0)
        self.axisWidget(QwtPlot.xTop).setMargin(0)
        self.axisWidget(QwtPlot.yRight).setMargin(0)
        self.axisWidget(QwtPlot.xBottom).setMargin(0)

        self.marker = QwtPlotMarker()
        self.marker.setValue(0, 5)
        self.marker.attach(self)
        
    def resizeEvent(self, event):
        super(TestPlot, self).resizeEvent(event)
        self.show_layout_details()
    
    def show_layout_details(self):
        text = QwtText(
          "plotLayout().canvasRect():\n%r\n\n"
          "canvas().geometry():\n%r\n\n"
          "plotLayout().scaleRect(QwtPlot.yLeft):\n%r\n\n"
          "axisWidget(QwtPlot.yLeft).geometry():\n%r\n\n"
          "plotLayout().scaleRect(QwtPlot.yRight):\n%r\n\n"
          "axisWidget(QwtPlot.yRight).geometry():\n%r\n\n"
          "plotLayout().scaleRect(QwtPlot.xBottom):\n%r\n\n"
          "axisWidget(QwtPlot.xBottom).geometry():\n%r\n\n"
          "plotLayout().scaleRect(QwtPlot.xTop):\n%r\n\n"
          "axisWidget(QwtPlot.xTop).geometry():\n%r\n\n"
              % (self.plotLayout().canvasRect().getCoords(),
                 self.canvas().geometry().getCoords(),
                 self.plotLayout().scaleRect(QwtPlot.yLeft).getCoords(),
                 self.axisWidget(QwtPlot.yLeft).geometry().getCoords(),
                 self.plotLayout().scaleRect(QwtPlot.yRight).getCoords(),
                 self.axisWidget(QwtPlot.yRight).geometry().getCoords(),
                 self.plotLayout().scaleRect(QwtPlot.xBottom).getCoords(),
                 self.axisWidget(QwtPlot.xBottom).geometry().getCoords(),
                 self.plotLayout().scaleRect(QwtPlot.xTop).getCoords(),
                 self.axisWidget(QwtPlot.xTop).geometry().getCoords(),
                 )
                       )
        text.setFont(QFont('Courier New'))
        text.setColor(Qt.blue)
        self.marker.setLabel(text)

if __name__ == '__main__':
    app = QApplication([])
    plot = TestPlot()
    plot.resize(300, 1000)
    plot.show()
    app.exec_()
