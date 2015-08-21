# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see qwt/LICENSE for details)

from qwt.interval import QwtInterval

import copy


class QwtScaleDiv(object):
    # enum TickType
    NoTick = -1
    MinorTick, MediumTick, MajorTick, NTickTypes = range(4)
    
    def __init__(self, *args):
        self.__ticks = None
        if len(args) == 2 and isinstance(args[1], (tuple, list)):
            interval, ticks = args
            self.__lowerBound = interval.minValue()
            self.__upperBound = interval.maxValue()
            self.__ticks = ticks[:]
        elif len(args) == 2:
            self.__lowerBound, self.__upperBound = args
        elif len(args) == 3:
            self.__lowerBound, self.__upperBound, ticks = args
            self.__ticks = ticks[:]
        elif len(args) == 4:
            (self.__lowerBound, self.__upperBound,
             minorTicks, mediumTicks, majorTicks) = args
            self.__ticks[self.MinorTick] = minorTicks
            self.__ticks[self.MediumTick] = mediumTicks
            self.__ticks[self.MajorTick] = majorTicks
        elif len(args) == 0:
            self.__lowerBound, self.__upperBound = 0., 0.
        else:
            raise TypeError("%s() takes 0, 2, 3 or 4 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def setInterval(self, *args):
        if len(args) == 2:
            self.__lowerBound, self.__upperBound = args
        elif len(args) == 1:
            interval, = args
            self.__lowerBound = interval.minValue()
            self.__upperBound = interval.maxValue()
        else:
            raise TypeError("%s().setInterval() takes 1 or 2 argument(s) (%s "\
                            "given)" % (self.__class__.__name__, len(args)))
    
    def interval(self):
        return QwtInterval(self.__lowerBound, self.__upperBound)
    
    def setLowerBound(self, lowerBound):
        self.__lowerBound = lowerBound
    
    def lowerBound(self):
        return self.__lowerBound
    
    def setUpperBound(self, upperBound):
        self.__upperBound = upperBound
    
    def upperBound(self):
        return self.__upperBound
    
    def range(self):
        return self.__upperBound - self.__lowerBound
    
    def __eq__(self, other):
        if self.__ticks is None:
            return False
        if self.__lowerBound != other.__lowerBound or\
           self.__upperBound != other.__upperBound:
            return False
        return self.__ticks == other.__ticks
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def isEmpty(self):
        return self.__lowerBound == self.__upperBound
    
    def isIncreasing(self):
        return self.__lowerBound <= self.__upperBound
    
    def contains(self, value):
        min_ = min([self.__lowerBound, self.__upperBound])
        max_ = max([self.__lowerBound, self.__upperBound])
        return value >= min_ and value <= max_
    
    def invert(self):
        (self.__lowerBound,
         self.__upperBound) = self.__upperBound, self.__lowerBound
        for index in range(self.NTickTypes):
            self.__ticks[index].reverse()
    
    def inverted(self):
        other = copy.deepcopy(self)
        other.invert()
        return other
    
    def bounded(self, lowerBound, upperBound):
        min_ = min([self.__lowerBound, self.__upperBound])
        max_ = max([self.__lowerBound, self.__upperBound])
        sd = QwtScaleDiv()
        sd.setInterval(lowerBound, upperBound)
        for tickType in range(self.NTickTypes):
            sd.setTicks(tickType, [tick for tick in self.__ticks[tickType]
                                   if tick >= min_ and tick <= max_])
        return sd
    
    def setTicks(self, tickType, ticks):
        if tickType in range(self.NTickTypes):
            self.__ticks[tickType] = ticks
    
    def ticks(self, tickType):
        if self.__ticks is not None and tickType in range(self.NTickTypes):
            return self.__ticks[tickType]
        else:
            return []
