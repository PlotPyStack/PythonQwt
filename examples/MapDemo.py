#!/usr/bin/env python


import random
import sys
import time
try:
    import resource
    has_resource = 1
except ImportError:
    has_resource = 0

from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *


def standard_map(x, y, kappa):
    """provide one interate of the inital conditions (x, y)
       for the standard map with parameter kappa.
    """
    y_new = y-kappa*sin(2.0*pi*x)
    x_new = x+y_new

    # bring back to [0,1.0]^2
    if( (x_new>1.0) or (x_new<0.0) ):
         x_new = x_new - floor(x_new)
    if( (y_new>1.0) or (y_new<0.0) ):
         y_new = y_new - floor(y_new)

    return x_new, y_new

# standard_map


class MapDemo(Qt.QMainWindow):

    def __init__(self, *args):
        Qt.QMainWindow.__init__(self, *args)

        self.plot = Qwt.QwtPlot(self)
        self.plot.setTitle("A Simple Map Demonstration")
        self.plot.setCanvasBackground(Qt.Qt.white)
        self.plot.setAxisTitle(Qwt.QwtPlot.xBottom, "x")
        self.plot.setAxisTitle(Qwt.QwtPlot.yLeft, "y")    
        self.plot.setAxisScale(Qwt.QwtPlot.xBottom, 0.0, 1.0)
        self.plot.setAxisScale(Qwt.QwtPlot.yLeft, 0.0, 1.0)
        self.setCentralWidget(self.plot)

        # Initialize map data
        self.count = self.i = 1000
        self.xs = zeros(self.count, Float)
        self.ys = zeros(self.count, Float)

        self.kappa = 0.2

        self.curve = Qwt.QwtPlotCurve("Map")
        self.curve.attach(self.plot)

        self.curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                           Qt.QBrush(Qt.Qt.red),
                                           Qt.QPen(Qt.Qt.blue),
                                           Qt.QSize(5, 5)))

        self.curve.setPen(Qt.QPen(Qt.Qt.cyan))

        toolBar = Qt.QToolBar(self)
        self.addToolBar(toolBar)

        toolBar.addWidget(Qt.QLabel("Count:", toolBar))
        sizeCounter = Qwt.QwtCounter(toolBar)
        toolBar.addWidget(sizeCounter)
        toolBar.addSeparator()
        sizeCounter.setRange(0, 1000000, 100)
        sizeCounter.setValue(self.count)
        sizeCounter.setNumButtons(3)
        self.connect(
            sizeCounter, Qt.SIGNAL('valueChanged(double)'), self.setCount)

        toolBar.addWidget(Qt.QLabel("Ticks (ms):", toolBar))
        tickCounter = Qwt.QwtCounter(toolBar)
        toolBar.addWidget(tickCounter)
        toolBar.addSeparator()
        # 1 tick = 1 ms, 10 ticks = 10 ms (Linux clock is 100 Hz)
        self.ticks = 10
        tickCounter.setRange(0, 1000, 1)
        tickCounter.setValue(self.ticks)
        tickCounter.setNumButtons(3)
        self.connect(
            tickCounter, Qt.SIGNAL('valueChanged(double)'), self.setTicks)
        self.tid = self.startTimer(self.ticks)

        self.timer_tic = None
        self.user_tic = None
        self.system_tic = None
        
        self.plot.replot()

    # __init__()
        
    def setCount(self, count):
        self.count = self.i = count
        self.xs = zeros(self.count, Float)
        self.ys = zeros(self.count, Float)
        self.i = self.count
        self.killTimer(self.tid)
        self.tid = self.startTimer(self.ticks)

    # setCount()

    def setTicks(self, ticks):
        self.i = self.count
        self.ticks = int(ticks)
        self.killTimer(self.tid)
        self.tid = self.startTimer(ticks)

    # setTicks()
        
    def resizeEvent(self, event):
        self.plot.resize(event.size())
        self.plot.move(0, 0)

    # resizeEvent()

    def moreData(self):
        if self.i == self.count:
            self.i = 0
            self.x = random.random()
            self.y = random.random()
            self.xs[self.i] = self.x
            self.ys[self.i] = self.y
            self.i += 1
            chunks = []
            if has_resource:
                self.user_toc, self.system_toc = resource.getrusage(
                    resource.RUSAGE_SELF)[:2]
                if self.user_tic:
                    chunks.append("user: %s s;"
                                  % (self.user_toc-self.user_tic))
                self.user_tic = self.user_toc
                if self.system_tic:
                    chunks.append("system: %s s;"
                                  % (self.system_toc-self.system_tic))
                self.system_tic = self.system_toc
            self.timer_toc = time.time()
            if self.timer_tic:
                chunks.append("wall: %s s." % (self.timer_toc-self.timer_tic))
                print(' '.join(chunks))
            self.timer_tic = self.timer_toc
        else:
            self.x, self.y = standard_map(self.x, self.y, self.kappa)
            self.xs[self.i] = self.x
            self.ys[self.i] = self.y
            self.i += 1

    # moreData()
        
    def timerEvent(self, e):
        self.moreData()
        self.curve.setData(self.xs[:self.i], self.ys[:self.i])
        self.plot.replot()

    # timerEvent()

# class MapDemo


def make():
    demo = MapDemo()
    demo.resize(600, 600)
    demo.show()
    return demo

# make()


def main(args):
    app = Qt.QApplication(args)
    demo = make()
    sys.exit(app.exec_())

# main()


# Admire! 
if __name__ == '__main__':
    if 'settracemask' in sys.argv:
        # for debugging, requires: python configure.py --trace ...
        import sip
        sip.settracemask(0x3f)

    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
