# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtPixelMatrix
--------------

.. autoclass:: QwtPixelMatrix
   :members:
"""

from qwt.qt.QtCore import QBitArray


class QwtPixelMatrix(QBitArray):
    """
    A bit field corresponding to the pixels of a rectangle
    
    `QwtPixelMatrix` is intended to filter out duplicates in an
    unsorted array of points.
    
    .. py:class:: QwtGraphic(rect)
    
        Constructor
        
        :param QRect rect: Bounding rectangle for the matrix
    """
    def __init__(self, rect):
        QBitArray.__init__(self, max([rect.width()*rect.height(), 0]))
        self.__rect = rect
    
    def setRect(self, rect):
        """
        Set the bounding rectangle of the matrix
        
        :param QRect rect: Bounding rectangle
            
        .. note::
        
            All bits are cleared
        """
        if rect != self.__rect:
            self.__rect = rect
            sz = max([rect.width()*rect.height(), 0])
            self.resize(sz)
        self.fill(False)
    
    def rect(self):
        """
        :return: Bounding rectangle
        """
        return self.__rect
    
    def testPixel(self, x, y):
        """
        Test if a pixel has been set
            
        :param int x: X-coordinate
        :param int y: Y-coordinate
        :return: true, when pos is outside of rect(), or when the pixel has already been set.
        """
        idx = self.index(x, y)
        if idx >= 0:
            return self.testBit(idx)
        else:
            return True
    
    def testAndSetPixel(self, x, y, on):
        """
        Set a pixel and test if a pixel has been set before
        
        :param int x: X-coordinate
        :param int y: Y-coordinate
        :param bool on: Set/Clear the pixel
        :return: true, when pos is outside of rect(), or when the pixel was set before.
        """
        idx = self.index(x, y)
        if idx < 0:
            return True
        onBefore = self.testBit(idx)
        self.setBit(idx, on)
        return onBefore
    
    def index(self, x, y):
        """
        Calculate the index in the bit field corresponding to a position
        
        :param int x: X-coordinate
        :param int y: Y-coordinate
        :return: Index, when rect() contains pos - otherwise -1.
        """
        dx = x - self.__rect.x()
        if dx < 0 or dx >= self.__rect.width():
            return -1
        dy = y - self.__rect.y()
        if dy < 0 or dy >= self.__rect.height():
            return -1
        return dy*self.__rect.width()+dx
        