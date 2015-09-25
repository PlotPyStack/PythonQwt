# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtLegendLabel
--------------

.. autoclass:: QwtLegendLabel
   :members:
"""

from qwt.text import QwtTextLabel
from qwt.legend_data import QwtLegendData

from qwt.qt.QtGui import (QStyleOption, QStyle, QPixmap, QApplication,
                          QPainter, qDrawWinButton)
from qwt.qt.QtCore import Signal, Qt, QSize, QRect, QPoint


BUTTONFRAME = 2
MARGIN = 2


def buttonShift(w):
    option = QStyleOption()
    option.initFrom(w)
    ph = w.style().pixelMetric(QStyle.PM_ButtonShiftHorizontal, option, w)
    pv = w.style().pixelMetric(QStyle.PM_ButtonShiftVertical, option, w)
    return QSize(ph, pv)


class QwtLegendLabel_PrivateData(object):
    def __init__(self):
        self.itemMode = QwtLegendData.ReadOnly
        self.isDown = False
        self.spacing = MARGIN
        self.legendData = QwtLegendData()
        self.icon = QPixmap()
        

class QwtLegendLabel(QwtTextLabel):
    """A widget representing something on a QwtLegend."""
    
    SIG_CLICKED = Signal()
    SIG_PRESSED = Signal()
    SIG_RELEASED = Signal()
    SIG_CHECKED = Signal(bool)
    
    def __init__(self, parent=None):
        QwtTextLabel.__init__(self, parent)
        self.__data = QwtLegendLabel_PrivateData()
        self.setMargin(MARGIN)
        self.setIndent(MARGIN)
        
    def setData(self, legendData):
        """
        Set the attributes of the legend label
        
        :param QwtLegendData legendData: Attributes of the label

        .. seealso::
        
            :py:meth:`data()`
        """
        self.__data.legendData = legendData
        doUpdate = self.updatesEnabled()
        self.setUpdatesEnabled(False)
        self.setText(legendData.title())
        icon = legendData.icon()
        if icon is not None:
            self.setIcon(icon.toPixmap())
        if legendData.hasRole(QwtLegendData.ModeRole):
            self.setItemMode(legendData.mode())
        if doUpdate:
            self.setUpdatesEnabled(True)
            self.update()
    
    def data(self):
        """
        :return: Attributes of the label

        .. seealso::
        
            :py:meth:`setData()`, :py:meth:`qwt.plot.QwtPlotItem.legendData()`
        """
        return self.__data.legendData
    
    def setText(self, text):
        """
        Set the text to the legend item
        
        :param qwt.text.QwtText text: Text label

        .. seealso::
        
            :py:meth:`text()`
        """
        flags = Qt.AlignLeft|Qt.AlignVCenter|Qt.TextExpandTabs|Qt.TextWordWrap
        txt = text  #TODO: WTF?
        txt.setRenderFlags(flags)
        QwtTextLabel.setText(self, text)
    
    def setItemMode(self, mode):
        """
        Set the item mode.
        The default is `QwtLegendData.ReadOnly`.
        
        :param int mode: Item mode

        .. seealso::
        
            :py:meth:`itemMode()`
        """
        if mode != self.__data.itemMode:
            self.__data.itemMode = mode
            self.__data.isDown = False
            self.setFocusPolicy(Qt.TabFocus if mode != QwtLegendData.ReadOnly
                                else Qt.NoFocus)
            self.setMargin(BUTTONFRAME+MARGIN)
            self.updateGeometry()
    
    def itemMode(self):
        """
        :return: Item mode

        .. seealso::
        
            :py:meth:`setItemMode()`
        """
        return self.__data.itemMode
    
    def setIcon(self, icon):
        """
        Assign the icon
        
        :param QPixmap icon: Pixmap representing a plot item

        .. seealso::
        
            :py:meth:`icon()`, :py:meth:`qwt.plot.QwtPlotItem.legendIcon()`
        """
        self.__data.icon = icon
        indent = self.margin()+self.__data.spacing
        if icon.width() > 0:
            indent += icon.width()+self.__data.spacing
        self.setIndent(indent)
    
    def icon(self):
        """
        :return: Pixmap representing a plot item

        .. seealso::
        
            :py:meth:`setIcon()`
        """
        return self.__data.icon
    
    def setSpacing(self, spacing):
        """
        Change the spacing between icon and text
        
        :param int spacing: Spacing

        .. seealso::
        
            :py:meth:`spacing()`, :py:meth:`qwt.text.QwtTextLabel.margin()`
        """
        spacing = max([spacing, 0])
        if spacing != self.__data.spacing:
            self.__data.spacing = spacing
            indent = self.margin()+self.__data.spacing
            if self.__data.icon.width() > 0:
                indent += self.__data.icon.width()+self.__data.spacing
            self.setIndent(indent)
    
    def spacing(self):
        """
        :return: Spacing between icon and text

        .. seealso::
        
            :py:meth:`setSpacing()`
        """
        return self.__data.spacing
    
    def setChecked(self, on):
        """
        Check/Uncheck a the item
        
        :param bool on: check/uncheck

        .. seealso::
        
            :py:meth:`isChecked()`, :py:meth:`setItemMode()`
        """
        if self.__data.itemMode == QwtLegendData.Checkable:
            isBlocked = self.signalsBlocked()
            self.blockSignals(True)
            self.setDown(on)
            self.blockSignals(isBlocked)
    
    def isChecked(self):
        """
        :return: true, if the item is checked

        .. seealso::
        
            :py:meth:`setChecked()`
        """
        return self.__data.itemMode == QwtLegendData.Checkable and self.isDown()
    
    def setDown(self, down):
        """
        Set the item being down
        
        :param bool on: true, if the item is down

        .. seealso::
        
            :py:meth:`isDown()`
        """
        if down == self.__data.isDown:
            return
        self.__data.isDown = down
        self.update()
        if self.__data.itemMode == QwtLegendData.Clickable:
            if self.__data.isDown:
                self.SIG_PRESSED.emit()
            else:
                self.SIG_RELEASED.emit()
                self.SIG_CLICKED.emit()
        if self.__data.itemMode == QwtLegendData.Checkable:
            self.SIG_CHECKED.emit(self.__data.isDown)
    
    def isDown(self):
        """
        :return: true, if the item is down

        .. seealso::
        
            :py:meth:`setDown()`
        """
        return self.__data.isDown
    
    def sizeHint(self):
        """
        :return: a size hint
        """
        sz = QwtTextLabel.sizeHint(self)
        sz.setHeight(max([sz.height(), self.__data.icon.height()+4]))
        if self.__data.itemMode != QwtLegendData.ReadOnly:
            sz += buttonShift(self)
            sz = sz.expandedTo(QApplication.globalStrut())
        return sz
    
    def paintEvent(self, e):
        cr = self.contentsRect()
        painter = QPainter(self)
        painter.setClipRegion(e.region())
        if self.__data.isDown:
            qDrawWinButton(painter, 0, 0, self.width(), self.height(),
                           self.palette(), True)
        painter.save()
        if self.__data.isDown:
            shiftSize = buttonShift(self)
            painter.translate(shiftSize.width(), shiftSize.height())
        painter.setClipRect(cr)
        self.drawContents(painter)
        if not self.__data.icon.isNull():
            iconRect = QRect(cr)
            iconRect.setX(iconRect.x()+self.margin())
            if self.__data.itemMode != QwtLegendData.ReadOnly:
                iconRect.setX(iconRect.x()+BUTTONFRAME)
            iconRect.setSize(self.__data.icon.size())
            iconRect.moveCenter(QPoint(iconRect.center().x(),
                                       cr.center().y()))
            painter.drawPixmap(iconRect, self.__data.icon)
        painter.restore()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.__data.itemMode == QwtLegendData.Clickable:
                self.setDown(True)
                return
            elif self.__data.itemMode == QwtLegendData.Checkable:
                self.setDown(not self.isDown())
                return
        QwtTextLabel.mousePressEvent(self, e)
    
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.__data.itemMode == QwtLegendData.Clickable:
                self.setDown(False)
                return
            elif self.__data.itemMode == QwtLegendData.Checkable:
                return
        QwtTextLabel.mouseReleaseEvent(self, e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Space:
            if self.__data.itemMode == QwtLegendData.Clickable:
                if not e.isAutoRepeat():
                    self.setDown(True)
                return
            elif self.__data.itemMode == QwtLegendData.Checkable:
                if not e.isAutoRepeat():
                    self.setDown(not self.isDown())
                return
        QwtTextLabel.keyPressEvent(self, e)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Space:
            if self.__data.itemMode == QwtLegendData.Clickable:
                if not e.isAutoRepeat():
                    self.setDown(False)
                return
            elif self.__data.itemMode == QwtLegendData.Checkable:
                return
        QwtTextLabel.keyReleaseEvent(self, e)
