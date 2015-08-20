#!/usr/bin/env python

#FIXME: scale issue!

import sys
from PyQt4 import Qt
import qwt as Qwt
import numpy as np

Size = 15
USize = 13

class CurveDemo(Qt.QFrame):

    def __init__(self, *args):
        Qt.QFrame.__init__(self, *args)

        self.setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Raised)
        self.setLineWidth(2)
        self.setMidLineWidth(3)

        p = Qt.QPalette()
        p.setColor(self.backgroundRole(), Qt.QColor(30, 30, 50))
        self.setPalette(p)
        # make curves and maps
        self.tuples = []
        # curve 1
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.QColor(150, 150, 200), 2))
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.XCross,
                                      Qt.QBrush(),
                                      Qt.QPen(Qt.Qt.yellow, 2),
                                      Qt.QSize(7, 7)))
        self.tuples.append((curve,
                            Qwt.QwtScaleMap(0, 100, -1.5, 1.5),
                            Qwt.QwtScaleMap(0, 100, 0.0, 2*np.pi)))
        # curve 2
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.QColor(200, 150, 50),
                                1,
                                Qt.Qt.DashDotDotLine))
        curve.setStyle(Qwt.QwtPlotCurve.Sticks)
        curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                      Qt.QBrush(Qt.Qt.blue),
                                      Qt.QPen(Qt.Qt.yellow),
                                      Qt.QSize(5, 5)))
        self.tuples.append((curve,
                            Qwt.QwtScaleMap(0, 100, 0.0, 2*np.pi),
                            Qwt.QwtScaleMap(0, 100, -3.0, 1.1)))
        # curve 3
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.QColor(100, 200, 150)))
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        self.tuples.append((curve,
                            Qwt.QwtScaleMap(0, 100, -1.1, 3.0),
                            Qwt.QwtScaleMap(0, 100, -1.1, 3.0)))
        # curve 4
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.Qt.red))
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        self.tuples.append((curve,
                            Qwt.QwtScaleMap(0, 100, -5.0, 1.1),
                            Qwt.QwtScaleMap(0, 100, -1.1, 5.0)))
        # data
        self.phase = 0.0
        self.base = np.arange(0.0, 2.01*np.pi, 2*np.pi/(USize-1))
        self.uval = np.cos(self.base)
        self.vval = np.sin(self.base)
        self.uval[1::2] *= 0.5
        self.vval[1::2] *= 0.5
        self.newValues()
        # start timer
        self.tid = self.startTimer(250)

    def paintEvent(self, event):
        Qt.QFrame.paintEvent(self,event)
        painter = Qt.QPainter(self)
        painter.setClipRect(self.contentsRect())
        self.drawContents(painter)

    def drawContents(self, painter):
        r = self.contentsRect()
        for curve, xMap, yMap in self.tuples:
            xMap.setPaintInterval(r.left(), r.right())
            yMap.setPaintInterval(r.top(), r.bottom())
            curve.draw(painter, xMap, yMap, r)

    def timerEvent(self, event):
        self.newValues()
        self.repaint()
        
    def newValues(self):
        phase = self.phase
        
        self.xval = np.arange(0, 2.01*np.pi, 2*np.pi/(Size-1))
        self.yval = np.sin(self.xval - phase)
        self.zval = np.cos(3*(self.xval + phase))
    
        s = 0.25 * np.sin(phase)
        c = np.sqrt(1.0 - s*s)
        u = self.uval
        self.uval = c*self.uval-s*self.vval
        self.vval = c*self.vval+s*u

        self.tuples[0][0].setData(self.yval, self.xval)
        self.tuples[1][0].setData(self.xval, self.zval)
        self.tuples[2][0].setData(self.yval, self.zval)
        self.tuples[3][0].setData(self.uval, self.vval)
        
        self.phase += 2*np.pi/100
        if self.phase>2*np.pi:
            self.phase = 0.0


def make():
    demo = CurveDemo()
    demo.resize(600, 600)
    demo.show()
    return demo


if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    demo = make()
    sys.exit(app.exec_())