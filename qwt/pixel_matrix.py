# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

from qwt.qt.QtCore import QBitArray


class QwtPixelMatrix(QBitArray):
    def __init__(self, rect):
        QBitArray.__init__(self, max([rect.width()*rect.height(), 0]))
        self.__rect = rect
    
    def setRect(self, rect):
        if rect != self.__rect:
            self.__rect = rect
            sz = max([rect.width()*rect.height(), 0])
            self.resize(sz)
        self.fill(False)
    
    def rect(self):
        return self.__rect
    
    def testPixel(self, x, y):
        idx = self.index(x, y)
        if idx >= 0:
            return self.testBit(idx)
        else:
            return True
    
    def testAndSetPixel(self, x, y, on):
        idx = self.index(x, y)
        if idx < 0:
            return True
        onBefore = self.testBit(idx)
        self.setBit(idx, on)
        return onBefore
    
    def index(self, x, y):
        dx = x - self.__rect.x()
        if dx < 0 or dx >= self.__rect.width():
            return -1
        dy = y - self.__rect.y()
        if dy < 0 or dy >= self.__rect.height():
            return -1
        return dy*self.__rect.width()+dx
        