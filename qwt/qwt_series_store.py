# -*- coding: utf-8 -*-

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
        self.d_series = None
    
    def data(self):
        return self.d_series
        
    def sample(self, index):
        if self.d_series:
            return self.d_series.sample(index)
        else:
            #TODO: not implemented!
            return
    
    def setData(self, series):
        if self.d_series != series:
            self.d_series = series
            self.dataChanged()
    
    def dataSize(self):
        if self.d_series is None:
            return 0
        return self.d_series.size()
    
    def dataRect(self):
        if self.d_series is None:
            return QRectF(1.0, 1.0, -2.0, -2.0)
        return self.d_series.boundingRect()
    
    def setRectOfInterest(self, rect):
        if self.d_series:
            self.d_series.setRectOfInterest(rect)
    
    def swapData(self, series):
        swappedSeries = self.d_series
        self.d_series = series
        return swappedSeries
