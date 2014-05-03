# -*- coding: utf-8 -*-

from qwt.qwt_series_data import QwtSeriesData, qwtBoundingRect
from qwt.qwt_interval import QwtInterval

from qwt.qt.QtCore import QPointF, QRectF


class QwtPointArrayData(QwtSeriesData):
    def __init__(self, x, y, size=None):
        QwtSeriesData.__init__(self)
        self.d_x = x
        self.d_y = y
        
    def boundingRect(self):
        if self.d_boundingRect.width() < 0:
            self.d_boundingRect = qwtBoundingRect(self)
        return self.d_boundingRect
    
    def size(self):
        return min([self.d_x.size, self.d_y.size])
    
    def sample(self, index):
        return QPointF(self.d_x[index], self.d_y[index])
    
    def xData(self):
        return self.d_x
        
    def yData(self):
        return self.d_y
    

class QwtCPointerData(QwtSeriesData):
    def __init__(self, x, y, size):
        QwtSeriesData.__init__(self)
        self.d_x = x
        self.d_y = y
        self.d_size = size
    
    def boundingRect(self):
        if self.d_boundingRect.width() < 0:
            self.d_boundingRect = qwtBoundingRect(self)
        return self.d_boundingRect
    
    def size(self):
        return self.d_size
    
    def sample(self, index):
        return QPointF(self.d_x[index], self.d_y[index])
    
    def xData(self):
        return self.d_x
    
    def yData(self):
        return self.d_y
    

class QwtSyntheticPointData(QwtSeriesData):
    def __init__(self, size, interval):
        QwtSeriesData.__init__(self)
        self.d_size = size
        self.d_interval = interval
        self.d_rectOfInterest = None
        self.d_intervalOfInterest = None
    
    def setSize(self, size):
        self.d_size = size
    
    def size(self):
        return self.d_size
    
    def setInterval(self, interval):
        self.d_interval = interval.normalized()
    
    def interval(self):
        return self.d_interval
    
    def setRectOfInterest(self, rect):
        self.d_rectOfInterest = rect
        self.d_intervalOfInterest = QwtInterval(rect.left(), rect.right()
                                                ).normalized()
    
    def rectOfInterest(self):
        return self.d_rectOfInterest
    
    def boundingRect(self):
        if self.d_size == 0 or\
           not (self.d_interval.isValid() or self.d_intervalOfInterest.isValid()):
            return QRectF(1.0, 1.0, -2.0, -2.0)
        return qwtBoundingRect(self)
    
    def sample(self, index):
        if index >= self.d_size:
            return QPointF(0, 0)
        xValue = self.x(index)
        yValue = self.y(xValue)
        return QPointF(xValue, yValue)
    
    def x(self, index):
        if self.d_interval.isValid():
            interval = self.d_interval
        else:
            interval = self.d_intervalOfInterest
        if not interval.isValid() or self.d_size == 0 or index >= self.d_size:
            return 0.
        dx = interval.width()/self.d_size
        return interval.minValue() + index*dx
    