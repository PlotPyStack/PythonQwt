# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see qwt/LICENSE for details)

from qwt.qt.QtCore import QRectF


class QwtAbstractSeriesStore(object):
    def dataChanged(self):
        raise NotImplementedError
    
    def dataSize(self):
        raise NotImplementedError
    
    def dataRect(self):
        raise NotImplementedError
    
    def setRectOfInterest(self, rect):
        raise NotImplementedError


class QwtSeriesStore(QwtAbstractSeriesStore):
    def __init__(self):
        self.__series = None
    
    def data(self):
        return self.__series
        
    def sample(self, index):
        if self.__series:
            return self.__series.sample(index)
        else:
            #TODO: not implemented!
            return
    
    def setData(self, series):
        if self.__series != series:
            self.__series = series
            self.dataChanged()
    
    def dataSize(self):
        if self.__series is None:
            return 0
        return self.__series.size()
    
    def dataRect(self):
        if self.__series is None or self.dataSize() == 0:
            return QRectF(1.0, 1.0, -2.0, -2.0)
        return self.__series.boundingRect()
    
    def setRectOfInterest(self, rect):
        if self.__series:
            self.__series.setRectOfInterest(rect)
    
    def swapData(self, series):
        swappedSeries = self.__series
        self.__series = series
        return swappedSeries
