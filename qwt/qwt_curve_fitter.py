# -*- coding: utf-8 -*-

from qwt.qwt_spline import QwtSpline

from qwt.qt.QtGui import QPolygonF

import numpy as np


class QwtCurveFitter(object):
    def __init__(self):
        pass


class QwtSplineCurveFitter_PrivateData(object):
    def __init__(self):
        self.fitMode = QwtSplineCurveFitter.Auto
        self.splineSize = 250
        self.spline = QwtSpline()


class QwtSplineCurveFitter(QwtCurveFitter):
    
    # enum FitMode
    Auto, Spline, ParametricSpline = range(3)
    
    def __init__(self):
        super(QwtSplineCurveFitter, self).__init__()
        self.__data = QwtSplineCurveFitter_PrivateData()
    
    def setFitMode(self, mode):
        self.__data.fitMode = mode
    
    def fitMode(self):
        return self.__data.fitMode
    
    def setSpline(self, spline):
        self.__data.spline = spline
        self.__data.spline.reset()
    
    def spline(self):
        return self.__data.spline
    
    def setSplineSize(self, splineSize):
        self.__data.splineSize = max([splineSize, 10])
    
    def splineSize(self):
        return self.__data.splineSize
    
    def fitCurve(self, points):
        size = points.size()
        if size <= 2:
            return points
        fitMode = self.__data.fitMode
        if fitMode == self.Auto:
            fitMode = self.Spline
            p = points#.data()
            for i in range(1, size):
                if p[i].x() <= p[i-1].x():
                    fitMode = self.ParametricSpline
                    break
        if fitMode == self.ParametricSpline:
            return self.fitParametric(points)
        else:
            return self.fitSpline(points)
    
    def fitSpline(self, points):
        self.__data.spline.setPoints(points)
        if not self.__data.spline.isValid():
            return points
        fittedPoints = self.__data.splineSize
        x1 = points[0].x()
        x2 = points[int(points.size()-1)].x()
        dx = x2 - x1
        delta = dx/(self.__data.splineSize()-1)
        for i in range(self.__data.splineSize):
            p = fittedPoints[i]
            v = x1 + i*delta
            sv = self.__data.spline.value(v)
            p.setX(v)
            p.setY(sv)
        self.__data.spline.reset()
        return fittedPoints
    
    def fitParametric(self, points):
        size = points.size()
        fittedPoints = QPolygonF(self.__data.splineSize)
        splinePointsX = QPolygonF(size)
        splinePointsY = QPolygonF(size)
        p = points.data()
        spX = splinePointsX.data()
        spY = splinePointsY.data()
        param = 0.
        for i in range(size):
            x = p[i].x()
            y = p[i].y()
            if i > 0:
                delta = np.sqrt((x-spX[i-1].y())**2+(y-spY[i-1].y())**2)
                param += max([delta, 1.])
            spX[i].setX(param)
            spX[i].setY(x)
            spY[i].setX(param)
            spY[i].setY(y)
        self.__data.spline.setPoints(splinePointsX)
        if not self.__data.spline.isValid():
            return points
        deltaX = splinePointsX[size-1].x()/(self.__data.splineSize-1)
        for i in range(self.__data.splineSize):
            dtmp = i*deltaX
            fittedPoints[i].setX(self.__data.spline.value(dtmp))
        self.__data.spline.setPoints(splinePointsY)
        if not self.__data.spline.isValid():
            return points
        deltaY = splinePointsY[size-1].x()/(self.__data.splineSize-1)
        for i in range(self.__data.splineSize):
            dtmp = i*deltaY
            fittedPoints[i].setY(self.__data.spline.value(dtmp))
        return fittedPoints


class QwtWeedingCurveFitter_PrivateData(object):
    def __init__(self):
        self.tolerance = 1.
        self.chunkSize = 0

class QwtWeedingCurveFitter_Line(object):
    def __init__(self, i1=0, i2=0):
        self.from_ = i1
        self.to = i2

class QwtWeedingCurveFitter(QwtCurveFitter):
    def __init__(self, tolerance=1.):
        super(QwtWeedingCurveFitter, self).__init__()
        self.__data = QwtWeedingCurveFitter_PrivateData()
        self.setTolerance(tolerance)
    
    def setTolerance(self, tolerance):
        self.__data.tolerance = max([tolerance, 0.])
    
    def tolerance(self):
        return self.__data.tolerance
    
    def setChunkSize(self, numPoints):
        if numPoints > 0:
            numPoints = max([numPoints, 3])
        self.__data.chunkSize = numPoints
    
    def chunkSize(self):
        return self.__data.chunkSize
    
    def fitCurve(self, points):
        fittedPoints = QPolygonF()
        if self.__data.chunkSize == 0:
            fittedPoints = self.simplify(points)
        else:
            for i in range(0, points.size(), self.__data.chunkSize):
                p = points.mid(i, self.__data.chunkSize)
                fittedPoints += self.simplify(p)
        return fittedPoints
    
    def simplify(self, points):
        Line = QwtWeedingCurveFitter_Line
        toleranceSqr = self.__data.tolerance*self.__data.tolerance
        stack = []
        p = points.data()
        nPoints = points.size()
        usePoint = [False]*nPoints
        stack.insert(0, Line(0, nPoints-1))
        while stack:
            r = stack.pop(0)
            vecX = p[r.to].x()-p[r.from_].x()
            vecY = p[r.to].y()-p[r.from_].y()
            vecLength = np.sqrt(vecX**2+vecY**2)
            unitVecX = vecX/vecLength if vecLength != 0. else 0.
            unitVecY = vecY/vecLength if vecLength != 0. else 0.
            maxDistSqr = 0.
            nVertexIndexMaxDistance = r.from_ + 1
            for i in range(r.from_+1, r.to):
                fromVecX = p[i].x()-p[r.from_].x()
                fromVecY = p[i].y()-p[r.from_].y()
                if fromVecX * unitVecX + fromVecY * unitVecY < 0.0:
                    distToSegmentSqr = fromVecX * fromVecX + fromVecY * fromVecY
                else:
                    toVecX = p[i].x() - p[r.to].x()
                    toVecY = p[i].y() - p[r.to].y()
                    toVecLength = toVecX * toVecX + toVecY * toVecY
                    s = toVecX * ( -unitVecX ) + toVecY * ( -unitVecY )
                    if s < 0.:
                        distToSegmentSqr = toVecLength
                    else:
                        distToSegmentSqr = abs( toVecLength - s * s )
                if maxDistSqr < distToSegmentSqr:
                    maxDistSqr = distToSegmentSqr
                    nVertexIndexMaxDistance = i
            if maxDistSqr <= toleranceSqr:
                usePoint[r.from_] = True
                usePoint[r.to] = True
            else:
                stack.insert(0, Line( r.from_, nVertexIndexMaxDistance ))
                stack.insert(0, Line( nVertexIndexMaxDistance, r.to ))
        stripped = QPolygonF()
        for i in range(0, nPoints):
            if usePoint[i]:
                stripped += p[i]
        return stripped
