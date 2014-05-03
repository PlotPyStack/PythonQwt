# -*- coding: utf-8 -*-

from qwt.qwt_curve_fitter import QwtSplineCurveFitter
from qwt.qwt_text import QwtText
from qwt.qwt_plot import QwtPlotItem, QwtPlotItem_PrivateData
from qwt.qwt_painter import QwtPainter
from qwt.qwt_point_mapper import QwtPointMapper
from qwt.qwt_clipper import QwtClipper
from qwt.qwt_math import qwtSqr
from qwt.qwt_graphic import QwtGraphic
from qwt.qwt_series_data import QwtPointSeriesData, QwtSeriesData
from qwt.qwt_series_store import QwtSeriesStore
from qwt.qwt_plot_seriesitem import QwtPlotSeriesItem
from qwt.qwt_point_data import QwtPointArrayData, QwtCPointerData

from qwt.qt.QtGui import QPen, QBrush, QPaintEngine, QPainter, QPolygonF
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
#        self.paintAttributes = QwtPlotCurve.ClipPolygons|QwtPlotCurve.FilterPoints
        #TODO: uncomment previous line when QwtClipper will be implemented
        self.paintAttributes = QwtPlotCurve.FilterPoints
        self.legendAttributes = 0
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
    
    def __init__(self, title):
        if not isinstance(title, QwtText):
            title = QwtText(title)
        self.d_data = None
        QwtPlotSeriesItem.__init__(self, title)
        QwtSeriesStore.__init__(self)
        self.init()
        
    def init(self):
        self.setItemAttribute(QwtPlotItem.Legend)
        self.setItemAttribute(QwtPlotItem.AutoScale)
        self.d_data = QwtPlotCurve_PrivateData()
        self.setData(QwtPointSeriesData())
        self.setZ(20.)
    
    def rtti(self):
        return QwtPlotItem.Rtti_PlotCurve
        
    def setPaintAttribute(self, attribute, on):
        if on:
            self.d_data.paintAttributes |= attribute
        else:
            self.d_data.paintAttributes &= ~attribute
    
    def testPaintAttribute(self, attribute):
        return self.d_data.paintAttributes & attribute
    
    def setLegendAttribute(self, attribute, on):
        if on != self.testLegendAttribute(attribute):
            if on:
                self.d_data.legendAttributes |= attribute
            else:
                self.d_data.legendAttributes &= ~attribute
            qwtUpdateLegendIconSize(self)
            self.legendChanged()
    
    def testLegendAttribute(self, attribute):
        return self.d_data.legendAttributes & attribute
    
    def setStyle(self, style):
        if style != self.d_data.style:
            self.d_data.style = style
            self.legendChanged()
            self.itemChanged()
    
    def style(self):
        return self.d_data.style
    
    def setSymbol(self, symbol):
        if symbol != self.d_data.symbol:
            self.d_data.symbol = symbol
            qwtUpdateLegendIconSize(self)
            self.legendChanged()
            self.itemChanged()
    
    def symbol(self):
        return self.d_data.symbol
    
    def setPen(self, *args):
        if len(args) == 3:
            color, width, style = args
        elif len(args) == 1:
            pen, = args
        else:
            raise TypeError("%s().setPen() takes 1 or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
        if pen != self.d_data.pen:
            self.d_data.pen = pen
            self.legendChanged()
            self.itemChanged()
    
    def pen(self):
        return self.d_data.pen
    
    def setBrush(self, brush):
        if brush != self.d_data.brush:
            self.d_data.brush = brush
            self.legendChanged()
            self.itemChanged()
    
    def brush(self):
        return self.d_data.brush
        
    def drawSeries(self, painter, xMap, yMap, canvasRect, from_, to):
        numSamples = self.dataSize()
        if not painter or numSamples <= 0:
            return
        if to < 0:
            to = numSamples-1
        if qwtVerifyRange(numSamples, from_, to) > 0:
            painter.save()
            painter.setPen(self.d_data.pen)
            self.drawCurve(painter, self.d_data.style, xMap, yMap, canvasRect,
                           from_, to)
            painter.restore()
            if self.d_data.symbol and\
               self.d_data.symbol.style() != QwtSymbol.NoSymbol:
                painter.save()
                self.drawSymbols(painter, self.d_data.symbol,
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
        doAlign = QwtPainter().roundingAlignment(painter)
        doFit = (self.d_data.attributes & self.Fitted)\
                and self.d_data.curveFitter
        doFill = self.d_data.brush.style() != Qt.NoBrush\
                 and self.d_data.brush.color().alpha() > 0
        clipRect = QRectF()
        if self.d_data.paintAttributes & self.ClipPolygons:
            pw = max([1., painter.pen().widthF()])
            clipRect = canvasRect.adjusted(-pw, -pw, pw, pw)
        doIntegers = False
        if QT_VERSION < 0x040800:
            if painter.paintEngine().type() == QPaintEngine.Raster:
                if not doFit and not doFill:
                    doIntegers = True
        noDuplicates = self.d_data.paintAttributes & self.FilterPoints
        mapper = QwtPointMapper()
        mapper.setFlag(QwtPointMapper.RoundPoints, doAlign)
        mapper.setFlag(QwtPointMapper.WeedOutPoints, noDuplicates)
        mapper.setBoundingRect(canvasRect)
        if doIntegers:
            polyline = mapper.toPolygon(xMap, yMap, self.data(), from_, to)
            if self.d_data.paintAttributes & self.ClipPolygons:
                clipped = QwtClipper().clipPolygon(clipRect.toAlignedRect(),
                                                   polyline, False)
                QwtPainter().drawPolyline(painter, clipped)
            else:
                QwtPainter().drawPolyline(painter, polyline)
        else:
            print('*** DEBUG: draw!')
            polyline = mapper.toPolygonF(xMap, yMap, self.data(), from_, to)
            if doFit:
                polyline = self.d_data.curveFitter.fitCurve(polyline)
            if self.d_data.paintAttributes & self.ClipPolygons:
                clipped = QwtClipper().clipPolygonF(clipRect, polyline, False)
                QwtPainter().drawPolyline(painter, clipped)
            else:
                QwtPainter().drawPolyline(painter, polyline)
            if doFill:
                self.fillCurve(painter, xMap, yMap, canvasRect, polyline)
    
    def drawSticks(self, painter, xMap, yMap, canvasRect, from_, to):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, False)
        doAlign = QwtPainter().roundingAlignment(painter)
        x0 = xMap.transform(self.d_data.baseline)
        y0 = yMap.transform(self.d_data.baseline)
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
                QwtPainter().drawLine(painter, x0, yi, xi, yi)
            else:
                QwtPainter().drawLine(painter, xi, y0, xi, yi)
        painter.restore()
        
    def drawDots(self, painter, xMap, yMap, canvasRect, from_, to):
        color = painter.pen().color()
        if painter.pen().style() == Qt.NoPen or color.alpha() == 0:
            return
        doFill = self.d_data.brush.style() != Qt.NoBrush\
                 and self.d_data.brush.color().alpha() > 0
        doAlign = QwtPainter().roundingAlignment(painter)
        mapper = QwtPointMapper()
        mapper.setBoundingRect(canvasRect)
        mapper.setFlag(QwtPointMapper.RoundPoints, doAlign)
        if self.d_data.paintAttributes & self.FilterPoints:
            if color.alpha() == 255\
               and not (painter.renderHints() & QPainter.Antialiasing):
                mapper.setFlag(QwtPointMapper.WeedOutPoints, True)
        if doFill:
            mapper.setFlag(QwtPointMapper.WeedOutPoints, False)
            points = mapper.toPointsF(xMap, yMap, self.data(), from_, to)
            QwtPainter().drawPoints(painter, points)
            self.fillCurve(painter, xMap, yMap, canvasRect, points)
        elif self.d_data.paintAttributes & self.ImageBuffer:
            image = mapper.toImage(xMap, yMap, self.data(), from_, to,
                            self.d_data.pen,
                            painter.testRenderHint(QPainter.Antialiasing),
                            self.renderThreadCount())
            painter.drawImage(canvasRect.toAlignedRect(), image)
        elif self.d_data.paintAttributes & self.MinimizeMemory:
            series = self.data()
            for i in range(from_, to+1):
                sample = series.sample(i)
                xi = xMap.transform(sample.x())
                yi = yMap.transform(sample.y())
                if doAlign:
                    xi = round(xi)
                    yi = round(yi)
                QwtPainter().drawPoint(painter, QPointF(xi, yi))
        else:
            if doAlign:
                points = mapper.toPoints(xMap, yMap, self.data(), from_, to)
                QwtPainter().drawPoints(painter, points)
            else:
                points = mapper.toPointsF(xMap, yMap, self.data(), from_, to)
                QwtPainter().drawPoints(painter, points)
    
    def drawSteps(self, painter, xMap, yMap, canvasRect, from_, to):
        doAlign = QwtPainter().roundingAlignment(painter)
        polygon = QPolygonF(2*(to-from_)+1)
        points = polygon.data()
        inverted = self.orientation() == Qt.Vertical
        if self.d_data.attributes & self.Inverted:
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
                p0 = points[ip-2]
                p = points[ip-1]
                if inverted:
                    p.setX(p0.x())
                    p.setY(yi)
                else:
                    p.setX(xi)
                    p.setY(p0.y())
            points[ip].setX(xi)
            points[ip].setY(yi)
            ip += 2
        if self.d_data.paintAttributes & self.ClipPolygons:
            clipped = QwtClipper().clipPolygonF(canvasRect, polygon, False)
            QwtPainter().drawPolyline(painter, clipped)
        else:
            QwtPainter().drawPolyline(painter, polygon)
        if self.d_data.brush.style() != Qt.NoBrush:
            self.fillCurve(painter, xMap, yMap, canvasRect, polygon)
    
    def setCurveAttribute(self, attribute, on):
        if (self.d_data.attributes & attribute) == on:
            return
        if on:
            self.d_data.attributes |= attribute
        else:
            self.d_data.attributes &= ~attribute
        self.itemChanged()
    
    def testCurveAttribute(self, attribute):
        return self.d_data.attributes & attribute
    
    def setCurveFitter(self, curveFitter):
        self.d_data.curveFitter = curveFitter
        self.itemChanged()
    
    def curveFitter(self):
        return self.d_data.curveFitter
    
    def fillCurve(self, painter, xMap, yMap, canvasRect, polygon):
        if self.d_data.brush.style() == Qt.NoBrush:
            return
        self.closePolyline(painter, xMap, yMap, polygon)
        if polygon.count() <= 2:
            return
        brush = self.d_data.brush
        if not brush.color().isValid():
            brush.setColor(self.d_data.pen.color())
        if self.d_data.paintAttributes & self.ClipPolygons:
            polygon = QwtClipper().clipPolygonF(canvasRect, polygon, True)
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        QwtPainter().drawPolygon(painter, polygon)
        painter.restore()
    
    def closePolyline(self, painter, xMap, yMap, polygon):
        if polygon.size() < 2:
            return
        doAlign = QwtPainter().roundingAlignment(painter)
        baseline = self.d_data.baseline
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
                       QwtPainter().roundingAlignment(painter))
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
        if self.d_data.baseline != value:
            self.d_data.baseline = value
            self.itemChanged()
    
    def baseline(self):
        return self.d_data.baseline
    
    def closestPoint(self, pos, dist):
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
        if dist:
            dist = np.sqrt(dmin)
        return index
    
    def legendIcon(self, index, size):
        if size.isEmpty():
            return QwtGraphic()
        graphic = QwtGraphic()
        graphic.setDefaultSize(size)
        graphic.setRenderHint(QwtGraphic.RenderPensUnscaled, True)
        painter = QPainter(graphic)
        painter.setRenderHint(QPainter.Antialiasing,
                          self.testRenderHint(QwtPlotItem.RenderAntialiased))
        if self.d_data.legendAttributes == 0 or\
           (self.d_data.legendAttributes & QwtPlotCurve.LegendShowBrush):
            brush = self.d_data.brush
            if brush.style() == Qt.NoBrush and self.d_data.legendAttributes == 0:
                if self.style() != QwtPlotCurve.NoCurve:
                    brush = QBrush(self.pen().color())
                elif self.d_data.symbol and\
                     self.d_data.symbol.style() != QwtSymbol.NoSymbol:
                    brush = QBrush(self.d_data.symbol.pen().color())
            if brush.style() != Qt.NoBrush:
                r = QRectF(0, 0, size.width(), size.height())
                painter.fillRect(r, brush)
        if self.d_data.legendAttributes & QwtPlotCurve.LegendShowLine:
            if self.pen() != Qt.NoPen:
                pn = self.pen()
                pn.setCapStyle(Qt.FlatCap)
                painter.setPen(pn)
                y = .5*size.height()
                QwtPainter().drawLine(painter, 0., y, size.width(), y)
        if self.d_data.legendAttributes & QwtPlotCurve.LegendShowSymbol:
            if self.d_data.symbol:
                r = QRectF(0, 0, size.width(), size.height())
                self.d_data.symbol.drawSymbol(painter, r)
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
