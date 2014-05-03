# -*- coding: utf-8 -*-

from qwt.qwt_series_data import QwtSeriesData, qwtBoundingRect
from qwt.qwt_interval import QwtInterval

from qwt.qt.QtCore import QPointF, QRectF


class QwtPointArrayData(QwtSeriesData):
    def __init__(self, x, y, size=None):
        QwtSeriesData.__init__(self)
        self.__x = x
        self.__y = y
        
    def boundingRect(self):
        if self.__boundingRect.width() < 0:
            self.__boundingRect = qwtBoundingRect(self)
        return self.__boundingRect
    
    def size(self):
        return min([self.__x.size, self.__y.size])
    
    def sample(self, index):
        return QPointF(self.__x[index], self.__y[index])
    
    def xData(self):
        return self.__x
        
    def yData(self):
        return self.__y
    

class QwtCPointerData(QwtSeriesData):
    def __init__(self, x, y, size):
        QwtSeriesData.__init__(self)
        self.__x = x
        self.__y = y
        self.__size = size
    
    def boundingRect(self):
        if self.__boundingRect.width() < 0:
            self.__boundingRect = qwtBoundingRect(self)
        return self.__boundingRect
    
    def size(self):
        return self.__size
    
    def sample(self, index):
        return QPointF(self.__x[index], self.__y[index])
    
    def xData(self):
        return self.__x
    
    def yData(self):
        return self.__y
    

class QwtSyntheticPointData(QwtSeriesData):
    def __init__(self, size, interval):
        QwtSeriesData.__init__(self)
        self.__size = size
        self.__interval = interval
        self.__rectOfInterest = None
        self.__intervalOfInterest = None
    
    def setSize(self, size):
        self.__size = size
    
    def size(self):
        return self.__size
    
    def setInterval(self, interval):
        self.__interval = interval.normalized()
    
    def interval(self):
        return self.__interval
    
    def setRectOfInterest(self, rect):
        self.__rectOfInterest = rect
        self.__intervalOfInterest = QwtInterval(rect.left(), rect.right()
                                                ).normalized()
    
    def rectOfInterest(self):
        return self.__rectOfInterest
    
    def boundingRect(self):
        if self.__size == 0 or\
           not (self.__interval.isValid() or self.__intervalOfInterest.isValid()):
            return QRectF(1.0, 1.0, -2.0, -2.0)
        return qwtBoundingRect(self)
    
    def sample(self, index):
        if index >= self.__size:
            return QPointF(0, 0)
        xValue = self.x(index)
        yValue = self.y(xValue)
        return QPointF(xValue, yValue)
    
    def x(self, index):
        if self.__interval.isValid():
            interval = self.__interval
        else:
            interval = self.__intervalOfInterest
        if not interval.isValid() or self.__size == 0 or index >= self.__size:
            return 0.
        dx = interval.width()/self.__size
        return interval.minValue() + index*dx
    