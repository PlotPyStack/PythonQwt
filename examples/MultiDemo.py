#!/usr/bin/env python

# Plot of scipy-, Numeric-, numarray-arrays and lists of Python floats.

import sys

from PyQt4 import Qt
#import PyQt4.Qwt5 as Qwt
import qwt as Qwt


def drange(start, stop, step):
    start, stop, step = float(start), float(stop), float(step)
    size = int(round((stop-start)/step))
    result = [start]*size
    for i in range(size):
        result[i] += i*step
    return result

# drange()
        
def lorentzian(x):
    return 1.0/(1.0+(x-5.0)**2)

# lorentzian()


class MultiDemo(Qt.QWidget):
    def __init__(self, *args):
        Qt.QWidget.__init__(self, *args)

        layout = Qt.QGridLayout(self)
        
        # try to create a plot for SciPy arrays
        try:
            # import does_not_exist
            import numpy
            # make a curve and copy the data
            numpy_curve = Qwt.QwtPlotCurve('y = lorentzian(x)')
            x = numpy.arange(0.0, 10.0, 0.01)
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
        except ImportError as message:
            print("%s: %s" % (ImportError, message))
            print("Install NumPy to plot plot NumPy arrays")
        except TypeError as message:
            print("%s: %s" % (TypeError, message))
            print("Rebuild PyQwt to plot NumPy arrays")

        # try to create a plot for Numeric arrays
        try:
            # import does_not_exist
            import Numeric
            # make a curve and copy the data
            numeric_curve = Qwt.QwtPlotCurve('y = lorentzian(x)')
            x = Numeric.arange(0.0, 10.0, 0.01)
            y = lorentzian(x)
            numeric_curve.setData(x, y)
            # here, we know we can plot Numeric arrays
            numeric_plot = Qwt.QwtPlot(self)
            numeric_plot.setTitle('Numeric array')
            numeric_plot.setCanvasBackground(Qt.Qt.white)
            numeric_plot.plotLayout().setCanvasMargin(0)
            numeric_plot.plotLayout().setAlignCanvasToScales(True)
            # insert a curve and make it red
            numeric_curve.attach(numeric_plot)
            numeric_curve.setPen(Qt.QPen(Qt.Qt.red))
            layout.addWidget(numeric_plot, 0, 1)
            numeric_plot.replot()
        except ImportError as message:
            print("%s: %s" % (ImportError, message))
            print("Install Numeric to plot Numeric arrays")
        except TypeError as message:
            print("%s: %s" % (TypeError, message))
            print("Rebuild PyQwt to plot Numeric arrays")

        # try to create a plot for numarray arrays
        try:
            # import does_not_exist
            import numarray
            # make a curve and copy the data
            numarray_curve = Qwt.QwtPlotCurve('y = lorentzian(x)')
            x = numarray.arange(0.0, 10.0, 0.01)
            y = lorentzian(x)
            numarray_curve.setData(x, y)
            # here, we know we can plot numarray arrays
            numarray_plot = Qwt.QwtPlot(self)
            numarray_plot.setTitle('numarray array')
            numarray_plot.setCanvasBackground(Qt.Qt.white)
            numarray_plot.plotLayout().setCanvasMargin(0)
            numarray_plot.plotLayout().setAlignCanvasToScales(True)
            # insert a curve and make it red
            numarray_curve.attach(numarray_plot)
            numarray_curve.setPen(Qt.QPen(Qt.Qt.red))
            layout.addWidget(numarray_plot, 1, 0)
            numarray_plot.replot()
        except ImportError as message:
            print("%s: %s" % (ImportError, message))
            print("Install numarray to plot numarray arrays")
        except TypeError as message:
            print("%s: %s" % (TypeError, message))
            print("Rebuild PyQwt to plot numarray arrays")            

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
        layout.addWidget(list_plot, 1, 1)
        list_plot.replot()

    # __init__()

# class MultiDemo


def main(args):
    app = Qt.QApplication(args)
    demo = make()
    sys.exit(app.exec_())

# main()


def make():
    demo = MultiDemo()
    demo.resize(400, 600)
    demo.show()
    return demo

# make()


# Admire!
if __name__ == '__main__':
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
