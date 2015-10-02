# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtSeriesStore
--------------

.. autoclass:: QwtSeriesStore
   :members:
"""

from qwt.qt.QtCore import QRectF


class QwtSeriesStore(object):
    """
    Class storing a `QwtSeriesData` object

    `QwtSeriesStore` and `QwtPlotSeriesItem` are intended as base classes for 
    all plot items iterating over a series of samples.
    """
    def __init__(self):
        self.__series = None
    
    def setData(self, series):
        """
        Assign a series of samples

        :param qwt.series_data.QwtSeriesData series: Data

        .. warning::
        
            The item takes ownership of the data object, deleting it 
            when its not used anymore.
        """
        if self.__series != series:
            self.__series = series
            self.dataChanged()
    
    def data(self):
        """
        :return: the series data
        """
        return self.__series
        
    def sample(self, index):
        """
        :param int index: Index
        :return: Sample at position index
        """
        if self.__series:
            return self.__series.sample(index)
        else:
            return
    
    def dataSize(self):
        """
        :return: Number of samples of the series
        
        .. seealso::
        
            :py:meth:`setData()`, 
            :py:meth:`qwt.series_data.QwtSeriesData.size()`
        """
        if self.__series is None:
            return 0
        return self.__series.size()
    
    def dataRect(self):
        """
        :return: Bounding rectangle of the series or an invalid rectangle, when no series is stored
        
        .. seealso::
        
            :py:meth:`qwt.series_data.QwtSeriesData.boundingRect()`
        """
        if self.__series is None or self.dataSize() == 0:
            return QRectF(1.0, 1.0, -2.0, -2.0)
        return self.__series.boundingRect()
    
    def setRectOfInterest(self, rect):
        """
        Set a the "rect of interest" for the series
        
        :param QRectF rect: Rectangle of interest
        
        .. seealso::
        
            :py:meth:`qwt.series_data.QwtSeriesData.setRectOfInterest()`
        """
        if self.__series:
            self.__series.setRectOfInterest(rect)
    
    def swapData(self, series):
        """
        Replace a series without deleting the previous one
        
        :param qwt.series_data.QwtSeriesData series: New series
        :return: Previously assigned series
        """
        swappedSeries = self.__series
        self.__series = series
        return swappedSeries
