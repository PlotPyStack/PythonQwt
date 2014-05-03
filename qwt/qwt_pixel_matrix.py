# -*- coding: utf-8 -*-


from qwt.qt.QtCore import QBitArray


class QwtPixelMatrix(QBitArray):
    def __init__(self, rect):
        QBitArray.__init__(self, max([rect.width()*rect.height(), 0]))
        self.d_rect = rect
    
    def setRect(self, rect):
        if rect != self.d_rect:
            self.d_rect = rect
            sz = max([rect.width()*rect.height(), 0])
            self.resize(sz)
        self.fill(False)
    
    def rect(self):
        return self.d_rect
    
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
        dx = x - self.d_rect.x()
        if dx < 0 or dx >= self.d_rect.width():
            return -1
        dy = y - self.d_rect.y()
        if dy < 0 or dy >= self.d_rect.height():
            return -1
        return dy*self.d_rect.width()+dx
        