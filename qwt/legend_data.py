# -*- coding: utf-8 -*-

from qwt.text import QwtText


class QwtLegendData(object):
    
    # enum Mode
    ReadOnly, Clickable, Checkable = range(3)
    
    # enum Role
    ModeRole, TitleRole, IconRole = range(3)
    UserRole = 32
    
    def __init__(self):
        self.__map = {}
    
    def setValues(self, map_):
        self.__map = map_
    
    def values(self):
        return self.__map
    
    def hasRole(self, role):
        return role in self.__map
        
    def setValue(self, role, data):
        self.__map[role] = data
    
    def value(self, role):
        return self.__map.get(role)
    
    def isValid(self):
        return len(self.__map) != 0
    
    def title(self):
        titleValue = self.value(QwtLegendData.TitleRole)
        if isinstance(titleValue, QwtText):
            text = titleValue
        else:
            text.setText(titleValue)
        return text
    
    def icon(self):
        return self.value(QwtLegendData.IconRole)
    
    def mode(self):
        modeValue = self.value(QwtLegendData.ModeRole)
        if isinstance(modeValue, int):
            return modeValue
        return QwtLegendData.ReadOnly
