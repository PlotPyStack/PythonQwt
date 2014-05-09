# -*- coding: utf-8 -*-

from qwt.qwt_interval import QwtInterval


class QwtIntervalSample(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.value = 0.
            self.interval = QwtInterval()
        elif len(args) == 2:
            v, intv = args
            self.value = v
            self.interval = intv
        elif len(args) == 3:
            v, min_, max_ = args
            self.value = v
            self.interval = QwtInterval(min_, max_)
        else:
            raise TypeError("%s() takes 0, 2 or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def __eq__(self, other):
        return self.value == other.value and self.interval == other.interval
    
    def __ne__(self, other):
        return not (self == other)
    

class QwtSetSample(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.value = 0
            self.set = []
        elif len(args) == 2:
            v, s = args
            self.value = v
            self.set = s
        else:
            raise TypeError("%s() takes 0 or 2 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def __eq__(self, other):
        return self.value == other.value and self.set == other.set
    
    def __ne__(self, other):
        return not (self == other)
    
    def added(self):
        return sum(self.set)
        

class QwtOHLCSample(object):
    def __init__(self, time=0., open_=0., high=0., low=0., close=0.):
        self.time = time
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        
    def isValid(self):
        return self.low <= self.high and self.open >= self.low and\
               self.open <= self.high and self.close >= self.low and\
               self.close <= self.high
    
    def boundingInterval(self):
        minY = self.open
        minY = min([minY, self.high])
        minY = min([minY, self.low])
        minY = min([minY, self.close])
        maxY = self.open
        maxY = max([maxY, self.high])
        maxY = max([maxY, self.low])
        maxY = max([maxY, self.close])
        return QwtInterval(minY, maxY)
        
    
