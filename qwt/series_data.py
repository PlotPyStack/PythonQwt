# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
Series data
-----------

QwtSeriesData
~~~~~~~~~~~~~

.. autoclass:: QwtSeriesData
   :members:
   
QwtPointArrayData
~~~~~~~~~~~~~~~~~

.. autoclass:: QwtPointArrayData
   :members:
"""

from qwt.qt.QtCore import QRectF, QPointF

import numpy as np


class QwtSeriesData(object):
    """
    Abstract interface for iterating over samples

    `PythonQwt` offers several implementations of the QwtSeriesData API,
    but in situations, where data of an application specific format
    needs to be displayed, without having to copy it, it is recommended
    to implement an individual data access.

    A subclass of `QwtSeriesData` must implement: 

      - size():
        
        Should return number of data points.

     - sample()

        Should return values x and y values of the sample at specific position
        as QPointF object.

     - boundingRect()

        Should return the bounding rectangle of the data series.
        It is used for autoscaling and might help certain algorithms for 
        displaying the data.
        The member `_boundingRect` is intended for caching the calculated 
        rectangle.
    """
    def __init__(self):
        self._boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
    
    def setRectOfInterest(self, rect):
        """
        Set a the "rect of interest"

        QwtPlotSeriesItem defines the current area of the plot canvas
        as "rectangle of interest" ( QwtPlotSeriesItem::updateScaleDiv() ).
        It can be used to implement different levels of details.

        The default implementation does nothing.
   
        :param QRectF rect: Rectangle of interest
        """
        pass
    
    def size(self):
        """
        :return: Number of samples
        """
        pass
        
    def sample(self, i):
        """
        Return a sample
        
        :param int i: Index
        :return: Sample at position i
        """
        pass
    
    def boundingRect(self):
        """
        Calculate the bounding rect of all samples

        The bounding rect is necessary for autoscaling and can be used
        for a couple of painting optimizations.

        :return: Bounding rectangle
        """
        pass


class QwtPointArrayData(QwtSeriesData):
    """
    Interface for iterating over two array objects
    
    .. py:class:: QwtCQwtPointArrayDataolorMap(x, y, [size=None])
    
        :param x: Array of x values
        :type x: list or tuple or numpy.array
        :param y: Array of y values
        :type y: list or tuple or numpy.array
        :param int size: Size of the x and y arrays
    """
    def __init__(self, x=None, y=None, size=None):
        QwtSeriesData.__init__(self)
        if x is None and y is not None:
            x = np.arange(len(y))
        elif y is None and x is not None:
            y = x
            x = np.arange(len(y))
        elif x is None and y is None:
            x = np.array([])
            y = np.array([])
        if isinstance(x, (tuple, list)):
            x = np.array(x)
        if isinstance(y, (tuple, list)):
            y = np.array(y)
        if size is not None:
            x = np.resize(x, (size, ))
            y = np.resize(y, (size, ))
        self.__x = x
        self.__y = y
        
    def boundingRect(self):
        """
        Calculate the bounding rectangle

        The bounding rectangle is calculated once by iterating over all
        points and is stored for all following requests.

        :return: Bounding rectangle
        """
        xmin = self.__x.min()
        xmax = self.__x.max()
        ymin = self.__y.min()
        ymax = self.__y.max()
        return QRectF(xmin, ymin, xmax-xmin, ymax-ymin)
    
    def size(self):
        """
        :return: Size of the data set
        """
        return min([self.__x.size, self.__y.size])
    
    def sample(self, index):
        """
        :param int index: Index
        :return: Sample at position `index`
        """
        return QPointF(self.__x[index], self.__y[index])
    
    def xData(self):
        """
        :return: Array of the x-values
        """
        return self.__x
        
    def yData(self):
        """
        :return: Array of the y-values
        """
        return self.__y
