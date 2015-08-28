# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

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
    Natural, Periodic = list(range(2))
    
    def __init__(self, other=None):
        if other is not None:
            self.__data = other.__data
        else:
            self.__data = QwtSpline_PrivateData()
    
    def setSplineType(self, splineType):
        self.__data.splineType = splineType
    
    def splineType(self):
        return self.__data.splineType
    
    def setPoints(self, points):
        """points: QPolygonF"""
        size = points.size()
        if size <= 2:
            self.reset()
            return False
        self.__data.points = points
        self.__data.a.resize(size-1)
        self.__data.b.resize(size-1)
        self.__data.c.resize(size-1)
        if self.__data.splineType == self.Periodic:
            ok = self.buildPeriodicSpline(points)
        else:
            ok = self.buildNaturalSpline(points)
        if not ok:
            self.reset()
        return ok
    
    def points(self):
        return self.__data.points
        
    def coefficientsA(self):
        return self.__data.a
    
    def coefficientsB(self):
        return self.__data.b
    
    def coefficientsC(self):
        return self.__data.c
    
    def reset(self):
        self.__data.a = np.array([])
        self.__data.b = np.array([])
        self.__data.c = np.array([])
        self.__data.points.resize(0)
    
    def isValid(self):
        return len(self.__data.a) > 0
    
    def value(self, x):
        if len(self.__data.a) == 0:
            return 0.
        i = lookup(x, self.__data.points)
        delta = x - self.__data.points[i].x()
        return ((self.__data.a[i]*delta + self.__data.b[i])\
                *delta + self.__data.c[i])*delta + self.__data.points[i].y()
    
    def buildNaturalSpline(self, points):
        #TODO: to be implemented (!!! performance issue !!!)--> scipy ?
        raise NotImplementedError
        
    def buildPeriodicSpline(self, points):
        #TODO: to be implemented (!!! performance issue !!!)--> scipy ?
        raise NotImplementedError
        
        
    