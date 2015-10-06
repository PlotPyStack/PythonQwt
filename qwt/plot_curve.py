# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtPlotCurve
------------

.. autoclass:: QwtPlotCurve
   :members:
"""

from qwt.text import QwtText
from qwt.plot import QwtPlotItem, QwtPlotItem_PrivateData
from qwt.painter import QwtPainter
from qwt.point_mapper import QwtPointMapper
from qwt.clipper import QwtClipper
from qwt.math import qwtSqr
from qwt.graphic import QwtGraphic
from qwt.series_data import QwtSeriesData, QwtPointArrayData
from qwt.series_store import QwtSeriesStore
from qwt.plot_seriesitem import QwtPlotSeriesItem
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
        

class QwtPlotCurve(QwtPlotSeriesItem, QwtSeriesStore):
    """
    A plot item, that represents a series of points

    A curve is the representation of a series of points in the x-y plane.
    It supports different display styles, interpolation ( f.e. spline )
    and symbols.
    
    .. seealso::
    
        :py:class:`qwt.symbol.QwtSymbol()`, 
        :py:class:`qwt.scale_map.QwtScaleMap()`
        
    Curve styles:
    
      * `QwtPlotCurve.NoCurve`:
        
        Don't draw a curve. Note: This doesn't affect the symbols.
            
      * `QwtPlotCurve.Lines`:

        Connect the points with straight lines. The lines might
        be interpolated depending on the 'Fitted' attribute. Curve
        fitting can be configured using setCurveFitter().

      * `QwtPlotCurve.Sticks`:
        
        Draw vertical or horizontal sticks ( depending on the 
        orientation() ) from a baseline which is defined by setBaseline().

      * `QwtPlotCurve.Steps`:
        
        Connect the points with a step function. The step function
        is drawn from the left to the right or vice versa,
        depending on the QwtPlotCurve::Inverted attribute.

      * `QwtPlotCurve.Dots`:
        
        Draw dots at the locations of the data points. Note:
        This is different from a dotted line (see setPen()), and faster
        as a curve in QwtPlotCurve::NoStyle style and a symbol 
        painting a point.

      * `QwtPlotCurve.UserCurve`:
        
        Styles >= QwtPlotCurve.UserCurve are reserved for derived
        classes of QwtPlotCurve that overload drawCurve() with
        additional application specific curve types.
    
    Curve attributes:
    
      * `QwtPlotCurve.Inverted`:
        
        For `QwtPlotCurve.Steps` only. 
        Draws a step function from the right to the left.
    
      * `QwtPlotCurve.Fitted`:

        .. warning ::
        
            This option is *not* supported in `PythonQwt`.
    
    Legend attributes:
    
      * `QwtPlotCurve.LegendNoAttribute`:
        
        `QwtPlotCurve` tries to find a color representing the curve 
        and paints a rectangle with it.

      * `QwtPlotCurve.LegendShowLine`:
        
        If the style() is not `QwtPlotCurve.NoCurve` a line 
        is painted with the curve pen().

      * `QwtPlotCurve.LegendShowSymbol`:
        
        If the curve has a valid symbol it is painted.

      * `QwtPlotCurve.LegendShowBrush`:
        
        If the curve has a brush a rectangle filled with the
        curve brush() is painted.
            
    Paint attributes:
    
      * `QwtPlotCurve.ClipPolygons`:
        
        Clip polygons before painting them. In situations, where points
        are far outside the visible area (f.e when zooming deep) this
        might be a substantial improvement for the painting performance
        
        .. warning::
            
            This option is currently *not* supported in `PythonQwt`.

      * `QwtPlotCurve.FilterPoints`:

        Tries to reduce the data that has to be painted, by sorting out
        duplicates, or paintings outside the visible area. Might have a
        notable impact on curves with many close points.
        Only a couple of very basic filtering algorithms are implemented.

      * `QwtPlotCurve.MinimizeMemory`:
        
        .. warning::

            This option was removed as it has no sense in `PythonQwt` 
            (the polyline plotting is not taking more memory than the 
            array data that is already there).
            
      * `QwtPlotCurve.ImageBuffer`:
        
        Render the points to a temporary image and paint the image.
        This is a very special optimization for Dots style, when
        having a huge amount of points. 
        With a reasonable number of points QPainter.drawPoints()
        will be faster.

            
    .. py:class:: QwtPlotCurve([title=None])
    
        Constructor
        
        :param title: Curve title
        :type title: qwt.text.QwtText or str or None
    """
    
    # enum CurveStyle
    NoCurve = -1
    Lines, Sticks, Steps, Dots = list(range(4))
    UserCurve = 100
    
    # enum CurveAttribute
    Inverted = 0x01
    
    # enum LegendAttribute
    LegendNoAttribute = 0x00
    LegendShowLine = 0x01
    LegendShowSymbol = 0x02
    LegendShowBrush = 0x04
    
    # enum PaintAttribute
    ClipPolygons = 0x01
    FilterPoints = 0x02
    # MinimizeMemory = 0x04 --> not necessary, see CHANGELOG
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
        """Initialize internal members"""
        self.__data = QwtPlotCurve_PrivateData()
        self.setItemAttribute(QwtPlotItem.Legend)
        self.setItemAttribute(QwtPlotItem.AutoScale)
        self.setData(QwtPointArrayData())
        self.setZ(20.)
    
    def rtti(self):
        """:return: `QwtPlotItem.Rtti_PlotCurve`"""
        return QwtPlotItem.Rtti_PlotCurve
        
    def setPaintAttribute(self, attribute, on=True):
        """
        Specify an attribute how to draw the curve

        Supported paint attributes:
        
            * `QwtPlotCurve.FilterPoints`
            * `QwtPlotCurve.ImageBuffer`
        
        :param int attribute: Paint attribute
        :param bool on: On/Off
        
        .. seealso::
        
            :py:meth:`testPaintAttribute()`
        """
        if on:
            self.__data.paintAttributes |= attribute
        else:
            self.__data.paintAttributes &= ~attribute
    
    def testPaintAttribute(self, attribute):
        """
        :param int attribute: Paint attribute
        :return: True, when attribute is enabled
        
        .. seealso::
        
            :py:meth:`setPaintAttribute()`
        """
        return self.__data.paintAttributes & attribute
    
    def setLegendAttribute(self, attribute, on=True):
        """
        Specify an attribute how to draw the legend icon
        
        Legend attributes:
        
            * `QwtPlotCurve.LegendNoAttribute`
            * `QwtPlotCurve.LegendShowLine`
            * `QwtPlotCurve.LegendShowSymbol`
            * `QwtPlotCurve.LegendShowBrush`
            
        :param int attribute: Legend attribute
        :param bool on: On/Off
        
        .. seealso::
        
            :py:meth:`testLegendAttribute()`, :py:meth:`legendIcon()`
        """
        if on != self.testLegendAttribute(attribute):
            if on:
                self.__data.legendAttributes |= attribute
            else:
                self.__data.legendAttributes &= ~attribute
            qwtUpdateLegendIconSize(self)
            self.legendChanged()
    
    def testLegendAttribute(self, attribute):
        """
        :param int attribute: Legend attribute
        :return: True, when attribute is enabled
        
        .. seealso::
        
            :py:meth:`setLegendAttribute()`
        """
        return self.__data.legendAttributes & attribute
    
    def setStyle(self, style):
        """
        Set the curve's drawing style
        
        Valid curve styles:
        
            * `QwtPlotCurve.NoCurve`
            * `QwtPlotCurve.Lines`
            * `QwtPlotCurve.Sticks`
            * `QwtPlotCurve.Steps`
            * `QwtPlotCurve.Dots`
            * `QwtPlotCurve.UserCurve`
            
        :param int style: Curve style
        
        .. seealso::
        
            :py:meth:`style()`
        """
        if style != self.__data.style:
            self.__data.style = style
            self.legendChanged()
            self.itemChanged()
    
    def style(self):
        """
        :return: Style of the curve
        
        .. seealso::
        
            :py:meth:`setStyle()`
        """
        return self.__data.style
    
    def setSymbol(self, symbol):
        """
        Assign a symbol

        The curve will take the ownership of the symbol, hence the previously
        set symbol will be delete by setting a new one. If symbol is None no 
        symbol will be drawn.
        
        :param qwt.symbol.QwtSymbol symbol: Symbol
        
        .. seealso::
        
            :py:meth:`symbol()`
        """
        if symbol != self.__data.symbol:
            self.__data.symbol = symbol
            qwtUpdateLegendIconSize(self)
            self.legendChanged()
            self.itemChanged()
    
    def symbol(self):
        """
        :return: Current symbol or None, when no symbol has been assigned
        
        .. seealso::
        
            :py:meth:`setSymbol()`
        """
        return self.__data.symbol
    
    def setPen(self, *args):
        """
        Build and/or assign a pen, depending on the arguments.
        
        .. py:method:: setPen(color, width, style)
        
            Build and assign a pen
    
            In Qt5 the default pen width is 1.0 ( 0.0 in Qt4 ) what makes it
            non cosmetic (see `QPen.isCosmetic()`). This method signature has 
            been introduced to hide this incompatibility.
            
            :param QColor color: Pen color
            :param float width: Pen width
            :param Qt.PenStyle style: Pen style
        
        .. py:method:: setPen(pen)
        
            Assign a pen
    
            :param QPen pen: New pen
        
        .. seealso::
        
            :py:meth:`pen()`, :py:meth:`brush()`
        """
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
        """
        :return: Pen used to draw the lines
        
        .. seealso::
        
            :py:meth:`setPen()`, :py:meth:`brush()`
        """
        return self.__data.pen
    
    def setBrush(self, brush):
        """
        Assign a brush.

        In case of `brush.style() != QBrush.NoBrush`
        and `style() != QwtPlotCurve.Sticks`
        the area between the curve and the baseline will be filled.
        
        In case `not brush.color().isValid()` the area will be filled by
        `pen.color()`. The fill algorithm simply connects the first and the
        last curve point to the baseline. So the curve data has to be sorted
        (ascending or descending).
        
        :param brush: New brush
        :type brush: QBrush or QColor
        
        .. seealso::
        
            :py:meth:`brush()`, :py:meth:`setBaseline()`, :py:meth:`baseline()`
        """
        if isinstance(brush, QColor):
            brush = QBrush(brush)
        else:
            assert isinstance(brush, QBrush)
        if brush != self.__data.brush:
            self.__data.brush = brush
            self.legendChanged()
            self.itemChanged()
    
    def brush(self):
        """
        :return: Brush used to fill the area between lines and the baseline
        
        .. seealso::
        
            :py:meth:`setBrush()`, :py:meth:`setBaseline()`, 
            :py:meth:`baseline()`
        """
        return self.__data.brush
    
    def directPaint(self, from_, to):
        """
        When observing a measurement while it is running, new points have 
        to be added to an existing seriesItem. This method can be used to 
        display them avoiding a complete redraw of the canvas.

        Setting `plot().canvas().setAttribute(Qt.WA_PaintOutsidePaintEvent, True)`
        will result in faster painting, if the paint engine of the canvas 
        widget supports this feature.
        
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted
        
        .. seealso::
        
            :py:meth:`drawSeries()`
        """
        directPainter = QwtPlotDirectPainter(self.plot())
        directPainter.drawSeries(self, from_, to)
        
    def drawSeries(self, painter, xMap, yMap, canvasRect, from_, to):
        """
        Draw an interval of the curve
        
        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted. If to < 0 the curve will be painted to its last point.
        
        .. seealso::
        
            :py:meth:`drawCurve()`, :py:meth:`drawSymbols()`
        """
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
        """
        Draw the line part (without symbols) of a curve interval.
        
        :param QPainter painter: Painter
        :param int style: curve style, see `QwtPlotCurve.CurveStyle`
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted. If to < 0 the curve will be painted to its last point.
        
        .. seealso::
        
            :py:meth:`draw()`, :py:meth:`drawDots()`, :py:meth:`drawLines()`, 
            :py:meth:`drawSteps()`, :py:meth:`drawSticks()`
        """
        if style == self.Lines:
            self.drawLines(painter, xMap, yMap, canvasRect, from_, to)
        elif style == self.Sticks:
            self.drawSticks(painter, xMap, yMap, canvasRect, from_, to)
        elif style == self.Steps:
            self.drawSteps(painter, xMap, yMap, canvasRect, from_, to)
        elif style == self.Dots:
            self.drawDots(painter, xMap, yMap, canvasRect, from_, to)
    
    def drawLines(self, painter, xMap, yMap, canvasRect, from_, to):
        """
        Draw lines
        
        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted. If to < 0 the curve will be painted to its last point.
        
        .. seealso::
        
            :py:meth:`draw()`, :py:meth:`drawDots()`, 
            :py:meth:`drawSteps()`, :py:meth:`drawSticks()`
        """
        if from_ > to:
            return
        doAlign = QwtPainter.roundingAlignment(painter)
        doFill = self.__data.brush.style() != Qt.NoBrush\
                 and self.__data.brush.color().alpha() > 0
        clipRect = QRectF()
        if self.__data.paintAttributes & self.ClipPolygons:
            pw = max([1., painter.pen().widthF()])
            clipRect = canvasRect.adjusted(-pw, -pw, pw, pw)
        doIntegers = False
        if QT_VERSION < 0x040800:
            if painter.paintEngine().type() == QPaintEngine.Raster:
                if not doFill:
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
        """
        Draw sticks
        
        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted. If to < 0 the curve will be painted to its last point.
        
        .. seealso::
        
            :py:meth:`draw()`, :py:meth:`drawDots()`, 
            :py:meth:`drawSteps()`, :py:meth:`drawLines()`
        """
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
        """
        Draw dots
        
        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted. If to < 0 the curve will be painted to its last point.
        
        .. seealso::
        
            :py:meth:`draw()`, :py:meth:`drawSticks()`, 
            :py:meth:`drawSteps()`, :py:meth:`drawLines()`
        """
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
                               painter.testRenderHint(QPainter.Antialiasing))
            painter.drawImage(canvasRect.toAlignedRect(), image)
        else:
            if doAlign:
                points = mapper.toPoints(xMap, yMap, self.data(), from_, to)
                QwtPainter.drawPoints(painter, points)
            else:
                points = mapper.toPointsF(xMap, yMap, self.data(), from_, to)
                QwtPainter.drawPoints(painter, points)
    
    def drawSteps(self, painter, xMap, yMap, canvasRect, from_, to):
        """
        Draw steps
        
        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted. If to < 0 the curve will be painted to its last point.
        
        .. seealso::
        
            :py:meth:`draw()`, :py:meth:`drawSticks()`, 
            :py:meth:`drawDots()`, :py:meth:`drawLines()`
        """
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
        """
        Specify an attribute for drawing the curve
        
        Supported curve attributes:

            * `QwtPlotCurve.Inverted`

        :param int attribute: Curve attribute
        :param bool on: On/Off
        
        .. seealso::
        
            :py:meth:`testCurveAttribute()`
        """
        if (self.__data.attributes & attribute) == on:
            return
        if on:
            self.__data.attributes |= attribute
        else:
            self.__data.attributes &= ~attribute
        self.itemChanged()
    
    def testCurveAttribute(self, attribute):
        """
        :return: True, if attribute is enabled
        
        .. seealso::
        
            :py:meth:`setCurveAttribute()`
        """
        return self.__data.attributes & attribute
    
    def fillCurve(self, painter, xMap, yMap, canvasRect, polygon):
        """
        Fill the area between the curve and the baseline with
        the curve brush

        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        :param QPolygonF polygon: Polygon - will be modified !
        
        .. seealso::
        
            :py:meth:`setBrush()`, :py:meth:`setBaseline()`, 
            :py:meth:`setStyle()`
        """
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
        """
        Complete a polygon to be a closed polygon including the 
        area between the original polygon and the baseline.

        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QPolygonF polygon: Polygon to be completed
        """
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
        """
        Draw symbols
        
        :param QPainter painter: Painter
        :param qwt.symbol.QwtSymbol symbol: Curve symbol
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted. If to < 0 the curve will be painted to its last point.
        
        .. seealso::
        
            :py:meth:`setSymbol()`, :py:meth:`drawSeries()`, 
            :py:meth:`drawCurve()`
        """
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
        """
        Set the value of the baseline

        The baseline is needed for filling the curve with a brush or
        the Sticks drawing style.
        
        The interpretation of the baseline depends on the `orientation()`.
        With `Qt.Horizontal`, the baseline is interpreted as a horizontal line
        at y = baseline(), with `Qt.Vertical`, it is interpreted as a vertical
        line at x = baseline().
        
        The default value is 0.0.
        
        :param float value: Value of the baseline
        
        .. seealso::
        
            :py:meth:`baseline()`, :py:meth:`setBrush()`, 
            :py:meth:`setStyle()`
        """
        if self.__data.baseline != value:
            self.__data.baseline = value
            self.itemChanged()
    
    def baseline(self):
        """
        :return: Value of the baseline
        
        .. seealso::
        
            :py:meth:`setBaseline()`
        """
        return self.__data.baseline
    
    def closestPoint(self, pos):
        """
        Find the closest curve point for a specific position
        
        :param QPoint pos: Position, where to look for the closest curve point
        :return: tuple `(index, dist)`
        
        `dist` is the distance between the position and the closest curve 
        point. `index` is the index of the closest curve point, or -1 if 
        none can be found ( f.e when the curve has no points ).
        
        .. note::
        
            `closestPoint()` implements a dumb algorithm, that iterates
            over all points
        """
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
        """
        :param int index: Index of the legend entry (ignored as there is only one)
        :param QSizeF size: Icon size
        :return: Icon representing the curve on the legend
        
        .. seealso::
        
            :py:meth:`qwt.plot.QwtPlotItem.setLegendIconSize()`,
            :py:meth:`qwt.plot.QwtPlotItem.legendData()`
        """
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
        """
        Initialize data with an array of points.
        
        .. py:method:: setSamples(samples):
        
            Same as `setData(QwtPointArrayData(samples))`
        
            :param samples: List/array of points
        
        .. py:method:: setSamples(xData, yData, [size=None]):

            Same as `setData(QwtPointArrayData(xData, yData, [size=None]))`
        
            :param xData: List/array of x values
            :param yData: List/array of y values
            :param size: size of xData and yData
            :type size: int or None
        
        .. seealso::
        
            :py:class:`qwt.point_data.QwtPointArrayData`,
        """
        if len(args) == 1:
            samples, = args
            if isinstance(samples, QwtSeriesData):
                self.setData(samples)
            else:
                self.setData(QwtPointArrayData(samples))
        elif len(args) == 3:
            xData, yData, size = args
            self.setData(QwtPointArrayData(xData, yData, size))
        elif len(args) == 2:
            xData, yData = args
            self.setData(QwtPointArrayData(xData, yData))
        else:
            raise TypeError("%s().setSamples() takes 1, 2 or 3 argument(s) "\
                            "(%s given)" % (self.__class__.__name__, len(args)))
