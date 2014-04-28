# -*- coding: utf-8 -*-


class QwtInterval(object):
    
    # enum BorderFlag
    IncludeBorders = 0x00
    ExcludeMinimum = 0x01
    ExcludeMaximum = 0x02
    ExcludeBorders = ExcludeMinimum | ExcludeMaximum
    
    def __init__(self, minValue=0., maxValue=-1., borderFlags=None):
        self.d_minValue = minValue
        self.d_maxValue = maxValue
        if borderFlags is None:
            self.d_borderFlags = self.IncludeBorders
        else:
            self.d_borderFlags = borderFlags

    def setInterval(self, minValue, maxValue, borderFlags):
        self.d_minValue = minValue
        self.d_maxValue = maxValue
        self.d_borderFlags = borderFlags
        
    def setBorderFlags(self, borderFlags):
        self.d_borderFlags = borderFlags

    def borderFlags(self):
        return self.d_borderFlags
    
    def setMinValue(self, minValue):
        self.d_minValue = minValue
    
    def setMaxValue(self, maxValue):
        self.d_maxValue = maxValue
    
    def minValue(self):
        return self.d_minValue
    
    def maxValue(self):
        return self.d_maxValue

    def isValid(self):
        if (self.d_borderFlags & self.ExcludeBorders) == 0:
            return self.d_minValue <= self.d_maxValue
        else:
            return self.d_minValue < self.d_maxValue
    
    def width(self):
        if self.isValid:
            return self.d_maxValue - self.d_minValue
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
        return self.d_minValue == other.d_minValue and\
               self.d_maxValue == other.d_maxValue and\
               self.d_borderFlags == other.d_borderFlags

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def isNull(self):
        return self.isValid() and self.d_minValue >= self.d_maxValue
    
    def invalidate(self):
        self.d_minValue = 0.
        self.d_maxValue = -1.
    
    def normalized(self):
        if self.d_minValue > self.d_maxValue:
            return self.inverted()
        elif self.d_minValue == self.d_maxValue and\
             self.d_borderFlags == self.ExcludeMinimum:
            return self.inverted()
        else:
            return self
    
    def inverted(self):
        borderFlags = self.IncludeBorders
        if self.d_borderFlags & self.ExcludeMinimum:
            borderFlags |= self.ExcludeMaximum
        if self.d_borderFlags & self.ExcludeMaximum:
            borderFlags |= self.ExcludeMinimum
        return QwtInterval(self.d_maxValue, self.d_minValue, borderFlags)
    
    def contains(self, value):
        if not self.isValid():
            return False
        elif value < self.d_minValue or value > self.d_maxValue:
            return False
        elif value == self.d_minValue and\
             self.d_borderFlags & self.ExcludeMinimum:
            return False
        elif value == self.d_maxValue and\
             self.d_borderFlags & self.ExcludeMaximum:
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
        if self.d_minValue < other.minValue():
            united.setMinValue(self.d_minValue)
            flags &= self.d_borderFlags & self.ExcludeMinimum
        elif other.minValue() < self.d_minValue:
            united.setMinValue(other.minValue())
            flags &= other.borderFlags() & self.ExcludeMinimum
        else:
            united.setMinValue(self.d_minValue)
            flags &= (self.d_borderFlags & other.borderFlags())\
                     & self.ExcludeMinimum
        
        # maximum
        if self.d_maxValue > other.maxValue():
            united.setMaxValue(self.d_maxValue)
            flags &= self.d_borderFlags & self.ExcludeMaximum
        elif other.maxValue() > self.d_maxValue:
            united.setMaxValue(other.maxValue())
            flags &= other.borderFlags() & self.ExcludeMaximum
        else:
            united.setMaxValue(self.d_maxValue)
            flags &= self.d_borderFlags & other.borderFlags()\
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
        delta = max([abs(value-self.d_maxValue),
                     abs(value-self.d_minValue)])
        return QwtInterval(value-delta, value+delta)

    def limited(self, lowerBound, upperBound):
        if not self.isValid() or lowerBound > upperBound:
            return QwtInterval()
        minValue = max([self.d_minValue, lowerBound])
        minValue = min([minValue, upperBound])
        maxValue = max([self.d_maxValue, lowerBound])
        maxValue = min([maxValue, upperBound])
        return QwtInterval(minValue, maxValue, self.d_borderFlags)
    
    def extend(self, value):
        if not self.isValid():
            return self
        return QwtInterval(min([value, self.d_minValue]),
                           max([value, self.d_maxValue]))
