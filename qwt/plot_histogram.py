# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see qwt/LICENSE for details)

from qwt.plot_seriesitem import QwtPlotSeriesItem
from qwt.series_store import QwtSeriesStore
from qwt.interval import QwtInterval
from qwt.series_data import QwtIntervalSeriesData
from qwt.plot import QwtPlotItem
from qwt.painter import QwtPainter
from qwt.sample import QwtIntervalSample
from qwt.column_symbol import QwtColumnRect, QwtColumnSymbol

from qwt.qt.QtGui import QPen, QBrush, QColor, QPolygonF
from qwt.qt.QtCore import Qt, QPointF, QRectF


def qwtIsCombinable(d1, d2):
    if d1.isValid() and d2.isValid():
        if d1.maxValue() == d2.minValue():
            if not d1.borderFlags() & QwtInterval.ExcludeMaximum\
               and d2.borderFlags() & QwtInterval.ExcludeMinimum:
                return True
    return False


class QwtPlotHistogram_PrivateData(object):
    def __init__(self):
        self.baseline = 0.
        self.style = 0
        self.symbol = None
        self.pen = QPen()
        self.brush = QBrush()


class QwtPlotHistogram(QwtPlotSeriesItem, QwtSeriesStore):
    
    # enum HistogramStyle
    Outline, Columns, Lines = list(range(3))
    UserStyle = 100
    
    def __init__(self, title=None):
        self.__data = None
        self.init()
    
    def init(self):
        self.__data = QwtPlotHistogram_PrivateData()
        self.setData(QwtIntervalSeriesData())
        self.setItemAttribute(QwtPlotItem.AutoScale, True)
        self.setItemAttribute(QwtPlotItem.Legend, True)
        self.setZ(20.)
    
    def setStyle(self, style):
        if style != self.__data.style:
            self.__data.style = style
            self.legendChanged()
            self.itemChanged()
            
    def style(self):
        return self.__data.style
    
    def setPen(self, *args):
        if len(args) not in (1, 2, 3):
            raise TypeError
        if isinstance(args[0], QColor):
            color = args[0]
            width = 0.
            style = Qt.PenStyle
            if len(args) > 1:
                width = args[1]
            if len(args) > 2:
                style = args[2]
            self.setPen(QPen(color, width, style))
        else:
            pen, = args
            if pen != self.__data.pen:
                self.__data.pen = pen
                self.legendChanged()
                self.itemChanged()
    
    def pen(self):
        return self.__data.pen

    def setBrush(self, brush):
        if brush != self.__data.brush:
            self.__data.brush = brush
            self.legendChanged()
            self.itemChanged()
    
    def brush(self):
        return self.__data.brush

    def setSymbol(self, symbol):
        if symbol != self.__data.symbol:
            self.__data.symbol = symbol
            self.legendChanged()
            self.itemChanged()
    
    def symbol(self):
        return self.__data.symbol

    def setBaseline(self, value):
        if value != self.__data.baseline:
            self.__data.baseline = value
            self.itemChanged()
    
    def baseline(self):
        return self.__data.baseline

    def boundingRect(self):
        rect = QRectF(self.data().boundingRect())
        if not rect.isValid():
            return rect
        if self.orientation() == Qt.Horizontal:
            rect = QRectF(rect.y(), rect.x(), rect.height(), rect.width())
            if rect.left() > self.__data.baseline:
                rect.setLeft(self.__data.baseline)
            elif rect.right() < self.__data.baseline:
                rect.setRight(self.__data.baseline)
        else:
            if rect.bottom() < self.__data.baseline:
                rect.setBottom(self.__data.baseline)
            elif rect.top() > self.__data.baseline:
                rect.setTop(self.__data.baseline)
        return rect
    
    def rtti(self):
        return QwtPlotItem.Rtti_PlotHistogram
    
    def setSamples(self, samples):
        if not isinstance(samples, QwtIntervalSeriesData):
            self.setData(QwtIntervalSeriesData(samples))
        else:
            self.setData(samples)
    
    def drawSeries(self, painter, xMap, yMap, canvasRect, from_, to):
        if not painter or self.dataSize() <= 0:
            return
        if to < 0:
            to = self.dataSize()-1
        if self.__data.style == self.Outline:
            self.drawOutline(painter, xMap, yMap, from_, to)
        elif self.__data.style == self.Lines:
            self.drawLines(painter, xMap, yMap, from_, to)
        elif self.__data.style == self.Columns:
            self.drawColumns(painter, xMap, yMap, from_, to)
    
    def drawOutline(self, painter, xMap, yMap, from_, to):
        doAlign = QwtPainter.roundingAlignment(painter)
        if self.orientation() == Qt.Horizontal:
            v0 = xMap.transform(self.baseline())
        else:
            v0 = yMap.transform(self.baseline())
        if doAlign:
            v0 = round(v0)
        previous = QwtIntervalSample()
        polygon = QPolygonF()
        for i in range(from_, to+1):
            sample = self.sample(i)
            if not sample.interval.isValid():
                self.flushPolygon(painter, v0, polygon)
                previous = sample
                continue
            if previous.interval.isValid():
                if not qwtIsCombinable(previous.interval, sample.interval):
                    self.flushPolygon(painter, v0, polygon)
            if self.orientation() == Qt.Vertical:
                x1 = xMap.transform(sample.interval.minValue())
                x2 = xMap.transform(sample.interval.maxValue())
                y = yMap.transform(sample.value)
                if doAlign:
                    x1 = round(x1)
                    x2 = round(x2)
                    y = round(y)
                if polygon.size() == 0:
                    polygon += QPointF(x1, v0)
                polygon += QPointF(x1, y)
                polygon += QPointF(x2, y)
            else:
                y1 = yMap.transform(sample.interval.minValue())
                y2 = yMap.transform(sample.interval.maxValue())
                x = xMap.transform(sample.value)
                if doAlign:
                    y1 = round(y1)
                    y2 = round(y2)
                    x = round(x)
                if polygon.size() == 0:
                    polygon += QPointF(v0, y1)
                polygon += QPointF(x, y1)
                polygon += QPointF(x, y2)
            previous = sample
        self.flushPolygon(painter, v0, polygon)
    
    def drawColumns(self, painter, xMap, yMap, from_, to):
        painter.setPen(self.__data.pen)
        painter.setBrush(self.__data.brush)
        series = self.data()
        for i in range(from_, to+1):
            sample = series.sample(i)
            if not sample.interval.isNull():
                rect = self.columnRect(sample, xMap, yMap)
                self.drawColumn(painter, rect, sample)
    
    def drawLines(self, painter, xMap, yMap, from_, to):
        doAlign = QwtPainter.roundingAlignment(painter)
        painter.setPen(self.__data.pen)
        painter.setBrush(self.__data.brush)
        series = self.data()
        for i in range(from_, to+1):
            sample = series.sample(i)
            if not sample.interval.isNull():
                rect = self.columnRect(sample, xMap, yMap)
                r = QRectF(rect.toRect())
                if doAlign:
                    r.setLeft(round(r.left()))
                    r.setRight(round(r.right()))
                    r.setTop(round(r.top()))
                    r.setBottom(round(r.bottom()))
                if rect.direction == QwtColumnRect.LeftToRight:
                    QwtPainter.drawLine(painter, r.topRight(), r.bottomRight())
                elif rect.direction == QwtColumnRect.RightToLeft:
                    QwtPainter.drawLine(painter, r.topLeft(), r.bottomLeft())
                elif rect.direction == QwtColumnRect.TopToBottom:
                    QwtPainter.drawLine(painter, r.bottomRight(), r.bottomLeft())
                elif rect.direction == QwtColumnRect.BottomToTop:
                    QwtPainter.drawLine(painter, r.topRight(), r.topLeft())

    def flushPolygon(self, painter, baseline, polygon):
        if polygon.size() == 0:
            return
        if self.orientation() == Qt.Horizontal:
            polygon += QPointF(baseline, polygon[-1].y())
        else:
            polygon += QPointF(polygon[-1].x(), baseline)
        if self.__data.brush.style() != Qt.NoBrush:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.__data.brush)
            if self.orientation() == Qt.Horizontal:
                polygon += QPointF(polygon[-1].x(), baseline)
                polygon += QPointF(polygon[0].x(), baseline)
            else:
                polygon += QPointF(baseline, polygon[-1].y())
                polygon += QPointF(baseline, polygon[0].y())
            QwtPainter.drawPolygon(painter, polygon)
            polygon.pop(-1)
            polygon.pop(-1)
        if self.__data.pen.style != Qt.NoPen:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(self.__data.pen)
            QwtPainter.drawPolyline(painter, polygon)
        polygon.clear()
    
    def columnRect(self, sample, xMap, yMap):
        rect = QwtColumnRect()
        iv = sample.interval
        if not iv.isValid():
            return rect
        if self.orientation() == Qt.Horizontal:
            x0 = xMap.transform(self.baseline())
            x = xMap.transform(sample.value)
            y1 = yMap.transform(iv.minValue())
            y2 = yMap.transform(iv.maxValue())
            rect.hInterval.setInterval(x0, x)
            rect.vInterval.setInterval(y1, y2, iv.borderFlags())
            if x < x0:
                rect.direction = QwtColumnRect.RightToLeft
            else:
                rect.direction = QwtColumnRect.LeftToRight
        else:
            x1 = xMap.transform(iv.minValue())
            x2 = xMap.transform(iv.maxValue())
            y0 = yMap.transform(self.baseline())
            y = yMap.transform(sample.value)
            rect.hInterval.setInterval(x1, x2, iv.borderFlags())
            rect.vInterval.setInterval(y0, y)
            if y < y0:
                rect.direction = QwtColumnRect.BottomToTop
            else:
                rect.direction = QwtColumnRect.TopToBottom
        return rect
        
    def drawColumn(self, painter, rect, sample):
        if self.__data.symbol and\
           self.__data.symbol.style() != QwtColumnSymbol.NoStyle:
            self.__data.symbol.draw(painter, rect)
        else:
            r = QRectF(rect.toRect())
            if QwtPainter.roundingAlignment(painter):
                r.setLeft(round(r.left()))
                r.setRight(round(r.right()))
                r.setTop(round(r.top()))
                r.setBottom(round(r.bottom()))
            QwtPainter.drawRect(painter, r)
    
    def legendIcon(self, index, size):
        return self.defaultIcon(self.__data.brush, size)
