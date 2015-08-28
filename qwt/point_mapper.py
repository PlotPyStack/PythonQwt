# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

USE_THREADS = False  # QtConcurrent is not supported by PyQt

from qwt.qt.QtGui import QPolygon, QPolygonF, QImage, QPainter
from qwt.qt.QtCore import QThread, Qt, QPoint, QPointF, QRectF

from qwt.pixel_matrix import QwtPixelMatrix

import numpy as np


class QwtDotsCommand(object):
    def __init__(self):
        self.series = None
        self.from_ = None
        self.to = None
        self.rgb = None

def qwtRenderDots(xMap, yMap, command, pos, image):
    rgb = command.rgb
    bits = image.bits()
    w = image.width()
    h = image.height()
    x0 = pos.x()
    y0 = pos.y()
    for i in range(command.from_, command.to+1):
        sample = command.series.sample(i)
        x = int(xMap.transform(sample.x())+0.5)-x0
        y = int(yMap.transform(sample.y())+0.5)-y0
        if x >= 0 and x < w and y >= 0 and y < h:
            bits[y*w+x] = rgb


def qwtToPoints(boundingRect, xMap, yMap, series, from_, to, round_,
                Polygon):
    Point = QPointF if isinstance(Polygon, QPolygonF) else QPoint
    points = []
    if boundingRect.isValid():
        for i in range(from_, to+1):
            sample = series.sample(i)
            x = xMap.transform(sample.x())
            y = yMap.transform(sample.y())
            if boundingRect.contains(x, y):
                points.append(Point(round_(x), round_(y)))
    else:
        for i in range(from_, to+1):
            sample = series.sample(i)
            x = xMap.transform(sample.x())
            y = yMap.transform(sample.y())
            points.append(Point(round_(x), round_(y)))
    return Polygon(list(set(points)))

def qwtToPointsI(boundingRect, xMap, yMap, series, from_, to):
    return qwtToPoints(boundingRect, xMap, yMap, series, from_, to, round,
                       QPolygon)

def qwtToPointsF(boundingRect, xMap, yMap, series, from_, to, round_):
    return qwtToPoints(boundingRect, xMap, yMap, series, from_, to, round_,
                       QPolygonF)


def qwtToPolylineFiltered(xMap, yMap, series, from_, to, round_,
                          Polygon, Point):
    polyline = Polygon(to-from_+1)
    pointer = polyline.data()
    dtype = np.float if Polygon is QPolygonF else np.int
    pointer.setsize(2*polyline.size()*np.finfo(dtype).dtype.itemsize)
    memory = np.frombuffer(pointer, dtype)
    memory[from_*2:to*2+1:2] =\
                        np.round(xMap.transform(series.xData()))[from_:to+1]
    memory[from_*2+1:to*2+2:2] =\
                        np.round(yMap.transform(series.yData()))[from_:to+1]
    return polyline    
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
    return qwtToPolylineFiltered(xMap, yMap, series, from_, to, round,
                                 QPolygon, QPoint)

def qwtToPolylineFilteredF(xMap, yMap, series, from_, to, round_):
    return qwtToPolylineFiltered(xMap, yMap, series, from_, to, round_,
                                 QPolygonF, QPointF)


def qwtToPointsFiltered(boundingRect, xMap, yMap, series, from_, to,
                        Polygon):
    Point = QPointF if isinstance(Polygon, QPolygonF) else QPoint
    if isinstance(boundingRect, QRectF):
        pixelMatrix = QwtPixelMatrix(boundingRect.toAlignedRect())
    else:
        pixelMatrix = QwtPixelMatrix(boundingRect)
    points = []
    for i in range(from_, to+1):
        sample = series.sample(i)
        x = int(round(xMap.transform(sample.x())))
        y = int(round(yMap.transform(sample.y())))
        if pixelMatrix.testAndSetPixel(x, y, True) == False:
            points.append(Point(x, y))
    return Polygon(list(points))

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
    RoundPoints = 0x01
    WeedOutPoints = 0x02
    
    def __init__(self):
        self.__data = QwtPointMapper_PrivateData()
        self.qwtInvalidRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.setBoundingRect(self.qwtInvalidRect)
        
    def setFlags(self, flags):
        self.__data.flags = flags
    
    def flags(self):
        return self.__data.flags
    
    def setFlag(self, flag, on=True):
        if on:
            self.__data.flags |= flag
        else:
            self.__data.flags &= ~flag
    
    def testFlag(self, flag):
        return self.__data.flags & flag
    
    def setBoundingRect(self, rect):
        self.__data.boundingRect = rect
        
    def boundingRect(self):
        return self.__data.boundingRect
    
    def toPolygonF(self, xMap, yMap, series, from_, to):
        round_ = round
        no_round = lambda x: x
        if self.__data.flags & QwtPointMapper.WeedOutPoints:
            if self.__data.flags & QwtPointMapper.RoundPoints:
                polyline = qwtToPolylineFilteredF(xMap, yMap, series,
                                                  from_, to, round_)
            else:
                polyline = qwtToPolylineFilteredF(xMap, yMap, series,
                                                  from_, to, no_round)
        else:
            if self.__data.flags & QwtPointMapper.RoundPoints:
                polyline = qwtToPointsF(self.qwtInvalidRect, xMap, yMap,
                                        series, from_, to, round_)
            else:
                polyline = qwtToPointsF(self.qwtInvalidRect, xMap, yMap,
                                        series, from_, to, no_round)
        return polyline
    
    def toPolygon(self, xMap, yMap, series, from_, to):
        if self.__data.flags & QwtPointMapper.WeedOutPoints:
            polyline = qwtToPolylineFilteredI(xMap, yMap, series, from_, to)
        else:
            polyline = qwtToPointsI(self.qwtInvalidRect, xMap, yMap,
                                    series, from_, to)
        return polyline
    
    def toPointsF(self, xMap, yMap, series, from_, to):
        round_ = round
        no_round = lambda x: x
        if self.__data.flags & QwtPointMapper.WeedOutPoints:
            if self.__data.flags & QwtPointMapper.RoundPoints:
                if self.__data.boundingRect.isValid():
                    points = qwtToPointsFilteredF(self.__data.boundingRect,
                                              xMap, yMap, series, from_, to)
                else:
                    points = qwtToPolylineFilteredF(xMap, yMap, series,
                                                    from_, to, round_)
            else:
                points = qwtToPolylineFilteredF(xMap, yMap, series,
                                                from_, to, no_round)
        else:
            if self.__data.flags & QwtPointMapper.RoundPoints:
                points = qwtToPointsF(self.__data.boundingRect,
                                      xMap, yMap, series, from_, to, round_)
            else:
                points = qwtToPointsF(self.__data.boundingRect,
                                      xMap, yMap, series, from_, to, no_round)
        return points

    def toPoints(self, xMap, yMap, series, from_, to):
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
    
    def toImage(self, xMap, yMap, series, from_, to, pen, antialiased,
                numThreads):
        if USE_THREADS:
            if numThreads == 0:
                numThreads = QThread.idealThreadCount()
            if numThreads <= 0:
                numThreads = 1
        rect = self.__data.boundingRect.toAlignedRect()
        image = QImage(rect.size(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        if pen.width() <= 1 and pen.color().alpha() == 255:
            command = QwtDotsCommand()
            command.series = series
            command.rgb = pen.color().rgba()
            if USE_THREADS:
                numPoints = int((to-from_+1)/numThreads)
                futures = []
                for i in range(numThreads):
                    pos = rect.topLeft()
                    index0 = from_ + i*numPoints
                    if i == numThreads-1:
                        command.from_ = index0
                        command.to = to
                        qwtRenderDots(xMap, yMap, command, pos, image)
                    else:
                        command.from_ = index0
                        command.to = index0 + numPoints - 1
                        futures += [QtConcurrent.run(qwtRenderDots,
                                            xMap, yMap, command, pos, image)]
                for future in futures:
                    future.waitForFinished()
            else:
                command.from_ = from_
                command.to = to
                qwtRenderDots(xMap, yMap, command, rect.topLeft(), image)
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
