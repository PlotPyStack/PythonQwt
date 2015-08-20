#!/usr/bin/env python

import sys
from PyQt4 import Qt
import qwt as Qwt
import numpy as np


class CartesianAxis(Qwt.QwtPlotItem):
    """Supports a coordinate system similar to 
    http://en.wikipedia.org/wiki/Image:Cartesian-coordinate-system.svg"""
    def __init__(self, masterAxis, slaveAxis):
        """Valid input values for masterAxis and slaveAxis are QwtPlot.yLeft,
        QwtPlot.yRight, QwtPlot.xBottom, and QwtPlot.xTop. When masterAxis is
        an x-axis, slaveAxis must be an y-axis; and vice versa."""
        Qwt.QwtPlotItem.__init__(self)
        self.__axis = masterAxis
        if masterAxis in (Qwt.QwtPlot.yLeft, Qwt.QwtPlot.yRight):
            self.setAxes(slaveAxis, masterAxis)
        else:
            self.setAxes(masterAxis, slaveAxis)
        self.scaleDraw = Qwt.QwtScaleDraw()
        self.scaleDraw.setAlignment((Qwt.QwtScaleDraw.LeftScale,
                                     Qwt.QwtScaleDraw.RightScale,
                                     Qwt.QwtScaleDraw.BottomScale,
                                     Qwt.QwtScaleDraw.TopScale)[masterAxis])

    def draw(self, painter, xMap, yMap, rect):
        """Draw an axis on the plot canvas"""
        xtr = xMap.transform
        ytr = yMap.transform
        if self.__axis in (Qwt.QwtPlot.yLeft, Qwt.QwtPlot.yRight):
            self.scaleDraw.move(round(xtr(0.0)), yMap.p2())
            self.scaleDraw.setLength(yMap.p1()-yMap.p2())
        elif self.__axis in (Qwt.QwtPlot.xBottom, Qwt.QwtPlot.xTop):
            self.scaleDraw.move(xMap.p1(), round(ytr(0.0)))
            self.scaleDraw.setLength(xMap.p2()-xMap.p1())
        self.scaleDraw.setScaleDiv(self.plot().axisScaleDiv(self.__axis))
        self.scaleDraw.draw(painter, self.plot().palette())


class CartesianPlot(Qwt.QwtPlot):
    """Creates a coordinate system similar system 
    http://en.wikipedia.org/wiki/Image:Cartesian-coordinate-system.svg"""
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)
        self.setTitle('Cartesian Coordinate System Demo')
        # create a plot with a white canvas
        self.setCanvasBackground(Qt.Qt.white)
        # set plot layout
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        # attach a grid
        grid = Qwt.QwtPlotGrid()
        grid.attach(self)
        grid.setPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine))
        # attach a x-axis
        xaxis = CartesianAxis(Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yLeft)
        xaxis.attach(self)
        self.enableAxis(Qwt.QwtPlot.xBottom, False)
        # attach a y-axis
        yaxis = CartesianAxis(Qwt.QwtPlot.yLeft, Qwt.QwtPlot.xBottom)
        yaxis.attach(self)
        self.enableAxis(Qwt.QwtPlot.yLeft, False)
        # calculate 3 NumPy arrays
        x = np.arange(-2*np.pi, 2*np.pi, 0.01)
        y = np.pi*np.sin(x)
        z = 4*np.pi*np.cos(x)*np.cos(x)*np.sin(x)
        # attach a curve
        curve = Qwt.QwtPlotCurve('y = pi*sin(x)')
        curve.attach(self)
        curve.setPen(Qt.QPen(Qt.Qt.green, 2))
        curve.setData(x, y)
        # attach another curve
        curve = Qwt.QwtPlotCurve('y = 4*pi*sin(x)*cos(x)**2')
        curve.attach(self)
        curve.setPen(Qt.QPen(Qt.Qt.black, 2))
        curve.setData(x, z)
        self.replot()


def make():
    demo = CartesianPlot()
    demo.resize(400, 300)
    demo.show()
    return demo


if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    demo = make()
    sys.exit(app.exec_())
