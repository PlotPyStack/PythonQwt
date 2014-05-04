#!/usr/bin/env python

import sys
from PyQt4 import Qt
#import PyQt4.Qwt5 as Qwt
import qwt as Qwt

import numpy as np

class SimplePlot(Qwt.QwtPlot):
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)
    	  # make a QwtPlot widget
        self.setTitle('ReallySimpleDemo.py')
#        self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.RightLegend)
        # set axis titles
        self.setAxisTitle(Qwt.QwtPlot.xBottom, 'x')
        self.setAxisTitle(Qwt.QwtPlot.yLeft, 'y')
        # insert a few curves
        cSin = Qwt.QwtPlotCurve('y = sin(x)')
        cSin.setPen(Qt.QPen(Qt.Qt.red))
        cSin.attach(self)
        cCos = Qwt.QwtPlotCurve('y = cos(x)')
        cCos.setPen(Qt.QPen(Qt.Qt.blue))
        cCos.attach(self)
        # make a Numeric array for the horizontal data
        x = np.arange(0.0, 10.0, 0.1)
        # initialize the data
        cSin.setData(x, np.sin(x))
        cCos.setData(x, np.cos(x))
#        # insert a horizontal marker at y = 0
        mY = Qwt.QwtPlotMarker()
        mY.setLabel(Qwt.QwtText('y = 0'))
        mY.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mY.setLineStyle(Qwt.QwtPlotMarker.HLine)
        mY.setYValue(0.0)
        mY.attach(self)
#        # insert a vertical marker at x = 2 pi
        mX = Qwt.QwtPlotMarker()
        mX.setLabel(Qwt.QwtText('x = 2 pi'))
        mX.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mX.setLineStyle(Qwt.QwtPlotMarker.VLine)
        mX.setXValue(2*np.pi)
        mX.attach(self)
        # replot
        self.replot()

def make():
    demo = SimplePlot()
    demo.resize(500, 300)
    demo.show()
    return demo

def main(args):
    app = Qt.QApplication(args)
    demo = make()
#    print([demo.axisEnabled(axisId) for axisId in range(demo.axisCnt)])
#    print('titleRect: %r' % demo.plotLayout().titleRect())
#    print('canvasRect: %r' % demo.plotLayout().canvasRect())
    for axisId in range(demo.axisCnt):
#        print('scaleRect(%d): %r' % (axisId, demo.plotLayout().scaleRect(axisId)))
        sd = demo.axisScaleDiv(axisId)
#        print('scaleDiv(%d): %r' % (axisId, sd.ticks(sd.MediumTick)))
#        print('scaleDiv(%d): %r' % (axisId, sd.ticks(sd.MinorTick)))
#    canvas = demo.canvas()
#    print(canvas.testPaintAttribute(canvas.BackingStore))
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
