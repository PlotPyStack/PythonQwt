#!/usr/bin/env python

# The Python version of qwt-*/examples/curvdemo2
# with a ConfigDialog contributed by Hans-Peter Jansen.


import sys
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

Size=15
USize=13

class ConfigDiag(Qt.QDialog):

    def __init__(self, parent = None):
        Qt.QDialog.__init__(self, parent)
        formLayout = Qt.QGridLayout()
        self.setLayout(formLayout)
        
        speedLayout = Qt.QHBoxLayout()
        speedLabel = Qt.QLabel("Timer [s]")
        speedLayout.addWidget(speedLabel)
        speedCounter = Qwt.QwtCounter()
        speedCounter.setRange(0.002, 1.0, 0.001)
        speedLayout.addWidget(speedCounter)
        formLayout.addLayout(speedLayout, 0, 0)
        self.s = speedLayout

        dismissButton = Qt.QPushButton("Dismiss")
        formLayout.addWidget(dismissButton, 1, 0)
        
        self.speedCounter = speedCounter
        self.connect(dismissButton,
                     Qt.SIGNAL("clicked()"),
                     self.accept)
        self.connect(self.speedCounter,
                     Qt.SIGNAL("valueChanged(double)"),
                     self.changeTimerSpeed)

    # __init__()
    
    def setTimerSpeed(self, t):
        self.speedCounter.setValue(t)

    # setTimerSpeed()

    def changeTimerSpeed(self, t):
        self.emit(Qt.SIGNAL("updateSpeed(double)"), t)

    # changeTimerSpeed()


class CurveDemo(Qt.QFrame):

    def __init__(self, *args):
        Qt.QFrame.__init__(self, *args)

        self.setWindowTitle("Click me to configure me")
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
        curve.setPen(
            Qt.QPen(Qt.QColor(150, 150, 200), 2))
        curve.setCurveType(Qwt.QwtPlotCurve.Xfy)
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        curveFitter = Qwt.QwtSplineCurveFitter()
        curveFitter.setSplineSize(150)
        curve.setCurveFitter(curveFitter)
        curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.XCross,
                                      Qt.QBrush(),
                                      Qt.QPen(Qt.Qt.yellow, 2),
                                      Qt.QSize(7, 7)))
        self.tuples.append((curve,
                            Qwt.QwtScaleMap(0, 100, -1.5, 1.5),
                            Qwt.QwtScaleMap(0, 100, 0.0, 2*pi)))
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
                            Qwt.QwtScaleMap(0, 100, 0.0, 2*pi),
                            Qwt.QwtScaleMap(0, 100, -3.0, 1.1)))
        # curve 3
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.QColor(100, 200, 150)))
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        curve.setCurveAttribute(Qwt.QwtPlotCurve.Fitted)
        curveFitter = Qwt.QwtSplineCurveFitter()
        curveFitter.setFitMode(Qwt.QwtSplineCurveFitter.ParametricSpline)
        curveFitter.setSplineSize(200)
        curve.setCurveFitter(curveFitter)
        self.tuples.append((curve,
                            Qwt.QwtScaleMap(0, 100, -1.1, 3.0),
                            Qwt.QwtScaleMap(0, 100, -1.1, 3.0)))
        # curve 4
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.Qt.red))
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        curve.setCurveAttribute(Qwt.QwtPlotCurve.Fitted)
        curveFitter = Qwt.QwtSplineCurveFitter()
        curveFitter.setSplineSize(200)
        curve.setCurveFitter(curveFitter)
        self.tuples.append((curve,
                            Qwt.QwtScaleMap(0, 100, -5.0, 1.1),
                            Qwt.QwtScaleMap(0, 100, -1.1, 5.0)))
        # data
        self.phase = 0.0
        self.base = arange(0.0, 2.01*pi, 2*pi/(USize-1))
        self.uval = cos(self.base)
        self.vval = sin(self.base)
        self.uval[1::2] *= 0.5
        self.vval[1::2] *= 0.5
        self.newValues()
        # timer config
        self.config = ConfigDiag()
        self.connect(self.config,
                     Qt.SIGNAL('updateSpeed(double)'),
                     self.setTimerSpeed)
         # start timer
        self.tid = None
        self.setTimerSpeed(0.02)
        self.config.setTimerSpeed(0.02)

    # __init__()

    def mousePressEvent(self, e):
        if not self.config.isVisible():
            self.config.show()
        else:
            self.config.hide()

    # mousePressEvent()

    def setTimerSpeed(self, seconds):
        if self.tid:
            self.killTimer(self.tid)
        self.tid = self.startTimer(int(seconds * 1000.0))

    # setTSpeed()

    def paintEvent(self, event):
        Qt.QFrame.paintEvent(self,event)
        painter = Qt.QPainter(self)
        #painter.setRenderHint(Qt.QPainter.Antialiasing)
        painter.setClipRect(self.contentsRect())
        self.drawContents(painter)

    # paintEvent()

    def drawContents(self, painter):
        r = self.contentsRect()
        for curve, xMap, yMap in self.tuples:
            xMap.setPaintInterval(r.left(), r.right())
            yMap.setPaintInterval(r.top(), r.bottom())
            curve.draw(painter, xMap, yMap, r)

    # drawContents()

    def timerEvent(self, event):
        self.newValues()
        self.repaint()

    # timerEvent()
    
    def newValues(self):
        phase = self.phase
        
        self.xval = arange(0, 2.01*pi, 2*pi/(Size-1))
        self.yval = sin(self.xval - phase)
        self.zval = cos(3*(self.xval + phase))
    
        s = 0.25 * sin(phase)
        c = sqrt(1.0 - s*s)
        u = self.uval
        self.uval = c*self.uval-s*self.vval
        self.vval = c*self.vval+s*u

        self.tuples[0][0].setData(self.yval, self.xval)
        self.tuples[1][0].setData(self.xval, self.zval)
        self.tuples[2][0].setData(self.yval, self.zval)
        self.tuples[3][0].setData(self.uval, self.vval)
        
        self.phase += 2*pi/100
        if self.phase>2*pi:
            self.phase = 0.0

    # newValues()

# class CurveDemo


def make():
    demo = CurveDemo()
    demo.resize(300, 300)
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
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
