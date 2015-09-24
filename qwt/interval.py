# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtInterval
-----------

.. autoclass:: QwtInterval
   :members:
"""


class QwtInterval(object):
    """
    A class representing an interval

    The interval is represented by 2 doubles, the lower and the upper limit.
    
    .. py:class:: QwtInterval(minValue=0., maxValue=-1., borderFlags=None)
    
        Build an interval with from min/max values
        
        :param float minValue: Minimum value
        :param float maxValue: Maximum value
        :param int borderFlags: Include/Exclude borders
    """
    
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
        """
        .. py:method:: setInterval(minValue, maxValue, borderFlags)
        
            Assign the limits of the interval
            
            :param: float minValue: Minimum value
            :param: float maxValue: Maximum value
            :param: int borderFlags: Include/Exclude borders
        """
        self.__minValue = minValue
        self.__maxValue = maxValue
        self.__borderFlags = borderFlags
        
    def setBorderFlags(self, borderFlags):
        """
        .. py:method:: setBorderFlags(borderFlags)
        
            Change the border flags
            
            :param: int borderFlags: Include/Exclude borders

        .. seealso::
        
            :py:meth:`borderFlags()`
        """
        self.__borderFlags = borderFlags

    def borderFlags(self):
        """
        .. py:method:: borderFlags()

            :return: Border flags

        .. seealso::
        
            :py:meth:`setBorderFlags()`
        """
        return self.__borderFlags
    
    def setMinValue(self, minValue):
        """
        .. py:method:: setMinValue(minValue)
        
            Assign the lower limit of the interval
                    
            :param: float minValue: Minimum value
        """
        self.__minValue = minValue
    
    def setMaxValue(self, maxValue):
        """
        .. py:method:: setMaxValue(minValue)
        
            Assign the upper limit of the interval
                    
            :param: float maxValue: Maximum value
        """
        self.__maxValue = maxValue
    
    def minValue(self):
        """
        .. py:method:: minValue()

            :return: Lower limit of the interval
        """
        return self.__minValue
    
    def maxValue(self):
        """
        .. py:method:: maxValue()

            :return: Upper limit of the interval
        """
        return self.__maxValue

    def isValid(self):
        """
        .. py:method:: isValid()
        
            A interval is valid when minValue() <= maxValue().
            In case of `QwtInterval.ExcludeBorders` it is true
            when minValue() < maxValue()

            :return: True, when the interval is valid
        """
        if (self.__borderFlags & self.ExcludeBorders) == 0:
            return self.__minValue <= self.__maxValue
        else:
            return self.__minValue < self.__maxValue
    
    def width(self):
        """
        .. py:method:: width()
        
            The width of invalid intervals is 0.0, otherwise the result is
            maxValue() - minValue().

            :return: the width of an interval
        """
        if self.isValid():
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
        """
        .. py:method:: isNull()

            :return: true, if isValid() && (minValue() >= maxValue())
        """
        return self.isValid() and self.__minValue >= self.__maxValue
    
    def invalidate(self):
        """
        .. py:method:: invalidate()

            The limits are set to interval [0.0, -1.0]

        .. seealso::
        
            :py:meth:`isValid()`
        """
        self.__minValue = 0.
        self.__maxValue = -1.
    
    def normalized(self):
        """
        .. py:method:: normalized()

            Normalize the limits of the interval
            
            If maxValue() < minValue() the limits will be inverted.
            
            :return: Normalized interval

        .. seealso::
        
            :py:meth:`isValid()`, :py:meth:`inverted()`
        """
        if self.__minValue > self.__maxValue:
            return self.inverted()
        elif self.__minValue == self.__maxValue and\
             self.__borderFlags == self.ExcludeMinimum:
            return self.inverted()
        else:
            return self
    
    def inverted(self):
        """
        .. py:method:: inverted()

            Invert the limits of the interval
            
            :return: Inverted interval

        .. seealso::
        
            :py:meth:`normalized()`
        """
        borderFlags = self.IncludeBorders
        if self.__borderFlags & self.ExcludeMinimum:
            borderFlags |= self.ExcludeMaximum
        if self.__borderFlags & self.ExcludeMaximum:
            borderFlags |= self.ExcludeMinimum
        return QwtInterval(self.__maxValue, self.__minValue, borderFlags)
    
    def contains(self, value):
        """
        .. py:method:: contains(value)

            Test if a value is inside an interval
            
            :param: float value: Value
            :return: true, if value >= minValue() && value <= maxValue()
        """
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
        """
        .. py:method:: unite(other)

            Unite two intervals
            
            :param: QwtInterval other: other interval to united with
            :return: united interval
        """
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
        """
        .. py:method:: intersect(other)

            Intersect two intervals
            
            :param: QwtInterval other: other interval to intersect with
            :return: intersected interval
        """
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
        """
        .. py:method:: intersects(other)

            Test if two intervals overlap
            
            :param: QwtInterval other: other interval
            :return: True, when the intervals are intersecting
        """
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
        """
        .. py:method:: symmetrize(value)

            Adjust the limit that is closer to value, so that value becomes
            the center of the interval.
            
            :param: float value: Center
            :return: Interval with value as center
        """
        if not self.isValid():
            return self
        delta = max([abs(value-self.__maxValue),
                     abs(value-self.__minValue)])
        return QwtInterval(value-delta, value+delta)

    def limited(self, lowerBound, upperBound):
        """
        .. py:method:: limited(lowerBound, upperBound)

            Limit the interval, keeping the border modes
            
            :param: float lowerBound: Lower limit
            :param: float upperBound: Upper limit
            :return: Limited interval
        """
        if not self.isValid() or lowerBound > upperBound:
            return QwtInterval()
        minValue = max([self.__minValue, lowerBound])
        minValue = min([minValue, upperBound])
        maxValue = max([self.__maxValue, lowerBound])
        maxValue = min([maxValue, upperBound])
        return QwtInterval(minValue, maxValue, self.__borderFlags)
    
    def extend(self, value):
        """
        .. py:method:: extend(value)

            Extend the interval

            If value is below minValue(), value becomes the lower limit.
            If value is above maxValue(), value becomes the upper limit.

            extend() has no effect for invalid intervals
            
            :param: float value: Value
            :return: extended interval
        """
        if not self.isValid():
            return self
        return QwtInterval(min([value, self.__minValue]),
                           max([value, self.__maxValue]))

