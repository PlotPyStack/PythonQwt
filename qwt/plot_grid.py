# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see qwt/LICENSE for details)

from qwt.scale_div import QwtScaleDiv
from qwt.plot import QwtPlotItem
from qwt.text import QwtText
from qwt.painter import QwtPainter
from qwt.math import qwtFuzzyGreaterOrEqual, qwtFuzzyLessOrEqual

from qwt.qt.QtGui import QPen
from qwt.qt.QtCore import Qt


class QwtPlotGrid_PrivateData(object):
    def __init__(self):
        self.xEnabled = True
        self.yEnabled = True
        self.xMinEnabled = False
        self.yMinEnabled = False
        self.xScaleDiv = QwtScaleDiv()
        self.yScaleDiv = QwtScaleDiv()
        self.majorPen = QPen()
        self.minorPen = QPen()


class QwtPlotGrid(QwtPlotItem):
    def __init__(self):
        QwtPlotItem.__init__(self, QwtText("Grid"))
        self.__data = QwtPlotGrid_PrivateData()
        self.setItemInterest(QwtPlotItem.ScaleInterest, True)
        self.setZ(10.)
        
    def rtti(self):
        return QwtPlotItem.Rtti_PlotGrid
    
    def enableX(self, on):
        if self.__data.xEnabled != on:
            self.__data.xEnabled = on
            self.legendChanged()
            self.itemChanged()
    
    def enableY(self, on):
        if self.__data.yEnabled != on:
            self.__data.yEnabled = on
            self.legendChanged()
            self.itemChanged()
    
    def enableXMin(self, on):
        if self.__data.xMinEnabled != on:
            self.__data.xMinEnabled = on
            self.legendChanged()
            self.itemChanged()
    
    def enableYMin(self, on):
        if self.__data.yMinEnabled != on:
            self.__data.yMinEnabled = on
            self.legendChanged()
            self.itemChanged()

    def setXDiv(self, scaleDiv):
        if self.__data.xScaleDiv != scaleDiv:
            self.__data.xScaleDiv = scaleDiv
            self.itemChanged()

    def setYDiv(self, scaleDiv):
        if self.__data.yScaleDiv != scaleDiv:
            self.__data.yScaleDiv = scaleDiv
            self.itemChanged()

    def setPen(self, *args):
        if len(args) == 3:
            color, width, style = args
            self.setPen(QPen(color, width, style))
        elif len(args) == 1:
            pen, = args
            if self.__data.majorPen != pen or self.__data.minorPen != pen:
                self.__data.majorPen = pen
                self.__data.minorPen = pen
                self.legendChanged()
                self.itemChanged()
        else:
            raise TypeError("%s().setPen() takes 1 or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))

    def setMajorPen(self, *args):
        if len(args) == 3:
            color, width, style = args
            self.setMajorPen(QPen(color, width, style))
        elif len(args) == 1:
            pen, = args
            if self.__data.majorPen != pen:
                self.__data.majorPen = pen
                self.legendChanged()
                self.itemChanged()
        else:
            raise TypeError("%s().setMajorPen() takes 1 or 3 argument(s) (%s "\
                            "given)" % (self.__class__.__name__, len(args)))

    def setMinorPen(self, *args):
        if len(args) == 3:
            color, width, style = args
            self.setMinorPen(QPen(color, width, style))
        elif len(args) == 1:
            pen, = args
            if self.__data.minorPen != pen:
                self.__data.minorPen = pen
                self.legendChanged()
                self.itemChanged()
        else:
            raise TypeError("%s().setMinorPen() takes 1 or 3 argument(s) (%s "\
                            "given)" % (self.__class__.__name__, len(args)))
    
    def draw(self, painter, xMap, yMap, canvasRect):
        minorPen = QPen(self.__data.minorPen)
        minorPen.setCapStyle(Qt.FlatCap)
        painter.setPen(minorPen)
        if self.__data.xEnabled and self.__data.xMinEnabled:
            self.drawLines(painter, canvasRect, Qt.Vertical, xMap,
                           self.__data.xScaleDiv.ticks(QwtScaleDiv.MinorTick))
            self.drawLines(painter, canvasRect, Qt.Vertical, xMap,
                           self.__data.xScaleDiv.ticks(QwtScaleDiv.MediumTick))
        if self.__data.yEnabled and self.__data.yMinEnabled:
            self.drawLines(painter, canvasRect, Qt.Horizontal, yMap,
                           self.__data.yScaleDiv.ticks(QwtScaleDiv.MinorTick))
            self.drawLines(painter, canvasRect, Qt.Horizontal, yMap,
                           self.__data.yScaleDiv.ticks(QwtScaleDiv.MediumTick))
        majorPen = QPen(self.__data.majorPen)
        majorPen.setCapStyle(Qt.FlatCap)
        painter.setPen(majorPen)
        if self.__data.xEnabled:
            self.drawLines(painter, canvasRect, Qt.Vertical, xMap,
                           self.__data.xScaleDiv.ticks(QwtScaleDiv.MajorTick))
        if self.__data.yEnabled:
            self.drawLines(painter, canvasRect, Qt.Horizontal, yMap,
                           self.__data.yScaleDiv.ticks(QwtScaleDiv.MajorTick))
        
    def drawLines(self, painter, canvasRect, orientation, scaleMap, values):
        x1 = canvasRect.left()
        x2 = canvasRect.right()-1.
        y1 = canvasRect.top()
        y2 = canvasRect.bottom()-1.
        doAlign = QwtPainter.roundingAlignment(painter)
        for val in values:
            value = scaleMap.transform(val)
            if doAlign:
                value = round(value)
            if orientation == Qt.Horizontal:
                if qwtFuzzyGreaterOrEqual(value, y1) and\
                   qwtFuzzyLessOrEqual(value, y2):
                    QwtPainter.drawLine(painter, x1, value, x2, value)
            else:
                if qwtFuzzyGreaterOrEqual(value, x1) and\
                   qwtFuzzyLessOrEqual(value, x2):
                    QwtPainter.drawLine(painter, value, y1, value, y2)
    
    def majorPen(self):
        return self.__data.majorPen
    
    def minorPen(self):
        return self.__data.minorPen
    
    def xEnabled(self):
        return self.__data.xEnabled
    
    def yEnabled(self):
        return self.__data.yEnabled
    
    def xMinEnabled(self):
        return self.__data.xMinEnabled
    
    def yMinEnabled(self):
        return self.__data.yMinEnabled
    
    def xScaleDiv(self):
        return self.__data.xScaleDiv
    
    def yScaleDiv(self):
        return self.__data.yScaleDiv
    
    def updateScaleDiv(self, xScaleDiv, yScaleDiv):
        self.setXDiv(xScaleDiv)
        self.setYDiv(yScaleDiv)
        