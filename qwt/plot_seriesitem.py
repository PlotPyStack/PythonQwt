# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtPlotSeriesItem
-----------------

.. autoclass:: QwtPlotSeriesItem
   :members:
"""

from qwt.plot import QwtPlotItem, QwtPlotItem_PrivateData
from qwt.text import QwtText

from qwt.qt.QtCore import Qt, QRectF


class QwtPlotSeriesItem_PrivateData(QwtPlotItem_PrivateData):
    def __init__(self):
        QwtPlotItem_PrivateData.__init__(self)
        self.orientation = Qt.Vertical


class QwtPlotSeriesItem(QwtPlotItem):
    """
    Base class for plot items representing a series of samples
    """
    def __init__(self, title):
        if not isinstance(title, QwtText):
            title = QwtText(title)
        QwtPlotItem.__init__(self, title)
        self.__data = QwtPlotSeriesItem_PrivateData()
        
    def setOrientation(self, orientation):
        """
        Set the orientation of the item.

        The `orientation()` might be used in specific way by a plot item.
        F.e. a QwtPlotCurve uses it to identify how to display the curve
        int `QwtPlotCurve.Steps` or `QwtPlotCurve.Sticks` style.

        .. seealso::
        
            :py:meth`orientation()`
        """
        if self.__data.orientation != orientation:
            self.__data.orientation = orientation
            self.legendChanged()
            self.itemChanged()
    
    def orientation(self):
        """
        :return: Orientation of the plot item

        .. seealso::
        
            :py:meth`setOrientation()`
        """
        return self.__data.orientation
    
    def draw(self, painter, xMap, yMap, canvasRect):
        """
        Draw the complete series

        :param QPainter painter: Painter
        :param qwt.scale_map.QwtScaleMap xMap: Maps x-values into pixel coordinates.
        :param qwt.scale_map.QwtScaleMap yMap: Maps y-values into pixel coordinates.
        :param QRectF canvasRect: Contents rectangle of the canvas
        """
        self.drawSeries(painter, xMap, yMap, canvasRect, 0, -1)
    
    def boundingRect(self):
        return self.dataRect()
    
    def updateScaleDiv(self, xScaleDiv, yScaleDiv):
        rect = QRectF(xScaleDiv.lowerBound(), yScaleDiv.lowerBound(),
                      xScaleDiv.range(), yScaleDiv.range())
        self.setRectOfInterest(rect)
        
    def dataChanged(self):
        self.itemChanged()
