# -*- coding: utf-8 -*-

from qwt.qt.QtGui import QPolygonF

import numpy as np


class QwtSpline_PrivateData(object):
    def __init__(self):
        self.splineType = QwtSpline.Natural
        self.a = np.array([])
        self.b = np.array([])
        self.c = np.array([])
        self.points = QPolygonF()


def lookup(x, values):
    size = values.size()
    if x <= values[0].x():
        i1 = 0
    elif x >= values[size-2].x():
        i1 = size-2
    else:
        i1 = 0
        i2 = size-2
        i3 = 0
        while i2-i1 > 1:
            i3 = i1 + ((i2-i1) >> 1)
            if values[i3].x() > x:
                i2 = i3
            else:
                i1 = i3
    return i1


class QwtSpline(object):
    
    # enum SplineType
    Natural, Periodic = range(2)
    
    def __init__(self, other=None):
        if other:
            self.d_data = other.d_data
        else:
            self.d_data = QwtSpline_PrivateData()
    
    def setSplineType(self, splineType):
        self.d_data.splineType = splineType
    
    def splineType(self):
        return self.d_data.splineType
    
    def setPoints(self, points):
        """points: QPolygonF"""
        size = points.size()
        if size <= 2:
            self.reset()
            return False
        self.d_data.points = points
        self.d_data.a.resize(size-1)
        self.d_data.b.resize(size-1)
        self.d_data.c.resize(size-1)
        if self.d_data.splineType == self.Periodic:
            ok = self.buildPeriodicSpline(points)
        else:
            ok = self.buildNaturalSpline(points)
        if not ok:
            self.reset()
        return ok
    
    def points(self):
        return self.d_data.points
        
    def coefficientsA(self):
        return self.d_data.a
    
    def coefficientsB(self):
        return self.d_data.b
    
    def coefficientsC(self):
        return self.d_data.c
    
    def reset(self):
        self.d_data.a = np.array([])
        self.d_data.b = np.array([])
        self.d_data.c = np.array([])
        self.d_data.points.resize(0)
    
    def isValid(self):
        return len(self.d_data.a) > 0
    
    def value(self, x):
        if len(self.d_data.a) == 0:
            return 0.
        i = lookup(x, self.d_data.points)
        delta = x - self.d_data.points[i].x()
        return ((self.d_data.a[i]*delta + self.d_data.b[i])\
                *delta + self.d_data.c[i])*delta + self.d_data.points[i].y()
    
    def buildNaturalSpline(self, points):
        #TODO: to be implemented (!!! performance issue !!!)--> scipy ?
        raise NotImplementedError
        
    def buildPeriodicSpline(self, points):
        #TODO: to be implemented (!!! performance issue !!!)--> scipy ?
        raise NotImplementedError
        
        
    