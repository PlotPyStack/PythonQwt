# -*- coding: utf-8 -*-

from qwt.qt.QtGui import QColor, qRed, qGreen, qBlue, qRgb, qRgba
from qwt.qt.QtCore import Qt, qIsNaN


class ColorStop(object):
    def __init__(self, pos, color):
        self.pos = pos
        self.rgb = color.rgb()
        self.r = qRed(self.rgb)
        self.g = qGreen(self.rgb)
        self.b = qBlue(self.rgb)


class ColorStops(object):
    def __init__(self):
        self._stops = []
        self.stops = []
    
    def insert(self, pos, color):
        if pos < 0. or pos > 1.:
            return
        if len(self._stops) == 0:
            index = 0
            self._stops = [None]
        else:
            index = self.findUpper(pos)
            if index == len(self._stops) or\
               abs(self._stops[index].pos-pos) >= .001:
                self._stops.append(None)
                for i in range(len(self._stops)-1, index, -1):
                    self._stops[i] = self._stops[i-1]
        self._stops[index] = ColorStop(pos, color)
    
    def stops(self):
        return [stop.pos for stop in self._stops]
    
    def findUpper(self, pos):
        index = 0
        n = len(self._stops)
        
        stops = self._stops
        
        while n > 0:
            half = n >> 1
            middle = index + half
            if stops[middle].pos <= pos:
                index = middle + 1
                n -= half + 1
            else:
                n = half
        return index
    
    def rgb(self, mode, pos):
        if pos <= 0.:
            return self._stops[0].rgb
        if pos >= 1.0:
            return self._stops[-1].rgb
        
        index = self.findUpper(pos)
        if mode == QwtLinearColorMap.FixedColors:
            return self._stops[index-1].rgb
        else:
            s1 = self._stops[index-1]
            s2 = self._stops[index]
            ratio = (pos-s1.pos)/(s2.pos-s1.pos)
            r = s1.r + round(ratio*(s2.r-s1.r))
            g = s1.g + round(ratio*(s2.g-s1.g))
            b = s1.b + round(ratio*(s2.b-s1.b))
            return qRgb(r, g, b)
        
        


class QwtColorMap(object):
    
    # enum Format
    RGB, Indexed = range(2)
    
    def __init__(self, format_=0):
        self.__format = format_
    
    def color(self, interval, value):
        if self.__format == self.RGB:
            return QColor(self.rgb(interval, value))
        else:
            index = self.colorIndex(interval, value)
            return self.colorTable(interval)[index]
    
    def format_(self):
        return self.__format
    
    def colorTable(self, interval):
        table = [0L] * 256
        if interval.isValid():
            step = interval.width()/(len(table)-1)
            for i in range(len(table)):
                table[i] = self.rgb(interval, interval.minValue()+step*i)
        return table


class QwtLinearColorMap_PrivateData(object):
    def __init__(self):
        self.colorStops = None
        self.mode = None


class QwtLinearColorMap(QwtColorMap):
    
    # enum Mode
    FixedColors, ScaledColors = range(2)
    
    def __init__(self, *args):
        color1, color2 = QColor(Qt.blue), QColor(Qt.yellow)
        if len(args) == 1:
            format_, = args
        elif len(args) == 3:
            color1, color2, format_ = args
        elif len(args) == 0:
            format_ = QwtColorMap.RGB
        else:
            raise TypeError("%s() takes 0, 1, or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
        super(QwtLinearColorMap, self).__init__(format_)
        self.__data = QwtLinearColorMap_PrivateData()
        self.__data.mode = self.ScaledColors
        self.setColorInterval(color1, color2)
    
    def setMode(self, mode):
        self.__data.mode = mode
    
    def mode(self):
        return self.__data.mode
    
    def setColorInterval(self, color1, color2):
        self.__data.colorStops = ColorStops()
        self.__data.colorStops.insert(0., color1)
        self.__data.colorStops.insert(1., color2)
    
    def addColorStop(self, value, color):
        if value >= 0. and value <= 1.:
            self.__data.colorStops.insert(value, color)
    
    def colorStops(self):
        return self.__data.colorStops.stops()
    
    def color1(self):
        return QColor(self.__data.colorStops.rgb(self.__data.mode, 0.))
    
    def color2(self):
        return QColor(self.__data.colorStops.rgb(self.__data.mode, 1.))
    
    def rgb(self, interval, value):
        if qIsNaN(value):
            return qRgba(0, 0, 0, 0)
        width = interval.width()
        ratio = 0.
        if width > 0.:
            ratio = (value-interval.minValue())/width
        return self.__data.colorStops.rgb(self.__data.mode, ratio)
    
    def colorIndex(self, interval, value):
        width = interval.width()
        if qIsNaN(value) or width <= 0. or value <= interval.minValue():
            return 0
        if value >= interval.maxValue():
            return 255
        ratio = (value-interval.minValue())/width
        if self.__data.mode == self.FixedColors:
            index = ratio*255
        else:
            index = round(ratio*255)
        return index
    

class QwtAlphaColorMap_PrivateData(object):
    def __init__(self):
        self.color = None
        self.rgb = None

class QwtAlphaColorMap(QwtColorMap):
    def __init__(self, color):
        super(QwtAlphaColorMap, self).__init__(QwtColorMap.RGB)
        self.__data = QwtAlphaColorMap_PrivateData()
        self.__data.color = color
        self.__data.rgb = color.rgb() & qRgba(255, 255, 255, 0)
    
    def setColor(self, color):
        self.__data.color = color
        self.__data.rgb = color.rgb()
    
    def color(self):
        return self.__data.color()
    
    def rgb(self, interval, value):
        width = interval.width()
        if not qIsNaN(value) and width >= 0.:
            ratio = (value-interval.minValue())/width
            alpha = round(255*ratio)
            if alpha < 0:
                alpha = 0
            if alpha > 255:
                alpha = 255
            return self.__data.rgb | (alpha << 24)
        return self.__data.rgb

