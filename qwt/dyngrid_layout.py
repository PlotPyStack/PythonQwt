# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see qwt/LICENSE for details)

from qwt.qt.QtGui import QLayout
from qwt.qt.QtCore import Qt, QRect, QSize


class QwtDynGridLayout_PrivateData(object):
    def __init__(self):
        self.isDirty = True
        self.maxColumns = 0
        self.numRows = 0
        self.numColumns = 0
        self.expanding = Qt.Orientations()
        self.itemSizeHints = []
        self.itemList = []
    
    def updateLayoutCache(self):
        self.itemSizeHints = [it.sizeHint() for it in self.itemList]
        self.isDirty = False
    
class QwtDynGridLayout(QLayout):
    def __init__(self, *args):
        self.__data = None
        parent = None
        margin = 0
        spacing = -1
        if len(args) in (2, 3):
            parent, margin = args[:2]
            if len(args) == 3:
                spacing = args[-1]
        elif len(args) == 1:
            if isinstance(args[0], int):
                spacing, = args
            else:
                parent, = args
        elif len(args) != 0:
            raise TypeError("%s() takes 0, 1, 2 or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
        QLayout.__init__(self, parent)
        self.__data = QwtDynGridLayout_PrivateData()
        self.setSpacing(spacing)
        self.setMargin(margin)
        
    def invalidate(self):
        self.__data.isDirty = True
        QLayout.invalidate(self)
    
    def setMaxColumns(self, maxColumns):
        self.__data.maxColumns = maxColumns
    
    def maxColumns(self):
        return self.__data.maxColumns
    
    def addItem(self, item):
        self.__data.itemList.append(item)
        self.invalidate()
    
    def isEmpty(self):
        return self.count() == 0
    
    def itemCount(self):
        return self.count()
    
    def itemAt(self, index):
        if index < 0 or index >= len(self.__data.itemList):
            return
        return self.__data.itemList[index]
    
    def takeAt(self, index):
        if index < 0 or index >= len(self.__data.itemList):
            return
        self.__data.isDirty = True
        return self.__data.itemList.pop(index)
    
    def count(self):
        return len(self.__data.itemList)
    
    def setExpandingDirections(self, expanding):
        self.__data.expanding = expanding
    
    def expandingDirections(self):
        return self.__data.expanding
    
    def setGeometry(self, rect):
        QLayout.setGeometry(self, rect)
        if self.isEmpty():
            return
        self.__data.numColumns = self.columnsForWidth(rect.width())
        self.__data.numRows = self.itemCount()/self.__data.numColumns
        if self.itemCount() % self.__data.numColumns:
            self.__data.numRows += 1
        itemGeometries = self.layoutItems(rect, self.__data.numColumns)
        for it, geo in zip(self.__data.itemList, itemGeometries):
            it.setGeometry(geo)
    
    def columnsForWidth(self, width):
        if self.isEmpty():
            return 0
        maxColumns = self.itemCount()
        if self.__data.maxColumns > 0:
            maxColumns = min([self.__data.maxColumns, maxColumns])
        if self.maxRowWidth(maxColumns) <= width:
            return maxColumns
        for numColumns in range(2, maxColumns+1):
            rowWidth = self.maxRowWidth(numColumns)
            if rowWidth > width:
                return numColumns-1
        return 1
    
    def maxRowWidth(self, numColumns):
        colWidth = [0] * numColumns
        if self.__data.isDirty:
            self.__data.updateLayoutCache()
        for index, hint in enumerate(self.__data.itemSizeHints):
            col = index % numColumns
            colWidth[col] = max([colWidth[col], hint.width()])
        return 2*self.margin()+(numColumns-1)*self.spacing()+sum(colWidth)
    
    def maxItemWidth(self):
        if self.isEmpty():
            return 0
        if self.__data.isDirty:
            self.__data.updateLayoutCache()
        return max([hint.width() for hint in self.__data.itemSizeHints])
    
    def layoutItems(self, rect, numColumns):
        itemGeometries = []
        if numColumns == 0 or self.isEmpty():
            return itemGeometries
        numRows = self.itemCount()/numColumns
        if numColumns % self.itemCount():
            numRows += 1
        if numRows == 0:
            return itemGeometries
        rowHeight = [0]*numRows
        colWidth = [0]*numColumns
        self.layoutGrid(numColumns, rowHeight, colWidth)
        expandH = self.expandingDirections() & Qt.Horizontal
        expandV = self.expandingDirections() & Qt.Vertical
        if expandH or expandV:
            self.stretchGrid(rect, numColumns, rowHeight, colWidth)
        maxColumns = self.__data.maxColumns
        self.__data.maxColumns = numColumns
        alignedRect = self.alignmentRect(rect)
        self.__data.maxColumns = maxColumns
        xOffset = 0 if expandH else alignedRect.x()
        yOffset = 0 if expandV else alignedRect.y()
        colX = [0] * numColumns
        rowY = [0] * numRows
        xySpace = self.spacing()
        rowY[0] = yOffset + self.margin()
        for r in range(1, numRows):
            rowY[r] = rowY[r-1] + rowHeight[r-1] + xySpace
        colX[0] = xOffset + self.margin()
        for c in range(1, numColumns):
            colX[c] = colX[c-1] + colWidth[c-1] + xySpace
        itemCount = len(self.__data.itemList)
        for i in range(itemCount):
            row = i/numColumns
            col = i % numColumns
            itemGeometry = QRect(colX[col], rowY[row],
                                 colWidth[col], rowHeight[row])
            itemGeometries.append(itemGeometry)
        return itemGeometries
        
    def layoutGrid(self, numColumns, rowHeight, colWidth):
        if numColumns <= 0:
            return
        if self.__data.isDirty:
            self.__data.updateLayoutCache()
        for index in range(len(self.__data.itemSizeHints)):
            row = index/numColumns
            col = index % numColumns
            size = self.__data.itemSizeHints[index]
            if col == 0:
                rowHeight[row] = size.height()
            else:
                rowHeight[row] = max([rowHeight[row], size.height()])
            if row == 0:
                colWidth[col] = size.width()
            else:
                colWidth[col] = max([colWidth[col], size.width()])
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        if self.isEmpty():
            return 0
        numColumns = self.columnsForWidth(width)
        numRows = self.itemCount()/numColumns
        if self.itemCount() % numColumns:
            numRows += 1
        rowHeight = [0] * numRows
        colWidth = [0] * numColumns
        self.layoutGrid(numColumns, rowHeight, colWidth)
        return 2*self.margin()+(numRows-1)*self.spacing()+sum(rowHeight)
    
    def stretchGrid(self, rect, numColumns, rowHeight, colWidth):
        if numColumns == 0 or self.isEmpty():
            return
        expandH = self.expandingDirections() & Qt.Horizontal
        expandV = self.expandingDirections() & Qt.Vertical
        if expandH:
            xDelta = rect.width()-2*self.margin()-(numColumns-1)*self.spacing()
            for col in range(numColumns):
                xDelta -= colWidth[col]
            if xDelta > 0:
                for col in range(numColumns):
                    space = xDelta/(numColumns-col)
                    colWidth[col] += space
                    xDelta -= space
        if expandV:
            numRows = self.itemCount()/numColumns
            if self.itemCount() % numColumns:
                numRows += 1
            yDelta = rect.height()-2*self.margin()-(numRows-1)*self.spacing()
            for row in range(numRows):
                yDelta -= rowHeight[row]
            if yDelta > 0:
                for row in range(numRows):
                    space = yDelta/(numRows-row)
                    rowHeight[row] += space
                    yDelta -= space
        
    def sizeHint(self):
        if self.isEmpty():
            return QSize()
        numColumns = self.itemCount()
        if self.__data.maxColumns > 0:
            numColumns = min([self.__data.maxColumns, numColumns])
        numRows = self.itemCount()/numColumns
        if self.itemCount() % numColumns:
            numRows += 1
        rowHeight = [0] * numRows
        colWidth = [0] * numColumns
        self.layoutGrid(numColumns, rowHeight, colWidth)
        h = 2*self.margin()+(numRows-1)*self.spacing()+sum(rowHeight)
        w = 2*self.margin()+(numColumns-1)*self.spacing()+sum(colWidth)
        return QSize(w, h)
    
    def numRows(self):
        return self.__data.numRows
    
    def numColumns(self):
        return self.__data.numColumns
