#!/usr/bin/env python

import sys
from PyQt4 import Qt
import qwt as Qwt
import numpy as np


def drange(start, stop, step):
    start, stop, step = float(start), float(stop), float(step)
    size = int(round((stop-start)/step))
    result = [start]*size
    for i in range(size):
        result[i] += i*step
    return result
        
def lorentzian(x):
    return 1.0/(1.0+(x-5.0)**2)


class MultiDemo(Qt.QWidget):
    def __init__(self, *args):
        Qt.QWidget.__init__(self, *args)
        layout = Qt.QGridLayout(self)        
        # try to create a plot for SciPy arrays

        # make a curve and copy the data
        numpy_curve = Qwt.QwtPlotCurve('y = lorentzian(x)')
        x = np.arange(0.0, 10.0, 0.01)
        y = lorentzian(x)
        numpy_curve.setData(x, y)
        # here, we know we can plot NumPy arrays
        numpy_plot = Qwt.QwtPlot(self)
        numpy_plot.setTitle('numpy array')
        numpy_plot.setCanvasBackground(Qt.Qt.white)
        numpy_plot.plotLayout().setCanvasMargin(0)
        numpy_plot.plotLayout().setAlignCanvasToScales(True)
        # insert a curve and make it red
        numpy_curve.attach(numpy_plot)
        numpy_curve.setPen(Qt.QPen(Qt.Qt.red))
        layout.addWidget(numpy_plot, 0, 0)
        numpy_plot.replot()

        # create a plot widget for lists of Python floats
        list_plot = Qwt.QwtPlot(self)
        list_plot.setTitle('Python list')
        list_plot.setCanvasBackground(Qt.Qt.white)
        list_plot.plotLayout().setCanvasMargin(0)
        list_plot.plotLayout().setAlignCanvasToScales(True)
        x = drange(0.0, 10.0, 0.01)
        y = [lorentzian(item) for item in x]
        # insert a curve, make it red and copy the lists
        list_curve = Qwt.QwtPlotCurve('y = lorentzian(x)')
        list_curve.attach(list_plot)
        list_curve.setPen(Qt.QPen(Qt.Qt.red))
        list_curve.setData(x, y)
        layout.addWidget(list_plot, 0, 1)
        list_plot.replot()


def make():
    demo = MultiDemo()
    demo.resize(400, 300)
    demo.show()
    return demo


if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    demo = make()
    sys.exit(app.exec_())
