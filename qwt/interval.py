# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see qwt/LICENSE for details)


class QwtInterval(object):
    
    # enum BorderFlag
    IncludeBorders = 0x00
    ExcludeMinimum = 0x01
    ExcludeMaximum = 0x02
    ExcludeBorders = ExcludeMinimum | ExcludeMaximum
    
    def __init__(self, minValue=0., maxValue=-1., borderFlags=None):
        assert not isinstance(minValue, QwtInterval)
        assert not isinstance(maxValue, QwtInterval)
        self.__minValue = minValue
        self.__maxValue = maxValue
        if borderFlags is None:
            self.__borderFlags = self.IncludeBorders
        else:
            self.__borderFlags = borderFlags

    def setInterval(self, minValue, maxValue, borderFlags):
        self.__minValue = minValue
        self.__maxValue = maxValue
        self.__borderFlags = borderFlags
        
    def setBorderFlags(self, borderFlags):
        self.__borderFlags = borderFlags

    def borderFlags(self):
        return self.__borderFlags
    
    def setMinValue(self, minValue):
        self.__minValue = minValue
    
    def setMaxValue(self, maxValue):
        self.__maxValue = maxValue
    
    def minValue(self):
        return self.__minValue
    
    def maxValue(self):
        return self.__maxValue

    def isValid(self):
        if (self.__borderFlags & self.ExcludeBorders) == 0:
            return self.__minValue <= self.__maxValue
        else:
            return self.__minValue < self.__maxValue
    
    def width(self):
        if self.isValid:
            return self.__maxValue - self.__minValue
        else:
            return 0.
    
    def __and__(self, other):
        return self.intersect(other)
    
    def __iand__(self, other):
        self = self & other
        return self
    
    def __or__(self, other):
        if isinstance(other, QwtInterval):
            return self.unite(other)
        else:
            return self.extend(other)
    
    def __ior__(self, other):
        self = self | other
        return self
    
    def __eq__(self, other):
        return self.__minValue == other.__minValue and\
               self.__maxValue == other.__maxValue and\
               self.__borderFlags == other.__borderFlags

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def isNull(self):
        return self.isValid() and self.__minValue >= self.__maxValue
    
    def invalidate(self):
        self.__minValue = 0.
        self.__maxValue = -1.
    
    def normalized(self):
        if self.__minValue > self.__maxValue:
            return self.inverted()
        elif self.__minValue == self.__maxValue and\
             self.__borderFlags == self.ExcludeMinimum:
            return self.inverted()
        else:
            return self
    
    def inverted(self):
        borderFlags = self.IncludeBorders
        if self.__borderFlags & self.ExcludeMinimum:
            borderFlags |= self.ExcludeMaximum
        if self.__borderFlags & self.ExcludeMaximum:
            borderFlags |= self.ExcludeMinimum
        return QwtInterval(self.__maxValue, self.__minValue, borderFlags)
    
    def contains(self, value):
        if not self.isValid():
            return False
        elif value < self.__minValue or value > self.__maxValue:
            return False
        elif value == self.__minValue and\
             self.__borderFlags & self.ExcludeMinimum:
            return False
        elif value == self.__maxValue and\
             self.__borderFlags & self.ExcludeMaximum:
            return False
        else:
            return True

    def unite(self, other):
        if not self.isValid():
            if not other.isValid():
                return QwtInterval()
            else:
                return other
        elif not other.isValid():
            return self
        
        united = QwtInterval()
        flags = self.IncludeBorders
        
        # minimum
        if self.__minValue < other.minValue():
            united.setMinValue(self.__minValue)
            flags &= self.__borderFlags & self.ExcludeMinimum
        elif other.minValue() < self.__minValue:
            united.setMinValue(other.minValue())
            flags &= other.borderFlags() & self.ExcludeMinimum
        else:
            united.setMinValue(self.__minValue)
            flags &= (self.__borderFlags & other.borderFlags())\
                     & self.ExcludeMinimum
        
        # maximum
        if self.__maxValue > other.maxValue():
            united.setMaxValue(self.__maxValue)
            flags &= self.__borderFlags & self.ExcludeMaximum
        elif other.maxValue() > self.__maxValue:
            united.setMaxValue(other.maxValue())
            flags &= other.borderFlags() & self.ExcludeMaximum
        else:
            united.setMaxValue(self.__maxValue)
            flags &= self.__borderFlags & other.borderFlags()\
                     & self.ExcludeMaximum
        
        united.setBorderFlags(flags)
        return united
        
    def intersect(self, other):
        if not other.isValid() or not self.isValid():
            return QwtInterval()
        
        i1 = self
        i2 = other
        
        if i1.minValue() > i2.minValue():
            i1, i2 = i2, i1
        elif i1.minValue() == i2.minValue():
            if i1.borderFlags() & self.ExcludeMinimum:
                i1, i2 = i2, i1
        
        if i1.maxValue() < i2.maxValue():
            return QwtInterval()
        
        if i1.maxValue() == i2.minValue():
            if i1.borderFlags() & self.ExcludeMaximum or\
               i2.borderFlags() & self.ExcludeMinimum:
                return QwtInterval()
        
        intersected = QwtInterval()
        flags = self.IncludeBorders
        
        intersected.setMinValue(i2.minValue())
        flags |= i2.borderFlags() & self.ExcludeMinimum
        
        if i1.maxValue() < i2.maxValue():
            intersected.setMaxValue(i1.maxValue())
            flags |= i1.borderFlags() & self.ExcludeMaximum
        elif i2.maxValue() < i1.maxValue():
            intersected.setMaxValue(i2.maxValue())
            flags |= i2.borderFlags() & self.ExcludeMaximum
        else:  # i1.maxValue() == i2.maxValue()
            intersected.setMaxValue(i1.maxValue())
            flags |= i1.borderFlags() & i2.borderFlags() & self.ExcludeMaximum
        
        intersected.setBorderFlags(flags)
        return intersected
    
    def intersects(self, other):
        if not other.isValid() or not self.isValid():
            return False
        
        i1 = self
        i2 = other
        
        if i1.minValue() > i2.minValue():
            i1, i2 = i2, i1
        elif i1.minValue() == i2.minValue() and\
             i1.borderFlags() & self.ExcludeMinimum:
            i1, i2 = i2, i1
        
        if i1.maxValue() > i2.minValue():
            return True
        elif i1.maxValue() == i2.minValue():
            return i1.borderFlags() & self.ExcludeMaximum and\
                   i2.borderFlags() & self.ExcludeMinimum
        return False
    
    def symmetrize(self, value):
        if not self.isValid():
            return self
        delta = max([abs(value-self.__maxValue),
                     abs(value-self.__minValue)])
        return QwtInterval(value-delta, value+delta)

    def limited(self, lowerBound, upperBound):
        if not self.isValid() or lowerBound > upperBound:
            return QwtInterval()
        minValue = max([self.__minValue, lowerBound])
        minValue = min([minValue, upperBound])
        maxValue = max([self.__maxValue, lowerBound])
        maxValue = min([maxValue, upperBound])
        return QwtInterval(minValue, maxValue, self.__borderFlags)
    
    def extend(self, value):
        if not self.isValid():
            return self
        return QwtInterval(min([value, self.__minValue]),
                           max([value, self.__maxValue]))

