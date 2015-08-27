#!/usr/bin/env python

import random
import sys

from qwt.qt.QtGui import QApplication, QPen, QColor
from qwt.qt.QtCore import QRect
from qwt.qt.QtCore import Qt
from qwt import (QwtPlot, QwtIntervalSample, QwtInterval, QwtPlotGrid,
                 QwtPlotItem, QwtPainter, QwtIntervalSeriesData)


class HistogramItem(QwtPlotItem):
    Auto = 0
    Xfy = 1
    def __init__(self, *args):
        QwtPlotItem.__init__(self, *args)
        self.__attributes = HistogramItem.Auto
        self.__data = QwtIntervalSeriesData()
        self.__color = QColor()
        self.__reference = 0.0
        self.setItemAttribute(QwtPlotItem.AutoScale, True)
        self.setItemAttribute(QwtPlotItem.Legend, True)
        self.setZ(20.0)

    def setData(self, data):
        self.__data = data
        self.itemChanged()

    def data(self):
        return self.__data

    def setColor(self, color):
        if self.__color != color:
            self.__color = color
            self.itemChanged()

    def color(self):
        return self.__color

    def boundingRect(self):
        result = self.__data.boundingRect()
        if not result.isValid():
            return result
        if self.testHistogramAttribute(HistogramItem.Xfy):
            result = QwtDoubleRect(result.y(), result.x(),
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

    def rtti(self):
        return QwtPlotItem.PlotHistogram

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
                    painter, Qt.Horizontal, QRect(x0, y1, x2-x0, y2-y1))
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
                    painter, Qt.Vertical, QRect(x1, y0, x2-x1, y2-y0))

    def setBaseline(self, reference):
        if self.baseline() != reference:
            self.__reference = reference
            self.itemChanged()
    
    def baseline(self,):
        return self.__reference

    def setHistogramAttribute(self, attribute, on = True):
        if self.testHistogramAttribute(attribute):
            return

        if on:
            self.__attributes |= attribute
        else:
            self.__attributes &= ~attribute

        self.itemChanged()

    def testHistogramAttribute(self, attribute):
        return bool(self.__attributes & attribute) 

    def drawBar(self, painter, orientation, rect):
        painter.save()
        color = painter.pen().color()
        r = rect.normalized()
        factor = 125;
        light = color.lighter(factor)
        dark = color.darker(factor)

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        QwtPainter.drawRect(painter, r.x()+1, r.y()+1,
                                r.width()-2, r.height()-2)

        painter.setBrush(Qt.NoBrush)

        painter.setPen(QPen(light, 2))
        QwtPainter.drawLine(
            painter, r.left()+1, r.top()+2, r.right()+1, r.top()+2)

        painter.setPen(QPen(dark, 2))
        QwtPainter.drawLine(
            painter, r.left()+1, r.bottom(), r.right()+1, r.bottom())

        painter.setPen(QPen(light, 1))
        QwtPainter.drawLine(
            painter, r.left(), r.top() + 1, r.left(), r.bottom())
        QwtPainter.drawLine(
            painter, r.left()+1, r.top()+2, r.left()+1, r.bottom()-1)

        painter.setPen(QPen(dark, 1))
        QwtPainter.drawLine(
            painter, r.right()+1, r.top()+1, r.right()+1, r.bottom())
        QwtPainter.drawLine(
            painter, r.right(), r.top()+2, r.right(), r.bottom()-1)

        painter.restore()


def make():
    demo = QwtPlot()
    demo.setCanvasBackground(Qt.white)
    demo.setTitle("Histogram")

    grid = QwtPlotGrid()
    grid.enableXMin(True)
    grid.enableYMin(True)
    grid.setMajorPen(QPen(Qt.black, 0, Qt.DotLine));
    grid.setMinorPen(QPen(Qt.gray, 0 , Qt.DotLine));
    grid.attach(demo)

    histogram = HistogramItem()
    histogram.setColor(Qt.darkCyan)

    numValues = 20
    samples = []
    pos = 0.0
    for i in range(numValues):
        width = 5 + random.randint(0, 4)
        value = random.randint(0, 99)
        samples.append(QwtIntervalSample(value, QwtInterval(pos, pos+width)));
        pos += width

    histogram.setData(QwtIntervalSeriesData(samples))
    histogram.attach(demo)
    demo.setAxisScale(QwtPlot.yLeft, 0.0, 100.0)
    demo.setAxisScale(QwtPlot.xBottom, 0.0, pos)
    demo.replot()
    demo.resize(600, 400)
    demo.show()
    return demo


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = make()
    sys.exit(app.exec_())
