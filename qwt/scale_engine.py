# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

from __future__ import division

from qwt.interval import QwtInterval
from qwt.scale_div import QwtScaleDiv
from qwt.transform import QwtLogTransform
from qwt.math import qwtFuzzyCompare
from qwt.transform import QwtTransform

from qwt.qt.QtCore import qFuzzyCompare

import numpy as np

DBL_MAX = np.finfo(float).max
LOG_MIN = 1.0e-100
LOG_MAX = 1.0e100


def qwtLog(base, value):
    return np.log(value)/np.log(base)

def qwtLogInterval(base, interval):
    return QwtInterval(qwtLog(base, interval.minValue()),
                       qwtLog(base, interval.maxValue()))

def qwtPowInterval(base, interval):
    return QwtInterval(np.power(base, interval.minValue()),
                       np.power(base, interval.maxValue()))

def qwtStepSize(intervalSize, maxSteps, base):
    minStep = divideInterval(intervalSize, maxSteps, base)
    if minStep != 0.:
        numTicks = np.ceil(abs(intervalSize/minStep))-1
        if qwtFuzzyCompare((numTicks+1)*abs(minStep),
                           abs(intervalSize), intervalSize) > 0:
            return .5*intervalSize
    return minStep

EPS = 1.0e-6

def ceilEps(value, intervalSize):
    eps = EPS*intervalSize
    value = (value-eps)/intervalSize
    return np.ceil(value)*intervalSize

def floorEps(value, intervalSize):
    eps = EPS*intervalSize
    value = (value+eps)/intervalSize
    return np.floor(value)*intervalSize

def divideEps(intervalSize, numSteps):
    if numSteps == 0. or intervalSize == 0.:
        return 0.
    return (intervalSize-(EPS*intervalSize))/numSteps

def divideInterval(intervalSize, numSteps, base):
    if numSteps <= 0:
        return 0.
    v = divideEps(intervalSize, numSteps)
    if v == 0.:
        return 0.

    lx = qwtLog(base, abs(v))
    p = np.floor(lx)
    fraction = np.power(base, lx-p)
    n = base
    while n > 1 and fraction <= n/2:
        n /= 2
    
    stepSize = n*np.power(base, p)
    if v < 0:
        stepSize = -stepSize
    
    return stepSize


class QwtScaleEngine_PrivateData(object):
    def __init__(self):
        self.attributes = QwtScaleEngine.NoAttribute
        self.lowerMargin = 0.
        self.upperMargin = 0.
        self.referenceValue = 0.
        self.base = 10
        self.transform = None  # QwtTransform


class QwtScaleEngine(object):
    
    # enum Attribute
    NoAttribute = 0x00
    IncludeReference = 0x01
    Symmetric = 0x02
    Floating = 0x04
    Inverted = 0x08
    
    def __init__(self, base=10):
        self.__data = QwtScaleEngine_PrivateData()
        self.setBase(base)
    
    def setTransformation(self, transform):
        assert transform is None or isinstance(transform, QwtTransform)
        if transform != self.__data.transform:
            self.__data.transform = transform
    
    def transformation(self):
        if self.__data.transform:
            return self.__data.transform.copy()
    
    def lowerMargin(self):
        return self.__data.lowerMargin
    
    def upperMargin(self):
        return self.__data.upperMargin
    
    def setMargins(self, lower, upper):
        self.__data.lowerMargin = max([lower, 0.])
        self.__data.upperMargin = max([upper, 0.])
    
    def divideInterval(self, intervalSize, numSteps):
        return divideInterval(intervalSize, numSteps, self.__data.base)
    
    def contains(self, interval, value):
        if not interval.isValid():
            return False
        elif qwtFuzzyCompare(value, interval.minValue(), interval.width()) < 0:
            return False
        elif qwtFuzzyCompare(value, interval.maxValue(), interval.width()) > 0:
            return False
        else:
            return True
    
    def strip(self, ticks, interval):
        if not interval.isValid() or not ticks:
            return []
        if self.contains(interval, ticks[0]) and\
           self.contains(interval, ticks[-1]):
            return ticks
        return [tick for tick in ticks
                if self.contains(interval, tick)]
    
    def buildInterval(self, value):
        if value == 0.:
            delta = .5
        else:
            delta = abs(.5*value)
        if DBL_MAX-delta < value:
            return QwtInterval(DBL_MAX-delta, DBL_MAX)
        if -DBL_MAX+delta > value:
            return QwtInterval(-DBL_MAX, -DBL_MAX+delta)
        return QwtInterval(value-delta, value+delta)
    
    def setAttribute(self, attribute, on=True):
        if on:
            self.__data.attributes |= attribute
        else:
            self.__data.attributes &= ~attribute
    
    def testAttribute(self, attribute):
        return self.__data.attributes & attribute
    
    def setAttributes(self, attributes):
        self.__data.attributes = attributes
    
    def attributes(self):
        return self.__data.attributes
    
    def setReference(self, r):
        self.__data.referenceValue = r
    
    def reference(self):
        return self.__data.referenceValue
    
    def setBase(self, base):
        self.__data.base = max([base, 2])
    
    def base(self):
        return self.__data.base


class QwtLinearScaleEngine(QwtScaleEngine):
    def __init__(self, base=10):
        super(QwtLinearScaleEngine, self).__init__(base)
    
    def autoScale(self, maxNumSteps, x1, x2, stepSize):
        interval = QwtInterval(x1, x2)
        interval = interval.normalized()
        interval.setMinValue(interval.minValue()-self.lowerMargin())
        interval.setMaxValue(interval.maxValue()+self.upperMargin())
        if self.testAttribute(QwtScaleEngine.Symmetric):
            interval = interval.symmetrize(self.reference())
        if self.testAttribute(QwtScaleEngine.IncludeReference):
            interval = interval.extend(self.reference())
        if interval.width() == 0.:
            interval = self.buildInterval(interval.minValue())
        stepSize = divideInterval(interval.width(),
                                  max([maxNumSteps, 1]), self.base())
        if not self.testAttribute(QwtScaleEngine.Floating):
            interval = self.align(interval, stepSize)
        x1 = interval.minValue()
        x2 = interval.maxValue()
        if self.testAttribute(QwtScaleEngine.Inverted):
            x1, x2 = x2, x1
            stepSize = -stepSize
        return x1, x2, stepSize
    
    def divideScale(self, x1, x2, maxMajorSteps, maxMinorSteps, stepSize=0.):
        interval = QwtInterval(x1, x2).normalized()
        if interval.width() <= 0:
            return QwtScaleDiv()
        stepSize = abs(stepSize)
        if stepSize == 0.:
            if maxMajorSteps < 1:
                maxMajorSteps = 1
            stepSize = divideInterval(interval.width(), maxMajorSteps,
                                      self.base())
        scaleDiv = QwtScaleDiv()
        if stepSize != 0.:
            ticks = self.buildTicks(interval, stepSize, maxMinorSteps)
            scaleDiv = QwtScaleDiv(interval, ticks)
        if x1 > x2:
            scaleDiv.invert()
        return scaleDiv
        
    def buildTicks(self, interval, stepSize, maxMinorSteps):
        ticks = [[] for _i in range(QwtScaleDiv.NTickTypes)]
        boundingInterval = self.align(interval, stepSize)
        ticks[QwtScaleDiv.MajorTick] = self.buildMajorTicks(boundingInterval,
                                                            stepSize)
        if maxMinorSteps > 0:
            self.buildMinorTicks(ticks, maxMinorSteps, stepSize)
        for i in range(QwtScaleDiv.NTickTypes):
            ticks[i] = self.strip(ticks[i], interval)
            for j in range(len(ticks[i])):
                if qwtFuzzyCompare(ticks[i][j], 0., stepSize) == 0:
                    ticks[i][j] = 0.
        return ticks
    
    def buildMajorTicks(self, interval, stepSize):
        numTicks = min([round(interval.width()/stepSize)+1, 10000])
        ticks = [interval.minValue()]
        for i in range(1, int(numTicks-1)):
            ticks += [interval.minValue()+i*stepSize]
        ticks += [interval.maxValue()]
        return ticks
    
    def buildMinorTicks(self, ticks, maxMinorSteps, stepSize):
        minStep = qwtStepSize(stepSize, maxMinorSteps, self.base())
        if minStep == 0.:
            return
        numTicks = int(np.ceil(abs(stepSize/minStep))-1)
        medIndex = -1
        if numTicks % 2:
            medIndex = numTicks/2
        for val in ticks[QwtScaleDiv.MajorTick]:
            for k in range(numTicks):
                val += minStep
                alignedValue = val
                if qwtFuzzyCompare(val, 0., stepSize) == 0:
                    alignedValue = 0.
                if k == medIndex:
                    ticks[QwtScaleDiv.MediumTick] += [alignedValue]
                else:
                    ticks[QwtScaleDiv.MinorTick] += [alignedValue]
    
    def align(self, interval, stepSize):
        x1 = interval.minValue()
        x2 = interval.maxValue()
        if -DBL_MAX+stepSize <= x1:
            x = floorEps(x1, stepSize)
            if qwtFuzzyCompare(x1, x, stepSize) != 0:
                x1 = x
        if DBL_MAX-stepSize >= x2:
            x = ceilEps(x2, stepSize)
            if qwtFuzzyCompare(x2, x, stepSize) != 0:
                x2 = x
        return QwtInterval(x1, x2)


class QwtLogScaleEngine(QwtScaleEngine):
    def __init__(self, base=10):
        super(QwtLogScaleEngine, self).__init__(base)
        self.setTransformation(QwtLogTransform())
        
    def autoScale(self, maxNumSteps, x1, x2, stepSize):
        if x1 > x2:
            x1, x2 = x2, x1
        logBase = self.base()
        interval = QwtInterval(x1/np.power(logBase, self.lowerMargin()),
                               x2*np.power(logBase, self.upperMargin()))
        if interval.maxValue()/interval.minValue() < logBase:
            linearScaler = QwtLinearScaleEngine()
            linearScaler.setAttributes(self.attributes())
            linearScaler.setReference(self.reference())
            linearScaler.setMargins(self.lowerMargin(), self.upperMargin())
            
            x1, x2, stepSize = linearScaler.autoScale(maxNumSteps,
                                                      x1, x2, stepSize)
            
            linearInterval = QwtInterval(x1, x2).normalized()
            linearInterval = linearInterval.limited(LOG_MIN, LOG_MAX)
            
            if linearInterval.maxValue()/linearInterval.minValue() < logBase:
                if stepSize < 0.:
                    stepSize = -qwtLog(logBase, abs(stepSize))
                else:
                    stepSize = qwtLog(logBase, stepSize)
                return x1, x2, stepSize
            
        logRef = 1.
        if self.reference() > LOG_MIN/2:
            logRef = min([self.reference(), LOG_MAX/2])
        
        if self.testAttribute(QwtScaleEngine.Symmetric):
            delta = max([interval.maxValue()/logRef,
                         logRef/interval.minValue()])
            interval.setInterval(logRef/delta, logRef*delta)
        
        if self.testAttribute(QwtScaleEngine.IncludeReference):
            interval = interval.extend(logRef)

        interval = interval.limited(LOG_MIN, LOG_MAX)        
        
        if interval.width() == 0.:
            interval = self.buildInterval(interval.minValue())
        
        stepSize = self.divideInterval(
            qwtLogInterval(logBase, interval).width(), max([maxNumSteps, 1]))
        if stepSize < 1.:
            stepSize = 1.
        
        if not self.testAttribute(QwtScaleEngine.Floating):
            interval = self.align(interval, stepSize)
        
        x1 = interval.minValue()
        x2 = interval.maxValue()
        
        if self.testAttribute(QwtScaleEngine.Inverted):
            x1, x2 = x2, x1
            stepSize = -stepSize
    
    def divideScale(self, x1, x2, maxMajorSteps, maxMinorSteps, stepSize=0.):
        interval = QwtInterval(x1, x2).normalized()
        interval = interval.limited(LOG_MIN, LOG_MAX)
        
        if interval.width() <= 0:
            return QwtScaleDiv()
        
        logBase = self.base()
        
        if interval.maxValue()/interval.minValue() < logBase:
            linearScaler = QwtLinearScaleEngine()
            linearScaler.setAttributes(self.attributes())
            linearScaler.setReference(self.reference())
            linearScaler.setMargins(self.lowerMargin(), self.upperMargin())
            
            if stepSize != 0.:
                if stepSize < 0.:
                    stepSize = -np.power(logBase, -stepSize)
                else:
                    stepSize = np.power(logBase, stepSize)
            
            return linearScaler.divideScale(x1, x2, maxMajorSteps,
                                            maxMinorSteps, stepSize)
        
        stepSize = abs(stepSize)
        if stepSize == 0.:
            if maxMajorSteps < 1:
                maxMajorSteps = 1
            stepSize = self.divideInterval(
                    qwtLogInterval(logBase, interval).width(), maxMajorSteps)
            if stepSize < 1.:
                stepSize = 1.
        
        scaleDiv = QwtScaleDiv()
        if stepSize != 0.:
            ticks = self.buildTicks(interval, stepSize, maxMinorSteps)
            scaleDiv = QwtScaleDiv(interval, ticks)
        
        if x1 > x2:
            scaleDiv.invert()
        
        return scaleDiv
    
    def buildTicks(self, interval, stepSize, maxMinorSteps):
        ticks = [[] for _i in range(QwtScaleDiv.NTickTypes)]
        boundingInterval = self.align(interval, stepSize)
        ticks[QwtScaleDiv.MajorTick] = self.buildMajorTicks(boundingInterval,
                                                            stepSize)
        if maxMinorSteps > 0:
            self.buildMinorTicks(ticks, maxMinorSteps, stepSize)
        for i in range(QwtScaleDiv.NTickTypes):
            ticks[i] = self.strip(ticks[i], interval)
        return ticks
    
    def buildMajorTicks(self, interval, stepSize):
        width = qwtLogInterval(self.base(), interval).width()
        numTicks = min([int(round(width/stepSize))+1, 10000])

        lxmin = np.log(interval.minValue())
        lxmax = np.log(interval.maxValue())
        lstep = (lxmax-lxmin)/float(numTicks-1)

        ticks = [interval.minValue()]
        for i in range(1, numTicks-1):
            ticks += [np.exp(lxmin+float(i)*lstep)]
        ticks += [interval.maxValue()]
        return ticks

    def buildMinorTicks(self, ticks, maxMinorSteps, stepSize):
        logBase = self.base()
        
        if stepSize < 1.1:
            minStep = self.divideInterval(stepSize, maxMinorSteps+1)
            if minStep == 0.:
                return
            
            numSteps = int(round(stepSize/minStep))
            
            mediumTickIndex = -1
            if numSteps > 2 and numSteps % 2 == 0:
                mediumTickIndex = numSteps/2
            
            for v in ticks[QwtScaleDiv.MajorTick]:
                s = logBase/numSteps
                if s >= 1.:
                    if not qFuzzyCompare(s, 1.):
                        ticks[QwtScaleDiv.MinorTick] += [v*s]
                    for j in range(2, numSteps):
                        ticks[QwtScaleDiv.MinorTick] += [v*j*s]
                else:
                    for j in range(1, numSteps):
                        tick = v + j*v*(logBase-1)/numSteps
                        if j == mediumTickIndex:
                            ticks[QwtScaleDiv.MediumTick] += [tick]
                        else:
                            ticks[QwtScaleDiv.MinorTick] += [tick]
                            
        else:
            minStep = self.divideInterval(stepSize, maxMinorSteps)
            if minStep == 0.:
                return
            
            if minStep < 1.:
                minStep = 1.
            
            numTicks = int(round(stepSize/minStep))-1
            
            if qwtFuzzyCompare((numTicks+1)*minStep, stepSize, stepSize) > 0:
                numTicks = 0
            
            if numTicks < 1:
                return
            
            mediumTickIndex = -1
            if numTicks > 2 and numTicks % 2:
                mediumTickIndex = numTicks/2
            
            minFactor = max([np.power(logBase, minStep), float(logBase)])
            
            for tick in ticks[QwtScaleDiv.MajorTick]:
                for j in range(numTicks):
                    tick *= minFactor
                    if j == mediumTickIndex:
                        ticks[QwtScaleDiv.MediumTick] += [tick]
                    else:
                        ticks[QwtScaleDiv.MinorTick] += [tick]

    def align(self, interval, stepSize):
        intv = qwtLogInterval(self.base(), interval)
        
        x1 = floorEps(intv.minValue(), stepSize)
        if qwtFuzzyCompare(interval.minValue(), x1, stepSize) == 0:
            x1 = interval.minValue()
        
        x2 = ceilEps(intv.maxValue(), stepSize)
        if qwtFuzzyCompare(interval.maxValue(), x2, stepSize) == 0:
            x2 = interval.maxValue()
        
        return qwtPowInterval(self.base(), QwtInterval(x1, x2))
        
        