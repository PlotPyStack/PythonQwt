#!/usr/bin/env python

# The really simple Python version of Qwt-5.0.0/examples/simple


import sys
from PyQt4 import Qt
#import PyQt4.Qwt5 as Qwt
import qwt as Qwt
from PyQt4.Qwt5.anynumpy import *


class SimplePlot(Qwt.QwtPlot):

    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)

	  # make a QwtPlot widget
        self.setTitle('ReallySimpleDemo.py')
        self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.RightLegend)
        
        # set axis titles
        self.setAxisTitle(Qwt.QwtPlot.xBottom, 'x -->')
        self.setAxisTitle(Qwt.QwtPlot.yLeft, 'y -->')
        self.enableAxis(self.xTop)
        self.enableAxis(self.yRight)

        # insert a few curves
        cSin = Qwt.QwtPlotCurve('y = sin(x)')
        cSin.setPen(Qt.QPen(Qt.Qt.red))
        cSin.attach(self)

        cCos = Qwt.QwtPlotCurve('y = cos(x)')
        cCos.setPen(Qt.QPen(Qt.Qt.blue))
        cCos.attach(self)
        
        # make a Numeric array for the horizontal data
        x = arange(0.0, 10.0, 0.1)

        # initialize the data
        cSin.setData(x, sin(x))
        cCos.setData(x, cos(x))

        # insert a horizontal marker at y = 0
        mY = Qwt.QwtPlotMarker()
        mY.setLabel(Qwt.QwtText('y = 0'))
        mY.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mY.setLineStyle(Qwt.QwtPlotMarker.HLine)
        mY.setYValue(0.0)
        mY.attach(self)

        # insert a vertical marker at x = 2 pi
        mX = Qwt.QwtPlotMarker()
        mX.setLabel(Qwt.QwtText('x = 2 pi'))
        mX.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mX.setLineStyle(Qwt.QwtPlotMarker.VLine)
        mX.setXValue(2*pi)
        mX.attach(self)

        # replot
        self.replot()

    # __init__()

# class Plot


def make():
    demo = SimplePlot()
    demo.resize(500, 300)
    demo.show()
    return demo

# make()


def main(args):
    app = Qt.QApplication(args)
    demo = make()
    sys.exit(app.exec_())

# main()


# Admire
if __name__ == '__main__':
    if 'settracemask' in sys.argv:
        # for debugging, requires: python configure.py --trace ...
        import sip
        sip.settracemask(0x3f)

    main(sys.argv)
        

# Local Variables: ***
# mode: python ***
# End: ***



