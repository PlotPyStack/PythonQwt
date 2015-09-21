# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

#XXX: Unfinished (and not imported elsewhere) translation of QwtClipper class

from qwt.qt.QtGui import QPolygon, QPolygonF
from qwt.qt.QtCore import QRect, QRectF

import numpy as np


class LeftEdge(object):
    def __init__(self, x1, x2, y1, y2):
        self.__x1 = x1
    
    def isInside(self, p):
        return p.x() >= self.__x1
    
    def intersection(self, p1, p2):
        dy = (p1.y()-p2.y())/(p1.x()-p2.x())
        return Point(self.__x1, (p2.y() + (self.__x1 - p2.x())*dy))

class RightEdge(object):
    def __init__(self, x1, x2, y1, y2):
        self.__x2 = x2
    
    def isInside(self, p):
        return p.x() <= self.__x2
    
    def intersection(self, p1, p2):
        dy = (p1.y()-p2.y())/(p1.x()-p2.x())
        return Point(self.__x2, (p2.y() + (self.__x2 - p2.x())*dy))

class TopEdge(object):
    def __init__(self, x1, x2, y1, y2):
        self.__y1 = y1
    
    def isInside(self, p):
        return p.y() >= self.__y1
    
    def intersection(self, p1, p2):
        dx = (p1.x()-p2.x())/(p1.y()-p2.y())
        return Point((p2.x() + (self.__y1 - p2.y())*dx), self.__y1)

class BottomEdge(object):
    def __init__(self, x1, x2, y1, y2):
        self.__y2 = y2
    
    def isInside(self, p):
        return p.y() <= self.__y2
    
    def intersection(self, p1, p2):
        dx = (p1.x()-p2.x())/(p1.y()-p2.y())
        return Point((p2.x() + (self.__y2 - p2.y())*dx), self.__y2)

class PointBuffer(object):
    def __init__(self, capacity=0):
        self.m_capacity = capacity
        self.m_size = 0
        self.m_buffer = None
        if capacity > 0:
            self.reserve(capacity)
    
    def setPoints(self, numPoints, points):
        self.reserve(numPoints)
        self.m_size = numPoints
    
    def reset(self):
        self.m_size = 0
    
    def size(self):
        return self.m_size
    
    def data(self):
        return self.m_buffer
    
    def operator(self, i):
        return self.m_buffer[i]


class QwtPolygonClipper(object):
    def __init__(self, clipRect):
        self.__clipRect = clipRect
    
    def clipPolygon(self, polygon, closePolygon):
        if self.__clipRect.contains(polygon.boundingRect()):
            return polygon
        


class QwtClipper(object):
    def __init__(self):
        pass
    
    def clipPolygon(self, clipRect, polygon, closePolygon):
        raise NotImplementedError("Nearly impossible to implement in pure Python")
        #XXX: the only viable option would be to use Qt's intersected method 
        # but unfortunately it's closing systematically the output polygon
        # (how to test it: polygon.intersected(QPolygonF(clipRect)))
        
        if isinstance(clipRect, QRectF):
            minX = np.ceil(clipRect.left())
            maxX = np.floor(clipRect.right())
            minY = np.ceil(clipRect.top())
            maxY = np.floor(clipRect.bottom())
            clipRect = QRect(minX, minY, maxX-minX, maxY-minY)
        clipper = QwtPolygonClipper(clipRect)
        return clipper.clipPolygon(polygon, closePolygon)
    
    def clipPolygonF(self, clipRect, polygon, closePolygon):
        raise NotImplementedError("Nearly impossible to implement in pure Python")
        #XXX: the only viable option would be to use Qt's intersected method 
        # but unfortunately it's closing systematically the output polygon
        # (how to test it: polygon.intersected(QPolygonF(clipRect)))
        
        if isinstance(clipRect, QRect):
            clipRect = QRectF(clipRect)
        clipper = QwtPolygonClipper(clipRect)
        return clipper.clipPolygon(polygon, closePolygon)
