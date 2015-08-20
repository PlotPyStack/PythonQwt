#!/usr/bin/env python

import sys
import numpy as np
import qwt
from PyQt4 import Qt


class SimplePlot(qwt.QwtPlot):
    def __init__(self, *args):
        qwt.QwtPlot.__init__(self, *args)
        self.setTitle('ReallySimpleDemo.py')
        self.insertLegend(qwt.QwtLegend(), qwt.QwtPlot.RightLegend)
        self.setAxisTitle(qwt.QwtPlot.xBottom, 'x -->')
        self.setAxisTitle(qwt.QwtPlot.yLeft, 'y -->')
        self.enableAxis(self.xBottom)

        # insert a few curves
        cSin = qwt.QwtPlotCurve('y = sin(x)')
        cSin.setPen(Qt.QPen(Qt.Qt.red))
        cSin.attach(self)
        cCos = qwt.QwtPlotCurve('y = cos(x)')
        cCos.setPen(Qt.QPen(Qt.Qt.blue))
        cCos.attach(self)
        
        # make a Numeric array for the horizontal data
        x = np.arange(0.0, 10.0, 0.1)

        # initialize the data
        cSin.setData(x, np.sin(x))
        cCos.setData(x, np.cos(x))

        # insert a horizontal marker at y = 0
        mY = qwt.QwtPlotMarker()
        mY.setLabel(qwt.QwtText('y = 0'))
        mY.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mY.setLineStyle(qwt.QwtPlotMarker.HLine)
        mY.setYValue(0.0)
        mY.attach(self)

        # insert a vertical marker at x = 2 pi
        mX = qwt.QwtPlotMarker()
        mX.setLabel(qwt.QwtText('x = 2 pi'))
        mX.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mX.setLineStyle(qwt.QwtPlotMarker.VLine)
        mX.setXValue(2*np.pi)
        mX.attach(self)

        # replot
        self.replot()


def make():
    demo = SimplePlot()
    demo.resize(800, 500)
    demo.show()
    return demo


if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    demo = make()
    demo.exportTo("demo.png", size=(1600, 900), resolution=200)
    sys.exit(app.exec_())
