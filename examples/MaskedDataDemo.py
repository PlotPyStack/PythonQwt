#!/usr/bin/env python

import sys
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt

try:
    import numpy as np
except ImportError:
    if not Qt.QCoreApplication.instance():
        a = Qt.QApplication([])
    Qt.QMessageBox.critical(
        None,
        'NumPy required',
        'This example requires NumPy, but failed to import NumPy.\n'
        'NumPy is available at http://sourceforge.net/projects/numpy'
        )
    raise SystemExit(
        'Failed to import NumPy.\n'
        'NumPy is available at http://sourceforge.net/projects/numpy'
        )


class MaskedData(Qwt.QwtArrayData):

    def __init__(self, x, y, mask):
        Qwt.QwtArrayData.__init__(self, x, y)
        self.__mask = np.asarray(mask, bool)
        # keep a copy of x and y for boundingRect()
        self.__x = np.asarray(x)
        self.__y = np.asarray(y)

    # __init__()

    def copy(self):
        return self

    # copy()

    def mask(self):
        return self.__mask

    # mask()

    def boundingRect(self):
        """Return the bounding rectangle of the data, accounting for the mask.
        """
        xmax = self.__x[self.__mask].max()
        xmin = self.__x[self.__mask].min()
        ymax = self.__y[self.__mask].max()
        ymin = self.__y[self.__mask].min()

        return Qt.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

    # boundingRect()

# class MaskedData


class MaskedCurve(Qwt.QwtPlotCurve):

    def __init__(self, x, y, mask):
        Qwt.QwtPlotCurve.__init__(self)
        self.setData(MaskedData(x, y, mask))

    # __init__()

    def draw(self, painter, xMap, yMap, rect):
        # When the array indices contains the indices of all valid data points,
        # a chunks of valid data is indexed by
        # indices[first], indices[first+1], .., indices[last].
        # The first index of a chunk of valid data is calculated by:
        # 1. indices[i] - indices[i-1] > 1
        # 2. indices[0] is always OK
        # The last index of a chunk of valid data is calculated by:
        # 1. index[i] - index[i+1] < -1
        # 2. index[-1] is always OK
        indices = np.arange(self.data().size())[self.data().mask()]
        fs = np.array(indices)
        fs[1:] -= indices[:-1]
        fs[0] = 2
        fs = indices[fs > 1]
        ls = np.array(indices)
        ls[:-1] -= indices[1:]
        ls[-1] = -2
        ls = indices[ls < -1]
        for first, last in zip(fs, ls):
            Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)

# class MaskedCurve


def make():
    demo = Qwt.QwtPlot()
    demo.setTitle('Masked Data Demo')
    demo.setCanvasBackground(Qt.Qt.white)
    # num = 501 causes a divide by zero warning 64-bit Gentoo
    x = np.linspace(-2*np.pi, 2*np.pi, num=501)
    y = 1/np.sin(x)
    mask = np.logical_and(y>-3.0, y<3.0)
    curve = MaskedCurve(x, y, mask)
    curve.attach(demo)
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
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***

