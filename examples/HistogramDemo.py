#!/usr/bin/env python

# The Python version of qwt-5.0/examples/histogram

import random
import sys
from PyQt4 import Qt
#import PyQt4.Qwt5 as Qwt
import qwt as Qwt


class HistogramItem(Qwt.QwtPlotItem):

    Auto = 0
    Xfy = 1
    
    def __init__(self, *args):
        Qwt.QwtPlotItem.__init__(self, *args)
        self.__attributes = HistogramItem.Auto
        self.__data = Qwt.QwtIntervalSeriesData()
        self.__color = Qt.QColor()
        self.__reference = 0.0
        self.setItemAttribute(Qwt.QwtPlotItem.AutoScale, True)
        self.setItemAttribute(Qwt.QwtPlotItem.Legend, True)
        self.setZ(20.0)

    # __init__()

    def setData(self, data):
        self.__data = data
        self.itemChanged()

    # setData()

    def data(self):
        return self.__data

    # data()

    def setColor(self, color):
        if self.__color != color:
            self.__color = color
            self.itemChanged()

    # setColor()

    def color(self):
        return self.__color

    # color()

    def boundingRect(self):
        result = self.__data.boundingRect()
        if not result.isValid():
            return result
        if self.testHistogramAttribute(HistogramItem.Xfy):
            result = Qwt.QwtDoubleRect(result.y(), result.x(),
                                       result.height(), result.width())
            if result.left() > self.baseline():
                result.setLeft(self.baseline())
            elif result.right() < self.baseline():
                result.setRight(self.baseline())
        else:
            if result.bottom() < self.baseline():
                result.setBottom(self.baseline())
            elif result.top() > self.baseline():
                result.setTop(self.baseline())
        return result

    # boundingRect()

    def rtti(self):
        return Qwt.QwtPlotItem.PlotHistogram

    # rtti()

    def draw(self, painter, xMap, yMap, rect):
        iData = self.data()
        painter.setPen(self.color())
        x0 = xMap.transform(self.baseline())
        y0 = yMap.transform(self.baseline())
        for i in range(iData.size()):
            if self.testHistogramAttribute(HistogramItem.Xfy):
                x2 = xMap.transform(iData.sample(i).value)
                if x2 == x0:
                    continue

                y1 = yMap.transform(iData.sample(i).interval.minValue())
                y2 = yMap.transform(iData.sample(i).interval.maxValue())

                if y1 > y2:
                    y1, y2 = y2, y1
                    
                if  i < iData.size()-2:
                    yy1 = yMap.transform(iData.sample(i+1).interval.minValue())
                    yy2 = yMap.transform(iData.sample(i+1).interval.maxValue())

                    if y2 == min(yy1, yy2):
                        xx2 = xMap.transform(iData.sample(i+1).interval.minValue())
                        if xx2 != x0 and ((xx2 < x0 and x2 < x0)
                                          or (xx2 > x0 and x2 > x0)):
                            # One pixel distance between neighboured bars
                            y2 += 1

                self.drawBar(
                    painter, Qt.Qt.Horizontal, Qt.QRect(x0, y1, x2-x0, y2-y1))
            else:
                y2 = yMap.transform(iData.sample(i).value)
                if y2 == y0:
                    continue

                x1 = xMap.transform(iData.sample(i).interval.minValue())
                x2 = xMap.transform(iData.sample(i).interval.maxValue())

                if x1 > x2:
                    x1, x2 = x2, x1

                if i < iData.size()-2:
                    xx1 = xMap.transform(iData.sample(i+1).interval.minValue())
                    xx2 = xMap.transform(iData.sample(i+1).interval.maxValue())
                    x2 = min(xx1, xx2)
                    yy2 = yMap.transform(iData.sample(i+1).value)
                    if x2 == min(xx1, xx2):
                        if yy2 != 0 and (( yy2 < y0 and y2 < y0)
                                         or (yy2 > y0 and y2 > y0)):
                            # One pixel distance between neighboured bars
                            x2 -= 1
                
                self.drawBar(
                    painter, Qt.Qt.Vertical, Qt.QRect(x1, y0, x2-x1, y2-y0))

    # draw()

    def setBaseline(self, reference):
        if self.baseline() != reference:
            self.__reference = reference
            self.itemChanged()

    # setBaseLine()
    
    def baseline(self,):
        return self.__reference

    # baseline()

    def setHistogramAttribute(self, attribute, on = True):
        if self.testHistogramAttribute(attribute):
            return

        if on:
            self.__attributes |= attribute
        else:
            self.__attributes &= ~attribute

        self.itemChanged()
    
    # setHistogramAttribute()

    def testHistogramAttribute(self, attribute):
        return bool(self.__attributes & attribute) 

    # testHistogramAttribute()

    def drawBar(self, painter, orientation, rect):
        painter.save()
        color = painter.pen().color()
        r = rect.normalized()
        factor = 125;
        light = color.light(factor)
        dark = color.dark(factor)

        painter.setBrush(color)
        painter.setPen(Qt.Qt.NoPen)
        Qwt.QwtPainter.drawRect(painter, r.x()+1, r.y()+1,
                                r.width()-2, r.height()-2)

        painter.setBrush(Qt.Qt.NoBrush)

        painter.setPen(Qt.QPen(light, 2))
        Qwt.QwtPainter.drawLine(
            painter, r.left()+1, r.top()+2, r.right()+1, r.top()+2)

        painter.setPen(Qt.QPen(dark, 2))
        Qwt.QwtPainter.drawLine(
            painter, r.left()+1, r.bottom(), r.right()+1, r.bottom())

        painter.setPen(Qt.QPen(light, 1))
        Qwt.QwtPainter.drawLine(
            painter, r.left(), r.top() + 1, r.left(), r.bottom())
        Qwt.QwtPainter.drawLine(
            painter, r.left()+1, r.top()+2, r.left()+1, r.bottom()-1)

        painter.setPen(Qt.QPen(dark, 1))
        Qwt.QwtPainter.drawLine(
            painter, r.right()+1, r.top()+1, r.right()+1, r.bottom())
        Qwt.QwtPainter.drawLine(
            painter, r.right(), r.top()+2, r.right(), r.bottom()-1)

        painter.restore()

    # drawBar()

# class HistogramItem


def make():
    demo = Qwt.QwtPlot()
    demo.setCanvasBackground(Qt.Qt.white)
    demo.setTitle("Histogram")

    grid = Qwt.QwtPlotGrid()
    grid.enableXMin(True)
    grid.enableYMin(True)
    grid.setMajorPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine));
    grid.setMinorPen(Qt.QPen(Qt.Qt.gray, 0 , Qt.Qt.DotLine));
     
    grid.attach(demo)

    histogram = HistogramItem()
    histogram.setColor(Qt.Qt.darkCyan)

    numValues = 20
    samples = []

    pos = 0.0
    for i in range(numValues):
        width = 5 + random.randint(0, 4)
        value = random.randint(0, 99)
        samples.append(Qwt.QwtIntervalSample(value, Qwt.QwtInterval(pos, pos+width)));
        pos += width

    histogram.setData(Qwt.QwtIntervalSeriesData(samples))
    histogram.attach(demo)

    demo.setAxisScale(Qwt.QwtPlot.yLeft, 0.0, 100.0)
    demo.setAxisScale(Qwt.QwtPlot.xBottom, 0.0, pos)
    demo.replot()
    
    demo.resize(600, 400)
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

