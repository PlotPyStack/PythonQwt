# -*- coding: utf-8 -*-

from qwt.qwt_interval import QwtInterval

import copy


class QwtScaleDiv(object):
    # enum TickType
    NoTick = -1
    MinorTick, MediumTick, MajorTick, NTickTypes = range(4)
    
    def __init__(self, *args):
        if len(args) == 2 and isinstance(args[1], (tuple, list)):
            interval, ticks = args
            self.d_lowerBound = interval.minValue()
            self.d_upperBound = interval.maxValue()
            self.d_ticks = ticks[:]
        elif len(args) == 2:
            self.d_lowerBound, self.d_upperBound = args
        elif len(args) == 3:
            self.d_lowerBound, self.d_upperBound, ticks = args
            self.d_ticks = ticks[:]
        elif len(args) == 4:
            (self.d_lowerBound, self.d_upperBound,
             minorTicks, mediumTicks, majorTicks) = args
            self.d_ticks[self.MinorTick] = minorTicks
            self.d_ticks[self.MediumTick] = mediumTicks
            self.d_ticks[self.MajorTick] = majorTicks
        elif len(args) == 0:
            self.d_lowerBound, self.d_upperBound = 0., 0.
        else:
            raise TypeError("%s() takes 0, 2, 3 or 4 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def setInterval(self, *args):
        if len(args) == 2:
            self.d_lowerBound, self.d_upperBound = args
        elif len(args) == 1:
            interval, = args
            self.d_lowerBound = interval.minValue()
            self.d_upperBound = interval.maxValue()
        else:
            raise TypeError("%s().setInterval() takes 1 or 2 argument(s) (%s "\
                            "given)" % (self.__class__.__name__, len(args)))
    
    def interval(self):
        return QwtInterval(self.d_lowerBound, self.d_upperBound)
    
    def setLowerBound(self, lowerBound):
        self.d_lowerBound = lowerBound
    
    def lowerBound(self):
        return self.d_lowerBound
    
    def setUpperBound(self, upperBound):
        self.d_upperBound = upperBound
    
    def upperBound(self):
        return self.d_upperBound
    
    def range(self):
        return self.d_upperBound - self.d_lowerBound
    
    def __eq__(self, other):
        if self.d_lowerBound != other.d_lowerBound or\
           self.d_upperBound != other.d_upperBound:
            return False
        for index in range(self.NTickTypes):
            if self.d_ticks[index] != other.d_ticks[index]:
                return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def isEmpty(self):
        return self.d_lowerBound == self.d_upperBound
    
    def isIncreasing(self):
        return self.d_lowerBound <= self.d_upperBound
    
    def contains(self, value):
        min_ = min([self.d_lowerBound, self.d_upperBound])
        max_ = max([self.d_lowerBound, self.d_upperBound])
        return value >= min_ and value <= max_
    
    def invert(self):
        (self.d_lowerBound,
         self.d_upperBound) = self.d_upperBound, self.d_lowerBound
        for index in range(self.NTickTypes):
            self.d_ticks[index].reverse()
    
    def inverted(self):
        other = copy.deepcopy(self)
        other.invert()
        return other
    
    def bounded(self, lowerBound, upperBound):
        min_ = min([self.d_lowerBound, self.d_upperBound])
        max_ = max([self.d_lowerBound, self.d_upperBound])
        sd = QwtScaleDiv()
        sd.setInterval(lowerBound, upperBound)
        for tickType in range(self.NTickTypes):
            sd.setTicks(tickType, [tick for tick in self.d_ticks[tickType]
                                   if tick >= min_ and tick <= max_])
        return sd
    
    def setTicks(self, tickType, ticks):
        if tickType in range(self.NTickTypes):
            self.d_ticks[tickType] = ticks
    
    def ticks(self, tickType):
        if tickType in range(self.NTickTypes):
            return self.d_ticks[tickType]
        else:
            return []
