# -*- coding: utf-8 -*-


class LeftEdge(object):
    def __init__(self, x1, x2, y1, y2):
        self.d_x1 = x1
    
    def isInside(self, p):
        return p.x() >= self.d_x1
    
    def intersection(self, p1, p2):
        dy = (p1.y()-p2.y())/(p1.x()-p2.x())
        return Point(self.d_x1, (p2.y() + (self.d_x1 - p2.x())*dy))

class RightEdge(object):
    def __init__(self, x1, x2, y1, y2):
        self.d_x2 = x2
    
    def isInside(self, p):
        return p.x() <= self.d_x2
    
    def intersection(self, p1, p2):
        dy = (p1.y()-p2.y())/(p1.x()-p2.x())
        return Point(self.d_x2, (p2.y() + (self.d_x2 - p2.x())*dy))

class TopEdge(object):
    def __init__(self, x1, x2, y1, y2):
        self.d_y1 = y1
    
    def isInside(self, p):
        return p.y() >= self.d_y1
    
    def intersection(self, p1, p2):
        dx = (p1.x()-p2.x())/(p1.y()-p2.y())
        return Point((p2.x() + (self.d_y1 - p2.y())*dx), self.d_y1)

class BottomEdge(object):
    def __init__(self, x1, x2, y1, y2):
        self.d_y2 = y2
    
    def isInside(self, p):
        return p.y() <= self.d_y2
    
    def intersection(self, p1, p2):
        dx = (p1.x()-p2.x())/(p1.y()-p2.y())
        return Point((p2.x() + (self.d_y2 - p2.y())*dx), self.d_y2)

class PointBuffer(object):
    def __init__(self, capacity=0):
        self.capacity = capacity
        self.m_size = 0
        self.m_buffer = None
        if capacity > 0:
            self.reserve(capacity)
    
    def setPoints(self, numPoints, points):
        self.reserve(numPoints)
        self.m_size = numPoints
        
        


class QwtClipper(object):
    pass
