# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtPointMapper
--------------

.. autoclass:: QwtPointMapper
   :members:
"""

from qwt.qt.QtGui import QPolygon, QPolygonF, QImage, QPainter
from qwt.qt.QtCore import Qt, QPoint, QPointF, QRectF

#from qwt.pixel_matrix import QwtPixelMatrix

import numpy as np


def qwtNoRoundF(data):
    return data

def qwtRoundF(data):
    return np.rint(data)

def qwtRoundI(data):
    return np.array(np.rint(data), dtype=np.int)


def qwtToPoints(boundingRect, xMap, yMap, series, from_, to, round_,
                Polygon):
    """
    Mapping points without any filtering
    - beside checking the bounding rectangle
    """
    Point = QPointF if Polygon is QPolygonF else QPoint
    polygon = qwtToPolylineFiltered(xMap, yMap, series, from_, to, round_,
                                    Polygon, Point)
    return polygon
#    # Pure Python implementation (catastophic performance)
#    Point = QPointF if Polygon is QPolygonF else QPoint
#    points = []
#    if boundingRect.isValid():
#        for i in range(from_, to+1):
#            sample = series.sample(i)
#            x = xMap.transform(sample.x())
#            y = yMap.transform(sample.y())
#            if boundingRect.contains(x, y):
#                points.append(Point(round_(x), round_(y)))
#    else:
#        for i in range(from_, to+1):
#            sample = series.sample(i)
#            x = xMap.transform(sample.x())
#            y = yMap.transform(sample.y())
#            points.append(Point(round_(x), round_(y)))
#    return Polygon(list(set(points)))

def qwtToPointsI(boundingRect, xMap, yMap, series, from_, to):
    return qwtToPoints(boundingRect, xMap, yMap, series, from_, to,
                       qwtNoRoundF, QPolygon)

def qwtToPointsF(boundingRect, xMap, yMap, series, from_, to, round_):
    return qwtToPoints(boundingRect, xMap, yMap, series, from_, to, round_,
                       QPolygonF)


def qwtToPolylineFiltered(xMap, yMap, series, from_, to, round_,
                          Polygon, Point):
    """
    Mapping points with filtering out consecutive
    points mapped to the same position
    
    .. warning::
    
        Filtering is currently not implemented
    """
    polyline = Polygon(to-from_+1)
    pointer = polyline.data()
    if Polygon is QPolygonF:
        dtype, tinfo = np.float, np.finfo
    else:
        dtype, tinfo = np.int, np.iinfo
    pointer.setsize(2*polyline.size()*tinfo(dtype).dtype.itemsize)
    memory = np.frombuffer(pointer, dtype)
    memory[:(to-from_)*2+1:2] =\
                        round_(xMap.transform(series.xData()))[from_:to+1]
    memory[1:(to-from_)*2+2:2] =\
                        round_(yMap.transform(series.yData()))[from_:to+1]
    return polyline    
#    # Pure Python implementation (catastophic performance)
#    points = polyline.data()
#    sample0 = series.sample(from_)
#    points[0].setX(round_(xMap.transform(sample0.x())))
#    points[0].setY(round_(yMap.transform(sample0.y())))
#    pos = 0
#    for i in range(from_, to+1):
#        sample = series.sample(i)
#        p = Point(round_(xMap.transform(sample.x())),
#                  round_(yMap.transform(sample.y())))
#        if points[pos] != p:
#            pos += 1
#            points[pos] = p
#    polyline.resize(pos+1)
#    return polyline

def qwtToPolylineFilteredI(xMap, yMap, series, from_, to):
    return qwtToPolylineFiltered(xMap, yMap, series, from_, to, qwtRoundI,
                                 QPolygon, QPoint)

def qwtToPolylineFilteredF(xMap, yMap, series, from_, to, round_):
    return qwtToPolylineFiltered(xMap, yMap, series, from_, to, round_,
                                 QPolygonF, QPointF)


def qwtToPointsFiltered(boundingRect, xMap, yMap, series, from_, to,
                        Polygon):
    Point = QPointF if isinstance(Polygon, QPolygonF) else QPoint
    return qwtToPolylineFiltered(xMap, yMap, series, from_, to, qwtRoundI,
                                 Polygon, Point)
#    # Pure Python implementation (catastophic performance)
#    Point = QPointF if Polygon is QPolygonF else QPoint
#    if isinstance(boundingRect, QRectF):
#        pixelMatrix = QwtPixelMatrix(boundingRect.toAlignedRect())
#    else:
#        pixelMatrix = QwtPixelMatrix(boundingRect)
#    points = []
#    for i in range(from_, to+1):
#        sample = series.sample(i)
#        x = int(round(xMap.transform(sample.x())))
#        y = int(round(yMap.transform(sample.y())))
#        if pixelMatrix.testAndSetPixel(x, y, True) == False:
#            points.append(Point(x, y))
#    return Polygon(list(points))

def qwtToPointsFilteredI(boundingRect, xMap, yMap, series, from_, to):
    return qwtToPointsFiltered(boundingRect, xMap, yMap, series, from_, to,
                               QPolygon)

def qwtToPointsFilteredF(boundingRect, xMap, yMap, series, from_, to):
    return qwtToPointsFiltered(boundingRect, xMap, yMap, series, from_, to,
                               QPolygonF)


class QwtPointMapper_PrivateData(object):
    def __init__(self):
        self.boundingRect = None
        self.flags = 0


class QwtPointMapper(object):
    """
    A helper class for translating a series of points

    `QwtPointMapper` is a collection of methods and optimizations
    for translating a series of points into paint device coordinates. 
    It is used by `QwtPlotCurve` but might also be useful for 
    similar plot items displaying a `QwtSeriesData`.
    
    Transformation flags:
    
      * `QwtPointMapper.RoundPoints`: Round points to integer values
      * `QwtPointMapper.WeedOutPoints`: Try to remove points, that are translated to the same position
    """
    
    RoundPoints = 0x01
    WeedOutPoints = 0x02
    
    def __init__(self):
        self.__data = QwtPointMapper_PrivateData()
        self.qwtInvalidRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.setBoundingRect(self.qwtInvalidRect)
        
    def setFlags(self, flags):
        """
        Set the flags affecting the transformation process

        :param flags: Flags
        
        .. seealso::
        
            :py:meth:`flags()`, :py:meth:`setFlag()`
        """
        self.__data.flags = flags
    
    def flags(self):
        """
        :return: Flags affecting the transformation process
        
        .. seealso::
        
            :py:meth:`setFlags()`, :py:meth:`setFlag()`
        """
        return self.__data.flags
    
    def setFlag(self, flag, on=True):
        """
        Modify a flag affecting the transformation process

        :param flag: Flag type
        
        .. seealso::
        
            :py:meth:`flag()`, :py:meth:`setFlags()`
        """
        if on:
            self.__data.flags |= flag
        else:
            self.__data.flags &= ~flag
    
    def testFlag(self, flag):
        """
        :param int flag: Flag type
        :return: True, when the flag is set
        
        .. seealso::
        
            :py:meth:`setFlags()`, :py:meth:`setFlag()`
        """
        return self.__data.flags & flag
    
    def setBoundingRect(self, rect):
        """
        Set a bounding rectangle for the point mapping algorithm

        A valid bounding rectangle can be used for optimizations
        
        :param QRectF rect: Bounding rectangle
        
        .. seealso::
        
            :py:meth:`boundingRect()`
        """
        self.__data.boundingRect = rect
        
    def boundingRect(self):
        """
        :return: Bounding rectangle
        
        .. seealso::
        
            :py:meth:`setBoundingRect()`
        """
        return self.__data.boundingRect
    
    def toPolygonF(self, xMap, yMap, series, from_, to):
        """
        Translate a series of points into a QPolygonF

        When the WeedOutPoints flag is enabled consecutive points,
        that are mapped to the same position will be one point. 
        
        When RoundPoints is set all points are rounded to integers
        but returned as PolygonF - what only makes sense
        when the further processing of the values need a QPolygonF.
        
        :param qwt.scale_map.QwtScaleMap xMap: x map
        :param qwt.scale_map.QwtScaleMap yMap: y map
        :param series: Series of points to be mapped
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted
        :return: Translated polygon
        """
        if self.__data.flags & QwtPointMapper.WeedOutPoints:
            if self.__data.flags & QwtPointMapper.RoundPoints:
                polyline = qwtToPolylineFilteredF(xMap, yMap, series,
                                                  from_, to, qwtRoundF)
            else:
                polyline = qwtToPolylineFilteredF(xMap, yMap, series,
                                                  from_, to, qwtNoRoundF)
        else:
            if self.__data.flags & QwtPointMapper.RoundPoints:
                polyline = qwtToPointsF(self.qwtInvalidRect, xMap, yMap,
                                        series, from_, to, qwtRoundF)
            else:
                polyline = qwtToPointsF(self.qwtInvalidRect, xMap, yMap,
                                        series, from_, to, qwtNoRoundF)
        return polyline
    
    def toPolygon(self, xMap, yMap, series, from_, to):
        """
        Translate a series of points into a QPolygon

        When the WeedOutPoints flag is enabled consecutive points,
        that are mapped to the same position will be one point. 
        
        :param qwt.scale_map.QwtScaleMap xMap: x map
        :param qwt.scale_map.QwtScaleMap yMap: y map
        :param series: Series of points to be mapped
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted
        :return: Translated polygon
        """
        if self.__data.flags & QwtPointMapper.WeedOutPoints:
            polyline = qwtToPolylineFilteredI(xMap, yMap, series, from_, to)
        else:
            polyline = qwtToPointsI(self.qwtInvalidRect, xMap, yMap,
                                    series, from_, to)
        return polyline
    
    def toPointsF(self, xMap, yMap, series, from_, to):
        """
        Translate a series of points into a QPolygonF:

          - `WeedOutPoints and RoundPoints and boundingRect().isValid()`:
        
            All points that are mapped to the same position 
            will be one point. Points outside of the bounding
            rectangle are ignored.
         
          - `WeedOutPoints and RoundPoints and not boundingRect().isValid()`:
        
            All consecutive points that are mapped to the same position 
            will one point
        
          - `WeedOutPoints and not RoundPoints`:
        
            All consecutive points that are mapped to the same position 
            will one point
        
          - `not WeedOutPoints and boundingRect().isValid()`:
         
            Points outside of the bounding rectangle are ignored.

        When RoundPoints is set all points are rounded to integers
        but returned as PolygonF - what only makes sense
        when the further processing of the values need a QPolygonF.
        
        :param qwt.scale_map.QwtScaleMap xMap: x map
        :param qwt.scale_map.QwtScaleMap yMap: y map
        :param series: Series of points to be mapped
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted
        :return: Translated polygon
        """
        if self.__data.flags & QwtPointMapper.WeedOutPoints:
            if self.__data.flags & QwtPointMapper.RoundPoints:
                if self.__data.boundingRect.isValid():
                    points = qwtToPointsFilteredF(self.__data.boundingRect,
                                              xMap, yMap, series, from_, to)
                else:
                    points = qwtToPolylineFilteredF(xMap, yMap, series,
                                                    from_, to, qwtRoundF)
            else:
                points = qwtToPolylineFilteredF(xMap, yMap, series,
                                                from_, to, qwtNoRoundF)
        else:
            if self.__data.flags & QwtPointMapper.RoundPoints:
                points = qwtToPointsF(self.__data.boundingRect,
                                  xMap, yMap, series, from_, to, qwtRoundF)
            else:
                points = qwtToPointsF(self.__data.boundingRect,
                                  xMap, yMap, series, from_, to, qwtNoRoundF)
        return points

    def toPoints(self, xMap, yMap, series, from_, to):
        """
        Translate a series of points into a QPolygon:

          - `WeedOutPoints and boundingRect().isValid()`:
        
            All points that are mapped to the same position 
            will be one point. Points outside of the bounding
            rectangle are ignored.
         
          - `WeedOutPoints and not boundingRect().isValid()`:
        
            All consecutive points that are mapped to the same position 
            will one point
        
          - `not WeedOutPoints and boundingRect().isValid()`:
         
            Points outside of the bounding rectangle are ignored.
        
        :param qwt.scale_map.QwtScaleMap xMap: x map
        :param qwt.scale_map.QwtScaleMap yMap: y map
        :param series: Series of points to be mapped
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted
        :return: Translated polygon
        """
        if self.__data.flags & QwtPointMapper.WeedOutPoints:
            if self.__data.boundingRect.isValid():
                points = qwtToPointsFilteredI(self.__data.boundingRect,
                                              xMap, yMap, series, from_, to)
            else:
                points = qwtToPolylineFilteredI(xMap, yMap, series, from_, to)
        else:
            points = qwtToPointsI(self.__data.boundingRect, xMap, yMap,
                                  series, from_, to)
        return points
    
    def toImage(self, xMap, yMap, series, from_, to, pen, antialiased):
        """
        Translate a series into a QImage
        
        :param qwt.scale_map.QwtScaleMap xMap: x map
        :param qwt.scale_map.QwtScaleMap yMap: y map
        :param series: Series of points to be mapped
        :param int from_: Index of the first point to be painted
        :param int to: Index of the last point to be painted
        :param QPen pen: Pen used for drawing a point of the image, where a point is mapped to
        :param bool antialiased: True, when the dots should be displayed antialiased
        :return: Image displaying the series
        """
        #TODO: rewrite this method to fix performance issue (litteral translation from C++!)
        rect = self.__data.boundingRect.toAlignedRect()
        image = QImage(rect.size(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        if pen.width() <= 1 and pen.color().alpha() == 255:
            bits = image.bits()
            w = image.width()
            h = image.height()
            x0 = rect.topLeft().x()
            y0 = rect.topLeft().y()
            for i in range(from_, to+1):
                sample = series.sample(i)
                x = int(xMap.transform(sample.x())+0.5)-x0
                y = int(yMap.transform(sample.y())+0.5)-y0
                if x >= 0 and x < w and y >= 0 and y < h:
                    bits[y*w+x] = pen.color().rgba()
        else:
            painter = QPainter(image)
            painter.setPen(pen)
            painter.setRenderHint(QPainter.Antialiasing, antialiased)
            chunkSize = 1000
            for i in range(chunkSize):
                indexTo = min([i+chunkSize-1, to])
                points = self.toPoints(xMap, yMap, series, i, indexTo)
                painter.drawPoints(points)
        return image
