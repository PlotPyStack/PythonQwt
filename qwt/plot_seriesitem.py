# -*- coding: utf-8 -*-

from qwt.plot import QwtPlotItem, QwtPlotItem_PrivateData
from qwt.text import QwtText
from qwt.series_store import QwtAbstractSeriesStore

from qwt.qt.QtCore import Qt, QRectF


class QwtPlotSeriesItem_PrivateData(QwtPlotItem_PrivateData):
    def __init__(self):
        QwtPlotItem_PrivateData.__init__(self)
        self.orientation = Qt.Vertical


class QwtPlotSeriesItem(QwtPlotItem, QwtAbstractSeriesStore):
    def __init__(self, title):
        QwtAbstractSeriesStore.__init__(self)
        if not isinstance(title, QwtText):
            title = QwtText(title)
        QwtPlotItem.__init__(self, title)
        self.__data = QwtPlotSeriesItem_PrivateData()
        
    def setOrientation(self, orientation):
        if self.__data.orientation != orientation:
            self.__data.orientation = orientation
            self.legendChanged()
            self.itemChanged()
    
    def orientation(self):
        return self.__data.orientation
    
    def draw(self, painter, xMap, yMap, canvasRect):
        self.drawSeries(painter, xMap, yMap, canvasRect, 0, -1)
    
    def boundingRect(self):
        return self.dataRect()
    
    def updateScaleDiv(self, xScaleDiv, yScaleDiv):
        rect = QRectF(xScaleDiv.lowerBound(), yScaleDiv.lowerBound(),
                      xScaleDiv.range(), yScaleDiv.range())
        self.setRectOfInterest(rect)
        
    def dataChanged(self):
        self.itemChanged()
