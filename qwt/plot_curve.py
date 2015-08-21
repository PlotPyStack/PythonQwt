# -*- coding: utf-8 -*-

from qwt.curve_fitter import QwtSplineCurveFitter
from qwt.text import QwtText
from qwt.plot import QwtPlotItem, QwtPlotItem_PrivateData
from qwt.painter import QwtPainter
from qwt.point_mapper import QwtPointMapper
from qwt.clipper import QwtClipper
from qwt.math import qwtSqr
from qwt.graphic import QwtGraphic
from qwt.series_data import QwtPointSeriesData, QwtSeriesData
from qwt.series_store import QwtSeriesStore
from qwt.plot_seriesitem import QwtPlotSeriesItem
from qwt.point_data import QwtPointArrayData, QwtCPointerData
from qwt.symbol import QwtSymbol
from qwt.plot_directpainter import QwtPlotDirectPainter

from qwt.qt.QtGui import (QPen, QBrush, QPaintEngine, QPainter, QPolygonF,
                          QColor)
from qwt.qt.QtCore import QSize, Qt, QT_VERSION, QRectF, QPointF

import numpy as np


def qwtUpdateLegendIconSize(curve):
    if curve.symbol() and\
       curve.testLegendAttribute(QwtPlotCurve.LegendShowSymbol):
        sz = curve.symbol().boundingRect().size()
        sz += QSize(2, 2)
        if curve.testLegendAttribute(QwtPlotCurve.LegendShowLine):
            w = np.ceil(1.5*sz.width())
            if w % 2:
                w += 1
            sz.setWidth(max([8, w]))
        curve.setLegendIconSize(sz)

def qwtVerifyRange(size, i1, i2):
    if size < 1:
        return 0
    i1 = max([0, min([i1, size-1])])
    i2 = max([0, min([i2, size-1])])
    if i1 > i2:
        i1, i2 = i2, i1
    return i2-i1+1


class QwtPlotCurve_PrivateData(QwtPlotItem_PrivateData):
    def __init__(self):
        QwtPlotItem_PrivateData.__init__(self)
        self.style = QwtPlotCurve.Lines
        self.baseline = 0.
        self.symbol = None
        self.attributes = 0
        self.paintAttributes = QwtPlotCurve.FilterPoints
        #TODO: uncomment next line when QwtClipper will be implemented
#        self.paintAttributes = QwtPlotCurve.ClipPolygons|QwtPlotCurve.FilterPoints
        self.legendAttributes = QwtPlotCurve.LegendShowLine
        self.pen = QPen(Qt.black)
        self.brush = QBrush()
        self.curveFitter = QwtSplineCurveFitter()
        

class QwtPlotCurve(QwtPlotSeriesItem, QwtSeriesStore):
    
    # enum CurveStyle
    NoCurve = -1
    Lines, Sticks, Steps, Dots = range(4)
    UserCurve = 100
    
    # enum CurveAttribute
    Inverted = 0x01
    Fitted = 0x02
    
    # enum LegendAttribute
    LegendNoAttribute = 0x00
    LegendShowLine = 0x01
    LegendShowSymbol = 0x02
    LegendShowBrush = 0x04
    
    # enum PaintAttribute
    ClipPolygons = 0x01
    FilterPoints = 0x02
    MinimizeMemory = 0x04
    ImageBuffer = 0x08
    
    def __init__(self, title=None):
        if title is None:
            title = QwtText("")
        if not isinstance(title, QwtText):
            title = QwtText(title)
        self.__data = None
        QwtPlotSeriesItem.__init__(self, title)
        QwtSeriesStore.__init__(self)
        self.init()
        
    def init(self):
        self.__data = QwtPlotCurve_PrivateData()
        self.setItemAttribute(QwtPlotItem.Legend)
        self.setItemAttribute(QwtPlotItem.AutoScale)
        self.setData(QwtPointSeriesData())
        self.setZ(20.)
    
    def rtti(self):
        return QwtPlotItem.Rtti_PlotCurve
        
    def setPaintAttribute(self, attribute, on=True):
        if on:
            self.__data.paintAttributes |= attribute
        else:
            self.__data.paintAttributes &= ~attribute
    
    def testPaintAttribute(self, attribute):
        return self.__data.paintAttributes & attribute
    
    def setLegendAttribute(self, attribute, on=True):
        if on != self.testLegendAttribute(attribute):
            if on:
                self.__data.legendAttributes |= attribute
            else:
                self.__data.legendAttributes &= ~attribute
            qwtUpdateLegendIconSize(self)
            self.legendChanged()
    
    def testLegendAttribute(self, attribute):
        return self.__data.legendAttributes & attribute
    
    def setStyle(self, style):
        if style != self.__data.style:
            self.__data.style = style
            self.legendChanged()
            self.itemChanged()
    
    def style(self):
        return self.__data.style
    
    def setSymbol(self, symbol):
        if symbol != self.__data.symbol:
            self.__data.symbol = symbol
            qwtUpdateLegendIconSize(self)
            self.legendChanged()
            self.itemChanged()
    
    def symbol(self):
        return self.__data.symbol
    
    def setPen(self, *args):
        if len(args) == 3:
            color, width, style = args
        elif len(args) == 1:
            pen, = args
        else:
            raise TypeError("%s().setPen() takes 1 or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
        if pen != self.__data.pen:
            if isinstance(pen, QColor):
                pen = QPen(pen)
            else:
                assert isinstance(pen, QPen)
            self.__data.pen = pen
            self.legendChanged()
            self.itemChanged()
    
    def pen(self):
        return self.__data.pen
    
    def setBrush(self, brush):
        if isinstance(brush, QColor):
            brush = QBrush(brush)
        else:
            assert isinstance(brush, QBrush)
        if brush != self.__data.brush:
            self.__data.brush = brush
            self.legendChanged()
            self.itemChanged()
    
    def brush(self):
        return self.__data.brush
    
    def directPaint(self, from_, to):
        """When observing an measurement while it is running, new points have 
        to be added to an existing seriesItem. drawSeries() can be used to 
        display them avoiding a complete redraw of the canvas.

        Setting plot().canvas().setAttribute(Qt.WA_PaintOutsidePaintEvent, True)
        will result in faster painting, if the paint engine of the canvas widget
        supports this feature."""
        directPainter = QwtPlotDirectPainter(self.plot())
        directPainter.drawSeries(self, from_, to)
        
    def drawSeries(self, painter, xMap, yMap, canvasRect, from_, to):
        numSamples = self.dataSize()
        if not painter or numSamples <= 0:
            return
        if to < 0:
            to = numSamples-1
        if qwtVerifyRange(numSamples, from_, to) > 0:
            painter.save()
            painter.setPen(self.__data.pen)
            self.drawCurve(painter, self.__data.style, xMap, yMap, canvasRect,
                           from_, to)
            painter.restore()
            if self.__data.symbol and\
               self.__data.symbol.style() != QwtSymbol.NoSymbol:
                painter.save()
                self.drawSymbols(painter, self.__data.symbol,
                                 xMap, yMap, canvasRect, from_, to)
                painter.restore()
    
    def drawCurve(self, painter, style, xMap, yMap, canvasRect, from_, to):
        if style == self.Lines:
            if self.testCurveAttribute(self.Fitted):
                from_ = 0
                to = self.dataSize()-1
            self.drawLines(painter, xMap, yMap, canvasRect, from_, to)
        elif style == self.Sticks:
            self.drawSticks(painter, xMap, yMap, canvasRect, from_, to)
        elif style == self.Steps:
            self.drawSteps(painter, xMap, yMap, canvasRect, from_, to)
        elif style == self.Dots:
            self.drawDots(painter, xMap, yMap, canvasRect, from_, to)
    
    def drawLines(self, painter, xMap, yMap, canvasRect, from_, to):
        if from_ > to:
            return
        doAlign = QwtPainter.roundingAlignment(painter)
        doFit = (self.__data.attributes & self.Fitted)\
                and self.__data.curveFitter
        doFill = self.__data.brush.style() != Qt.NoBrush\
                 and self.__data.brush.color().alpha() > 0
        clipRect = QRectF()
        if self.__data.paintAttributes & self.ClipPolygons:
            pw = max([1., painter.pen().widthF()])
            clipRect = canvasRect.adjusted(-pw, -pw, pw, pw)
        doIntegers = False
        if QT_VERSION < 0x040800:
            if painter.paintEngine().type() == QPaintEngine.Raster:
                if not doFit and not doFill:
                    doIntegers = True
        noDuplicates = self.__data.paintAttributes & self.FilterPoints
        mapper = QwtPointMapper()
        mapper.setFlag(QwtPointMapper.RoundPoints, doAlign)
        mapper.setFlag(QwtPointMapper.WeedOutPoints, noDuplicates)
        mapper.setBoundingRect(canvasRect)
        if doIntegers:
            polyline = mapper.toPolygon(xMap, yMap, self.data(), from_, to)
            if self.__data.paintAttributes & self.ClipPolygons:
                polyline = QwtClipper().clipPolygon(clipRect.toAlignedRect(),
                                                   polyline, False)
            QwtPainter.drawPolyline(painter, polyline)
        else:
            polyline = mapper.toPolygonF(xMap, yMap, self.data(), from_, to)
            if doFit:
                polyline = self.__data.curveFitter.fitCurve(polyline)
            if doFill:
                if painter.pen().style() != Qt.NoPen:
                    filled = QPolygonF(polyline)
                    self.fillCurve(painter, xMap, yMap, canvasRect, filled)
                    filled.clear()
                    if self.__data.paintAttributes & self.ClipPolygons:
                        polyline = QwtClipper().clipPolygonF(clipRect,
                                                             polyline, False)
                    QwtPainter.drawPolyline(painter, polyline)
                else:
                    self.fillCurve(painter, xMap, yMap, canvasRect, polyline)
            else:
                if self.__data.paintAttributes & self.ClipPolygons:
                    polyline = QwtClipper().clipPolygonF(clipRect, polyline,
                                                         False)
                QwtPainter.drawPolyline(painter, polyline)
    
    def drawSticks(self, painter, xMap, yMap, canvasRect, from_, to):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, False)
        doAlign = QwtPainter.roundingAlignment(painter)
        x0 = xMap.transform(self.__data.baseline)
        y0 = yMap.transform(self.__data.baseline)
        if doAlign:
            x0 = round(x0)
            y0 = round(y0)
        o = self.orientation()
        series = self.data()
        for i in range(from_, to+1):
            sample = series.sample(i)
            xi = xMap.transform(sample.x())
            yi = yMap.transform(sample.y())
            if doAlign:
                xi = round(xi)
                yi = round(yi)
            if o == Qt.Horizontal:
                QwtPainter.drawLine(painter, x0, yi, xi, yi)
            else:
                QwtPainter.drawLine(painter, xi, y0, xi, yi)
        painter.restore()
        
    def drawDots(self, painter, xMap, yMap, canvasRect, from_, to):
        color = painter.pen().color()
        if painter.pen().style() == Qt.NoPen or color.alpha() == 0:
            return
        doFill = self.__data.brush.style() != Qt.NoBrush\
                 and self.__data.brush.color().alpha() > 0
        doAlign = QwtPainter.roundingAlignment(painter)
        mapper = QwtPointMapper()
        mapper.setBoundingRect(canvasRect)
        mapper.setFlag(QwtPointMapper.RoundPoints, doAlign)
        if self.__data.paintAttributes & self.FilterPoints:
            if color.alpha() == 255\
               and not (painter.renderHints() & QPainter.Antialiasing):
                mapper.setFlag(QwtPointMapper.WeedOutPoints, True)
        if doFill:
            mapper.setFlag(QwtPointMapper.WeedOutPoints, False)
            points = mapper.toPointsF(xMap, yMap, self.data(), from_, to)
            QwtPainter.drawPoints(painter, points)
            self.fillCurve(painter, xMap, yMap, canvasRect, points)
        elif self.__data.paintAttributes & self.ImageBuffer:
            image = mapper.toImage(xMap, yMap, self.data(), from_, to,
                            self.__data.pen,
                            painter.testRenderHint(QPainter.Antialiasing),
                            self.renderThreadCount())
            painter.drawImage(canvasRect.toAlignedRect(), image)
        elif self.__data.paintAttributes & self.MinimizeMemory:
            series = self.data()
            for i in range(from_, to+1):
                sample = series.sample(i)
                xi = xMap.transform(sample.x())
                yi = yMap.transform(sample.y())
                if doAlign:
                    xi = round(xi)
                    yi = round(yi)
                QwtPainter.drawPoint(painter, QPointF(xi, yi))
        else:
            if doAlign:
                points = mapper.toPoints(xMap, yMap, self.data(), from_, to)
                QwtPainter.drawPoints(painter, points)
            else:
                points = mapper.toPointsF(xMap, yMap, self.data(), from_, to)
                QwtPainter.drawPoints(painter, points)
    
    def drawSteps(self, painter, xMap, yMap, canvasRect, from_, to):
        doAlign = QwtPainter.roundingAlignment(painter)
        polygon = QPolygonF(2*(to-from_)+1)
        inverted = self.orientation() == Qt.Vertical
        if self.__data.attributes & self.Inverted:
            inverted = not inverted
        series = self.data()
        ip = 0
        for i in range(from_, to+1):
            sample = series.sample(i)
            xi = xMap.transform(sample.x())
            yi = yMap.transform(sample.y())
            if doAlign:
                xi = round(xi)
                yi = round(yi)
            if ip > 0:
                p0 = polygon[ip-2]
                if inverted:
                    polygon[ip-1] = QPointF(p0.x(), yi)
                else:
                    polygon[ip-1] = QPointF(xi, p0.y())
            polygon[ip] = QPointF(xi, yi)
            ip += 2
        if self.__data.paintAttributes & self.ClipPolygons:
            clipped = QwtClipper().clipPolygonF(canvasRect, polygon, False)
            QwtPainter.drawPolyline(painter, clipped)
        else:
            QwtPainter.drawPolyline(painter, polygon)
        if self.__data.brush.style() != Qt.NoBrush:
            self.fillCurve(painter, xMap, yMap, canvasRect, polygon)
    
    def setCurveAttribute(self, attribute, on=True):
        if (self.__data.attributes & attribute) == on:
            return
        if on:
            self.__data.attributes |= attribute
        else:
            self.__data.attributes &= ~attribute
        self.itemChanged()
    
    def testCurveAttribute(self, attribute):
        return self.__data.attributes & attribute
    
    def setCurveFitter(self, curveFitter):
        self.__data.curveFitter = curveFitter
        self.itemChanged()
    
    def curveFitter(self):
        return self.__data.curveFitter
    
    def fillCurve(self, painter, xMap, yMap, canvasRect, polygon):
        if self.__data.brush.style() == Qt.NoBrush:
            return
        self.closePolyline(painter, xMap, yMap, polygon)
        if polygon.count() <= 2:
            return
        brush = self.__data.brush
        if not brush.color().isValid():
            brush.setColor(self.__data.pen.color())
        if self.__data.paintAttributes & self.ClipPolygons:
            polygon = QwtClipper().clipPolygonF(canvasRect, polygon, True)
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        QwtPainter.drawPolygon(painter, polygon)
        painter.restore()
    
    def closePolyline(self, painter, xMap, yMap, polygon):
        if polygon.size() < 2:
            return
        doAlign = QwtPainter.roundingAlignment(painter)
        baseline = self.__data.baseline
        if self.orientation() == Qt.Vertical:
            if yMap.transformation():
                baseline = yMap.transformation().bounded(baseline)
            refY = yMap.transform(baseline)
            if doAlign:
                refY = round(refY)
            polygon += QPointF(polygon.last().x(), refY)
            polygon += QPointF(polygon.first().x(), refY)
        else:
            if xMap.transformation():
                baseline = xMap.transformation().bounded(baseline)
            refX = xMap.transform(baseline)
            if doAlign:
                refX = round(refX)
            polygon += QPointF(refX, polygon.last().y())
            polygon += QPointF(refX, polygon.first().y())
    
    def drawSymbols(self, painter, symbol, xMap, yMap, canvasRect, from_, to):
        mapper = QwtPointMapper()
        mapper.setFlag(QwtPointMapper.RoundPoints,
                       QwtPainter.roundingAlignment(painter))
        mapper.setFlag(QwtPointMapper.WeedOutPoints,
                       self.testPaintAttribute(QwtPlotCurve.FilterPoints))
        mapper.setBoundingRect(canvasRect)
        chunkSize = 500
        for i in range(from_, to+1, chunkSize):
            n = min([chunkSize, to-i+1])
            points = mapper.toPointsF(xMap, yMap, self.data(), i, i+n-1)
            if points.size() > 0:
                symbol.drawSymbols(painter, points)
    
    def setBaseline(self, value):
        if self.__data.baseline != value:
            self.__data.baseline = value
            self.itemChanged()
    
    def baseline(self):
        return self.__data.baseline
    
    def closestPoint(self, pos):
        numSamples = self.dataSize()
        if self.plot() is None or numSamples <= 0:
            return -1
        series = self.data()
        xMap = self.plot().canvasMap(self.xAxis())
        yMap = self.plot().canvasMap(self.yAxis())
        index = -1
        dmin = 1.0e10
        for i in range(numSamples):
            sample = series.sample(i)
            cx = xMap.transform(sample.x())-pos.x()
            cy = yMap.transform(sample.y())-pos.y()
            f = qwtSqr(cx)+qwtSqr(cy)
            if f < dmin:
                index = i
                dmin = f
        dist = np.sqrt(dmin)
        return index, dist
    
    def legendIcon(self, index, size):
        if size.isEmpty():
            return QwtGraphic()
        graphic = QwtGraphic()
        graphic.setDefaultSize(size)
        graphic.setRenderHint(QwtGraphic.RenderPensUnscaled, True)
        painter = QPainter(graphic)
        painter.setRenderHint(QPainter.Antialiasing,
                          self.testRenderHint(QwtPlotItem.RenderAntialiased))
        if self.__data.legendAttributes == 0 or\
           (self.__data.legendAttributes & QwtPlotCurve.LegendShowBrush):
            brush = self.__data.brush
            if brush.style() == Qt.NoBrush and self.__data.legendAttributes == 0:
                if self.style() != QwtPlotCurve.NoCurve:
                    brush = QBrush(self.pen().color())
                elif self.__data.symbol and\
                     self.__data.symbol.style() != QwtSymbol.NoSymbol:
                    brush = QBrush(self.__data.symbol.pen().color())
            if brush.style() != Qt.NoBrush:
                r = QRectF(0, 0, size.width(), size.height())
                painter.fillRect(r, brush)
        if self.__data.legendAttributes & QwtPlotCurve.LegendShowLine:
            if self.pen() != Qt.NoPen:
                pn = self.pen()
#                pn.setCapStyle(Qt.FlatCap)
                painter.setPen(pn)
                y = .5*size.height()
                QwtPainter.drawLine(painter, 0., y, size.width(), y)
        if self.__data.legendAttributes & QwtPlotCurve.LegendShowSymbol:
            if self.__data.symbol:
                r = QRectF(0, 0, size.width(), size.height())
                self.__data.symbol.drawSymbol(painter, r)
        return graphic    

    def setData(self, *args):
        """Compatibility with Qwt5"""
        if len(args) == 1:
            super(QwtPlotCurve, self).setData(*args)
        elif len(args) == 2:
            self.setSamples(*args)
        else:
            raise TypeError("%s().setData() takes 1 or 2 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def setSamples(self, *args):
        if len(args) == 1:
            samples, = args
            if isinstance(samples, QwtSeriesData):
                self.setData(samples)
            else:
                self.setData(QwtPointSeriesData(samples))
        elif len(args) == 3:
            xData, yData, size = args
            self.setData(QwtPointArrayData(xData, yData, size))
        elif len(args) == 2:
            xData, yData = args
            self.setData(QwtPointArrayData(xData, yData))
        else:
            raise TypeError("%s().setSamples() takes 1, 2 or 3 argument(s) "\
                            "(%s given)" % (self.__class__.__name__, len(args)))
    
    def setRawSamples(self, xData, yData, size):
        self.setData(QwtCPointerData(xData, yData, size))
