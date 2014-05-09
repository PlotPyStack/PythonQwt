#!/usr/bin/env python

# The Python version of qwt-*/examples/curvedemo1/curvdemo1


import sys
from PyQt4 import Qt
#import PyQt4.Qwt5 as Qwt
import qwt as Qwt
from PyQt4.Qwt5.anynumpy import *


class CurveDemo(Qt.QFrame):

    def __init__(self, *args):
        Qt.QFrame.__init__(self, *args)

        self.xMap = Qwt.QwtScaleMap()
        self.xMap.setScaleInterval(-0.5, 10.5)
        self.yMap = Qwt.QwtScaleMap()
        self.yMap.setScaleInterval(-1.1, 1.1)

        # frame style
        self.setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Raised)
        self.setLineWidth(2)
        self.setMidLineWidth(3)

        # calculate values
        self.x = arange(0, 10.0, 10.0/27)
        self.y = sin(self.x)*cos(2*self.x)
        
        # make curves with different styles
        self.curves = []
        self.titles = []
#        # curve 0
#        self.titles.append('Style: Lines/Fitted, Symbol: Cross')
#        curve = Qwt.QwtPlotCurve()
#        curve.setPen(Qt.QPen(Qt.Qt.darkGreen))
#        curve.setStyle(Qwt.QwtPlotCurve.Lines)
#        curve.setCurveAttribute(Qwt.QwtPlotCurve.Fitted)
#        curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Cross,
#                                      Qt.QBrush(),
#                                      Qt.QPen(Qt.Qt.black),
#                                      Qt.QSize(5, 5)))
#        self.curves.append(curve)
        # curve 1
        self.titles.append('Style: Sticks, Symbol: Ellipse')
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.Qt.red))
        curve.setStyle(Qwt.QwtPlotCurve.Sticks)
        curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                      Qt.QBrush(Qt.Qt.yellow),
                                      Qt.QPen(Qt.Qt.blue),
                                      Qt.QSize(5, 5)))
        self.curves.append(curve)
        # curve 2
        self.titles.append('Style: Lines, Symbol: None')
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.Qt.darkBlue))
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        self.curves.append(curve)
        # curve 3
        self.titles.append('Style: Lines, Symbol: None, Antialiased')
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.Qt.darkBlue))
        curve.setStyle(Qwt.QwtPlotCurve.Lines)
        curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
        self.curves.append(curve)
        # curve 4
        self.titles.append('Style: Steps, Symbol: None')
        curve = Qwt.QwtPlotCurve()
        curve.setPen(Qt.QPen(Qt.Qt.darkCyan))
        curve.setStyle(Qwt.QwtPlotCurve.Steps)
        self.curves.append(curve)        
        # curve 5
        self.titles.append('Style: NoCurve, Symbol: XCross')
        curve = Qwt.QwtPlotCurve()
        curve.setStyle(Qwt.QwtPlotCurve.NoCurve)
        curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.XCross,
                                      Qt.QBrush(),
                                      Qt.QPen(Qt.Qt.darkMagenta),
                                      Qt.QSize(5, 5)))
        self.curves.append(curve)

        # attach data, using Numeric
        for curve in self.curves:
            curve.setData(self.x, self.y)

    # __init__()

    def shiftDown(self, rect, offset):
        rect.translate(0, offset)

    # shiftDown()

    def paintEvent(self, event):
        Qt.QFrame.paintEvent(self, event)
        painter = Qt.QPainter(self)
        painter.setClipRect(self.contentsRect())
        self.drawContents(painter)

    # paintEvent()

    def drawContents(self, painter):
        # draw curves
        r = self.contentsRect()
        dy = r.height()/len(self.curves)
        r.setHeight(dy)
        for curve in self.curves:
            self.xMap.setPaintInterval(r.left(), r.right())
            self.yMap.setPaintInterval(r.top(), r.bottom())
            engine = painter.device().paintEngine()
            if engine is not None and engine.hasFeature(Qt.QPaintEngine.Antialiasing):
                painter.setRenderHint(
                    Qt.QPainter.Antialiasing,
                    curve.testRenderHint(Qwt.QwtPlotItem.RenderAntialiased))
            curve.draw(painter, self.xMap, self.yMap, r)
            self.shiftDown(r, dy)
        # draw titles
        r = self.contentsRect()
        r.setHeight(dy)
        painter.setFont(Qt.QFont('Helvetica', 8))
        painter.setPen(Qt.Qt.black)
        for title in self.titles:
            painter.drawText(
                0, r.top(), r.width(), painter.fontMetrics().height(),
                Qt.Qt.AlignTop | Qt.Qt.AlignHCenter, title)
            self.shiftDown(r, dy)

    # drawContents()

# class CurveDemo


def make():
    demo = CurveDemo()
    demo.resize(300, 600)
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
