# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtPlotGrid
-----------

.. autoclass:: QwtPlotGrid
   :members:
"""

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
    """
    A class which draws a coordinate grid

    The `QwtPlotGrid` class can be used to draw a coordinate grid.
    A coordinate grid consists of major and minor vertical
    and horizontal grid lines. The locations of the grid lines
    are determined by the X and Y scale divisions which can
    be assigned with `setXDiv()` and `setYDiv()`.
    The `draw()` member draws the grid within a bounding
    rectangle.
    """
    
    def __init__(self):
        QwtPlotItem.__init__(self, QwtText("Grid"))
        self.__data = QwtPlotGrid_PrivateData()
        self.setItemInterest(QwtPlotItem.ScaleInterest, True)
        self.setZ(10.)
        
    def rtti(self):
        """
        :return: Return `QwtPlotItem.Rtti_PlotGrid`
        """
        return QwtPlotItem.Rtti_PlotGrid
    
    def enableX(self, on):
        """
        Enable or disable vertical grid lines
        
        :param bool on: Enable (true) or disable
        
        .. seealso::
        
            :py:meth:`enableXMin()`
        """
        if self.__data.xEnabled != on:
            self.__data.xEnabled = on
            self.legendChanged()
            self.itemChanged()
    
    def enableY(self, on):
        """
        Enable or disable horizontal grid lines
        
        :param bool on: Enable (true) or disable
        
        .. seealso::
        
            :py:meth:`enableYMin()`
        """
        if self.__data.yEnabled != on:
            self.__data.yEnabled = on
            self.legendChanged()
            self.itemChanged()
    
    def enableXMin(self, on):
        """
        Enable or disable  minor vertical grid lines.
        
        :param bool on: Enable (true) or disable
        
        .. seealso::
        
            :py:meth:`enableX()`
        """
        if self.__data.xMinEnabled != on:
            self.__data.xMinEnabled = on
            self.legendChanged()
            self.itemChanged()
    
    def enableYMin(self, on):
        """
        Enable or disable  minor horizontal grid lines.
        
        :param bool on: Enable (true) or disable
        
        .. seealso::
        
            :py:meth:`enableY()`
        """
        if self.__data.yMinEnabled != on:
            self.__data.yMinEnabled = on
            self.legendChanged()
            self.itemChanged()

    def setXDiv(self, scaleDiv):
        """
        Assign an x axis scale division
        
        :param qwt.scale_div.QwtScaleDiv scaleDiv: Scale division
        """
        if self.__data.xScaleDiv != scaleDiv:
            self.__data.xScaleDiv = scaleDiv
            self.itemChanged()

    def setYDiv(self, scaleDiv):
        """
        Assign an y axis scale division
        
        :param qwt.scale_div.QwtScaleDiv scaleDiv: Scale division
        """
        if self.__data.yScaleDiv != scaleDiv:
            self.__data.yScaleDiv = scaleDiv
            self.itemChanged()

    def setPen(self, *args):
        """
        Build and/or assign a pen for both major and minor grid lines
        
        .. py:method:: setPen(color, width, style)
        
            Build and assign a pen for both major and minor grid lines
    
            In Qt5 the default pen width is 1.0 ( 0.0 in Qt4 ) what makes it
            non cosmetic (see `QPen.isCosmetic()`). This method signature has 
            been introduced to hide this incompatibility.
            
            :param QColor color: Pen color
            :param float width: Pen width
            :param Qt.PenStyle style: Pen style
        
        .. py:method:: setPen(pen)
        
            Assign a pen for both major and minor grid lines
    
            :param QPen pen: New pen
        
        .. seealso::
        
            :py:meth:`pen()`, :py:meth:`brush()`
        """
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
        """
        Build and/or assign a pen for both major grid lines
        
        .. py:method:: setMajorPen(color, width, style)
        
            Build and assign a pen for both major grid lines
    
            In Qt5 the default pen width is 1.0 ( 0.0 in Qt4 ) what makes it
            non cosmetic (see `QPen.isCosmetic()`). This method signature has 
            been introduced to hide this incompatibility.
            
            :param QColor color: Pen color
            :param float width: Pen width
            :param Qt.PenStyle style: Pen style
        
        .. py:method:: setMajorPen(pen)
        
            Assign a pen for the major grid lines
    
            :param QPen pen: New pen
        
        .. seealso::
        
            :py:meth:`majorPen()`, :py:meth:`setMinorPen()`, 
            :py:meth:`setPen()`, :py:meth:`pen()`, :py:meth:`brush()`
        """
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
        """
        Build and/or assign a pen for both minor grid lines
        
        .. py:method:: setMinorPen(color, width, style)
        
            Build and assign a pen for both minor grid lines
    
            In Qt5 the default pen width is 1.0 ( 0.0 in Qt4 ) what makes it
            non cosmetic (see `QPen.isCosmetic()`). This method signature has 
            been introduced to hide this incompatibility.
            
            :param QColor color: Pen color
            :param float width: Pen width
            :param Qt.PenStyle style: Pen style
        
        .. py:method:: setMinorPen(pen)
        
            Assign a pen for the minor grid lines
    
            :param QPen pen: New pen
        
        .. seealso::
        
            :py:meth:`minorPen()`, :py:meth:`setMajorPen()`, 
            :py:meth:`setPen()`, :py:meth:`pen()`, :py:meth:`brush()`
        """
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
        """
        Draw the grid

        The grid is drawn into the bounding rectangle such that
        grid lines begin and end at the rectangle's borders. The X and Y
        maps are used to map the scale divisions into the drawing region
        screen.

        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: X axis map
        :param qwt.scale_map.QwtScaleMap yMap: Y axis
        :param QRectF canvasRect: Contents rectangle of the plot canvas
        """
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
        for val in values:
            value = scaleMap.transform(val)
            if orientation == Qt.Horizontal:
                if qwtFuzzyGreaterOrEqual(value, y1) and\
                   qwtFuzzyLessOrEqual(value, y2):
                    painter.drawLine(x1, value, x2, value)
            else:
                if qwtFuzzyGreaterOrEqual(value, x1) and\
                   qwtFuzzyLessOrEqual(value, x2):
                    painter.drawLine(value, y1, value, y2)
    
    def majorPen(self):
        """
        :return: the pen for the major grid lines
        
        .. seealso::
        
            :py:meth:`setMajorPen()`, :py:meth:`setMinorPen()`, 
            :py:meth:`setPen()`
        """
        return self.__data.majorPen
    
    def minorPen(self):
        """
        :return: the pen for the minor grid lines
        
        .. seealso::
        
            :py:meth:`setMinorPen()`, :py:meth:`setMajorPen()`, 
            :py:meth:`setPen()`
        """
        return self.__data.minorPen
    
    def xEnabled(self):
        """
        :return: True if vertical grid lines are enabled
        
        .. seealso::
        
            :py:meth:`enableX()`
        """
        return self.__data.xEnabled
    
    def yEnabled(self):
        """
        :return: True if horizontal grid lines are enabled
        
        .. seealso::
        
            :py:meth:`enableY()`
        """
        return self.__data.yEnabled
    
    def xMinEnabled(self):
        """
        :return: True if minor vertical grid lines are enabled
        
        .. seealso::
        
            :py:meth:`enableXMin()`
        """
        return self.__data.xMinEnabled
    
    def yMinEnabled(self):
        """
        :return: True if minor horizontal grid lines are enabled
        
        .. seealso::
        
            :py:meth:`enableYMin()`
        """
        return self.__data.yMinEnabled
    
    def xScaleDiv(self):
        """
        :return: the scale division of the x axis
        """
        return self.__data.xScaleDiv
    
    def yScaleDiv(self):
        """
        :return: the scale division of the y axis
        """
        return self.__data.yScaleDiv
    
    def updateScaleDiv(self, xScaleDiv, yScaleDiv):
        """
        Update the grid to changes of the axes scale division
        
        :param qwt.scale_map.QwtScaleMap xMap: Scale division of the x-axis
        :param qwt.scale_map.QwtScaleMap yMap: Scale division of the y-axis
        
        .. seealso::
        
            :py:meth:`updateAxes()`
        """
        self.setXDiv(xScaleDiv)
        self.setYDiv(yScaleDiv)
        