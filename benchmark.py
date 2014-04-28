#!/usr/bin/env python

import sys
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt

import numpy as np
import time

N = 5000000

class PythonQwtPlotCurve(Qwt.QwtPlotCurve):
    def drawCurve(self, painter, style, xMap, yMap, from_, to):
        t0 = time.time()
        
        if from_ > to:
            return
        
        size = to - from_ + 1

        x_cnv = xMap.pDist()/xMap.sDist()
        px = (self.xdata-xMap.s1())*x_cnv + xMap.p1()
        y_cnv = yMap.pDist()/yMap.sDist()
        py = -(self.ydata-yMap.s1())*y_cnv + yMap.p1()

        polygon = Qt.QPolygonF(size)
        pointer = polygon.data()
#        pointer.setsize(2*size*self.xdata.itemsize)
        pointer.setsize(2*size*np.finfo(np.float).dtype.itemsize)
        memory = np.frombuffer(pointer, np.float)
        memory[0::2] = px
        memory[1::2] = py
        painter.drawPolyline(polygon)

        print('Elapsed time (Python): %d ms' % ((time.time()-t0)*1e3))
        print('')

class OriginalQwtPlotCurve(Qwt.QwtPlotCurve):
    def drawCurve(self, painter, style, xMap, yMap, i_from, i_to):
        t0 = time.time()
        super(OriginalQwtPlotCurve, self).drawCurve(painter, style,
                                                    xMap, yMap, i_from, i_to)
        print('Elapsed time (PyQwt ): %d ms' % ((time.time()-t0)*1e3))


class SimplePlot(Qwt.QwtPlot):
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)
        cSin = OriginalQwtPlotCurve('y = sin(x)')
        cSin.attach(self)
        cCos = PythonQwtPlotCurve('y = sin(x)')
        cCos.attach(self)
        x = np.linspace(0., 100., N)
        cSin.setData(x, np.sin(x))
        y = np.cos(x)
        cCos.setData(x, y)
        cCos.xdata = x
        cCos.ydata = y
        self.replot()

if __name__ == '__main__':
    app = Qt.QApplication([])
    demo = SimplePlot()
    demo.resize(500, 300)
    demo.show()
    sys.exit(app.exec_())
