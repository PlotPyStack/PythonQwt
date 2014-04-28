# -*- coding: utf-8 -*-

QWT_USE_THREADS = True

from qwt.qt.QtGui import (QPolygon, QPolygonF, QPoint, QPointF, QRectF, QImage,
                          QPainter)
from qwt.qt.QtCore import QThread, Qt, QtConcurrent

from qwt.qwt_pixel_matrix import QwtPixelMatrix


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
    polyline = Polygon(to-from_+1)
    points = polyline.data()
    numPoints = 0
    if boundingRect.isValid():
        for i in range(from_, to+1):
            sample = series.sample(i)
            x = xMap.transform(sample.x())
            y = yMap.transform(sample.y())
            if boundingRect.contains(x, y):
                points[numPoints].setX(round_(x))
                points[numPoints].setY(round_(y))
                numPoints += 1
        polyline.resize(numPoints)
    else:
        for i in range(from_, to+1):
            sample = series.sample(i)
            x = xMap.transform(sample.x())
            y = yMap.transform(sample.y())
            points[numPoints].setX(round_(x))
            points[numPoints].setY(round_(y))
            numPoints += 1
    return polyline

def qwtToPointsI(boundingRect, xMap, yMap, series, from_, to):
    return qwtToPoints(boundingRect, xMap, yMap, series, from_, to, round,
                       QPolygon)

def qwtToPointsF(boundingRect, xMap, yMap, series, from_, to, round_):
    return qwtToPoints(boundingRect, xMap, yMap, series, from_, to, round_,
                       QPolygonF)


def qwtToPolylineFiltered(xMap, yMap, series, from_, to, round_,
                          Polygon, Point):
    polyline = Polygon(to-from_+1)
    points = polyline.data()
    sample0 = series.sample(from_)
    points[0].setX(round_(xMap.transform(sample0.x())))
    points[0].setY(round_(yMap.transform(sample0.y())))
    pos = 0
    for i in range(from_, to+1):
        sample = series.sample(i)
        p = Point(round_(xMap.transform(sample.x())),
                  round_(yMap.transform(sample.y())))
        if points[pos] != p:
            pos += 1
            points[pos] = p
    polyline.resize(pos+1)
    return polyline

def qwtToPolylineFilteredI(xMap, yMap, series, from_, to):
    return qwtToPolylineFiltered(xMap, yMap, series, from_, to, round,
                                 QPolygon, QPoint)

def qwtToPolylineFilteredF(xMap, yMap, series, from_, to, round_):
    return qwtToPolylineFiltered(xMap, yMap, series, from_, to, round_,
                                 QPolygonF, QPointF)


def qwtToPointsFiltered(boundingRect, xMap, yMap, series, from_, to,
                        Polygon):
    polygon = Polygon(to-from_+1)
    points = polygon.data()
    pixelMatrix = QwtPixelMatrix(boundingRect.toAlignedRect())
    numPoints = 0
    for i in range(from_, to+1):
        sample = series.sample(i)
        x = round(xMap.transform(sample.x()))
        y = round(yMap.transform(sample.y()))
        if not pixelMatrix.testAndSetPixel(x, y, True):
            points[numPoints].setX(x)
            points[numPoints].setY(y)
            numPoints += 1
    polygon.resize(numPoints)
    return polygon

def qwtToPointsFilteredI(boundingRect, xMap, yMap, series, from_, to):
    return qwtToPointsFiltered(boundingRect, xMap, yMap, series, from_, to,
                               QPolygon)

def qwtToPointsFilteredF(boundingRect, xMap, yMap, series, from_, to):
    return qwtToPointsFiltered(boundingRect, xMap, yMap, series, from_, to,
                               QPolygonF)


class QwtPointMapper_PrivateData(object):
    def __init__(self):
        self.boundingRect = None
        self.flags = None


class QwtPointMapper(object):
    RoundPoints = 0x01
    WeedOutPoints = 0x02
    
    def __init__(self):
        self.d_data = QwtPointMapper_PrivateData()
        self.qwtInvalidRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.setBoundingRect(self.qwtInvalidRect)
        
    def setFlags(self, flags):
        self.d_data.flags = flags
    
    def flags(self):
        return self.d_data.flags
    
    def setFlag(self, flag, on):
        if on:
            self.d_data.flags |= flag
        else:
            self.d_data.flags &= not flag
    
    def testFlag(self, flag):
        return self.d_data.flags & flag
    
    def setBoundingRect(self, rect):
        self.d_data.boundingRect = rect
        
    def boundingRect(self):
        return self.d_data.boundingRect
    
    def toPolygonF(self, xMap, yMap, series, from_, to):
        round_ = round
        no_round = lambda x: x
        if self.d_data.flags & QwtPointMapper.WeedOutPoints:
            if self.d_data.flags & QwtPointMapper.RoundPoints:
                polyline = qwtToPolylineFilteredF(xMap, yMap, series,
                                                  from_, to, round_)
            else:
                polyline = qwtToPolylineFilteredF(xMap, yMap, series,
                                                  from_, to, no_round)
        else:
            if self.d_data.flags & QwtPointMapper.RoundPoints:
                polyline = qwtToPointsF(self.qwtInvalidRect, xMap, yMap,
                                        series, from_, to, round_)
            else:
                polyline = qwtToPointsF(self.qwtInvalidRect, xMap, yMap,
                                        series, from_, to, no_round)
        return polyline
    
    def toPolygon(self, xMap, yMap, series, from_, to):
        if self.d_data.flags & QwtPointMapper.WeedOutPoints:
            polyline = qwtToPolylineFilteredI(xMap, yMap, series, from_, to)
        else:
            polyline = qwtToPointsI(self.qwtInvalidRect, xMap, yMap,
                                    series, from_, to)
        return polyline
    
    def toPointsF(self, xMap, yMap, series, from_, to):
        round_ = round
        no_round = lambda x: x
        if self.d_data.flags & QwtPointMapper.WeedOutPoints:
            if self.d_data.flags & QwtPointMapper.RoundPoints:
                if self.d_data.boundingRect.isValid():
                    points = qwtToPointsFilteredF(self.d_data.boundingRect,
                                              xMap, yMap, series, from_, to)
                else:
                    points = qwtToPolylineFilteredF(xMap, yMap, series,
                                                    from_, to, round_)
            else:
                points = qwtToPolylineFilteredF(xMap, yMap, series,
                                                from_, to, no_round)
        else:
            if self.d_data.flags & QwtPointMapper.RoundPoints:
                points = qwtToPointsF(self.d_data.boundingRect,
                                      xMap, yMap, series, from_, to, round_)
            else:
                points = qwtToPointsF(self.d_data.boundingRect,
                                      xMap, yMap, series, from_, to, no_round)
        return points

    def toPoints(self, xMap, yMap, series, from_, to):
        if self.d_data.flags & QwtPointMapper.WeedOutPoints:
            if self.d_data.boundingRect.isValid():
                points = qwtToPointsFilteredI(self.d_data.boundingRect,
                                              xMap, yMap, series, from_, to)
            else:
                points = qwtToPolylineFilteredI(xMap, yMap, series, from_, to)
        else:
            points = qwtToPointsI(self.d_data.boundingRect, xMap, yMap,
                                  series, from_, to)
        return points
    
    def toImage(self, xMap, yMap, series, from_, to, pen, antialiased,
                numThreads):
        if QWT_USE_THREADS:
            if numThreads == 0:
                numThreads = QThread.idealThreadCount()
            if numThreads <= 0:
                numThreads = 1
        rect = self.d_data.boundingRect.toAlignedRect()
        image = QImage(rect.size(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        if pen.width() <= 1 and pen.color().alpha() == 255:
            command = QwtDotsCommand()
            command.series = series
            command.rgb = pen.color().rgba()
            if QWT_USE_THREADS:
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
