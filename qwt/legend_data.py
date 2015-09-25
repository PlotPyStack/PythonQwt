# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtLegendData
-------------

.. autoclass:: QwtLegendData
   :members:
"""

from qwt.text import QwtText


class QwtLegendData(object):
    """
    Attributes of an entry on a legend
    
    `QwtLegendData` is an abstract container ( like `QAbstractModel` )
    to exchange attributes, that are only known between to 
    the plot item and the legend. 
      
    By overloading `QwtPlotItem.legendData()` any other set of attributes
    could be used, that can be handled by a modified ( or completely 
    different ) implementation of a legend.
    
    .. seealso::
    
        :py:class:`qwt.legend.QwtLegend`
    
    .. note::
    
        The stockchart example implements a legend as a tree 
        with checkable items
    """
    
    # enum Mode
    ReadOnly, Clickable, Checkable = list(range(3))
    
    # enum Role
    ModeRole, TitleRole, IconRole = list(range(3))
    UserRole = 32
    
    def __init__(self):
        self.__map = {}
    
    def setValues(self, map_):
        """
        Set the legend attributes
        
        :param dict map\_: Values

        .. seealso::
        
            :py:meth:`values()`
        """
        self.__map = map_
    
    def values(self):
        """
        :return: Legend attributes

        .. seealso::
        
            :py:meth:`setValues()`
        """
        return self.__map
    
    def hasRole(self, role):
        """
        :param int role: Attribute role
        :return: True, when the internal map has an entry for role
        """
        return role in self.__map
        
    def setValue(self, role, data):
        """
        Set an attribute value
        
        :param int role: Attribute role
        :param QVariant data: Attribute value

        .. seealso::
        
            :py:meth:`value()`
        """
        self.__map[role] = data
    
    def value(self, role):
        """
        :param int role: Attribute role
        :return: Attribute value for a specific role

        .. seealso::
        
            :py:meth:`setValue()`
        """
        return self.__map.get(role)
    
    def isValid(self):
        """
        :return: True, when the internal map is empty
        """
        return len(self.__map) != 0
    
    def title(self):
        """
        :return: Value of the TitleRole attribute
        """
        titleValue = self.value(QwtLegendData.TitleRole)
        if isinstance(titleValue, QwtText):
            text = titleValue
        else:
            text.setText(titleValue)
        return text
    
    def icon(self):
        """
        :return: Value of the IconRole attribute
        """
        return self.value(QwtLegendData.IconRole)
    
    def mode(self):
        """
        :return: Value of the ModeRole attribute
        """
        modeValue = self.value(QwtLegendData.ModeRole)
        if isinstance(modeValue, int):
            return modeValue
        return QwtLegendData.ReadOnly
