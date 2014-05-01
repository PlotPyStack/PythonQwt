# -*- coding: utf-8 -*-

from qwt.qwt_curve_fitter import QwtSplineCurveFitter
from qwt.qwt_text import QwtText
from qwt.qwt_plot import QwtPlotItem

from qwt.qt.QtGui import QPen, QBrush
from qwt.qt.QtCore import QSize, Qt

import numpy as np


def qwtUpdateLegendIconSize(curve):
    if curve.symbol() and\
       curve.testLegendAttribute(QwtPlotCurve.LegendShowSymbol):
        sz = curve.symbol().boundingRect().size()
        sz += QSize(2, 2)
        if curve.testLegendAttribute(QwtPlotCurve.LegendShowLine):
            w = np.ceil(1.5*sz.width())
            if w % 2:
                w += 1
            sz.setWidth(max([8, w]))
        curve.setLegendIconSize(sz)

def qwtVerifyRange(size, i1, i2):
    if size < 1:
        return 0
    i1 = max([0, min([i1, size-1])])
    i2 = max([0, min([i2, size-1])])
    if i1 > i2:
        i1, i2 = i2, i1
    return i2-i1+1


class QwtPlotCurve_PrivateData(object):
    def __init__(self):
        self.style = QwtPlotCurve.Lines
        self.baseLine = 0.
        self.symbol = None
        self.attributes = 0
        self.paintAttributes = QwtPlotCurve.ClipPolygons|QwtPlotCurve.FilterPoints
        self.legendAttributes = 0
        self.pen = QPen(Qt.black)
        self.brush = QBrush()
        self.curveFitter = QwtSplineCurveFitter()
        

class QwtPlotCurve(QwtPlotSeriesItem, QwtSeriesStore):
    
    # enum CurveStyle
    NoCurve = -1
    Lines, Sticks, Steps, Dots = range(4)
    UserCurve = 100
    
    # enum CurveAttribute
    Inverted = 0x01
    Fitted = 0x02
    
    # enum LegendAttribute
    LegendNoAttribute = 0x00
    LegendShowLine = 0x01
    LegendShowSymbol = 0x02
    LegendShowBrush = 0x04
    
    # enum PaintAttribute
    ClipPolygons = 0x01
    FilterPoints = 0x02
    MinimizeMemory = 0x04
    ImageBuffer = 0x08
    
    def __init__(self, title):
        if not isinstance(title, QwtText):
            title = QwtText(title)
        self.d_data = None
        QwtPlotSeriesItem.__init__(self, title)
        self.init()
        
    def init(self):
        self.setItemAttribute(QwtPlotItem.Legend)
        self.setItemAttribute(QwtPlotItem.AutoScale)
        self.d_data = QwtPlotCurve_PrivateData()
        self.setData(QwtPointSeriesData())
        self.setZ(20.)
    
    def rtti(self):
        return QwtPlotItem.Rtti_PlotCurve
        
    def setPaintAttribute(self, attribute, on):
        if on:
            self.d_data.paintAttributes |= attribute
        else:
            self.d_data.paintAttributes &= ~attribute
    
    def testPaintAttribute(self, attribute):
        return self.d_data.paintAttributes & attribute
    
    def setLegendAttribute(self, attribute, on):
        if on != self.testLegendAttribute(attribute):
            if on:
                self.d_data.legendAttributes |= attribute
            else:
                self.d_data.legendAttributes &= ~attribute
            qwtUpdateLegendIconSize(self)
            self.legendChanged()
    
    def testLegendAttribute(self, attribute):
        return self.d_data.legendAttributes & attribute
    
    def setStyle(self, style):
        if style != self.d_data.style:
            self.d_data.style = style
            self.legendChanged()
            self.itemChanged()
    
    def style(self):
        return self.d_data.style
    
    def setSymbol(self, symbol):
        if symbol != self.d_data.symbol:
            self.d_data.symbol = symbol
            qwtUpdateLegendIconSize(self)
            self.legendChanged()
            self.itemChanged()
    
    def symbol(self):
        return self.d_data.symbol
    
    def setPen(self, *args):
        if len(args) == 3:
            color, width, style = args
        elif len(args) == 1:
            pen, = args
        if pen != self.d_data.pen:
            self.d_data.pen = pen
            self.legendChanged()
            self.itemChanged()
    
    def pen(self):
        return self.d_data.pen
    
    def setBrush(self, brush):
        if brush != self.d_data.brush:
            self.d_data.brush = brush
            self.legendChanged()
            self.itemChanged()
    
    def brush(self):
        return self.d_data.brush
        
    def drawSeries(self, painter, xMap, yMap, canvasRect, from_, to):
        numSamples = self.dataSize()
        if not painter or numSamples <= 0:
            return
        if to < 0:
            to = numSamples-1
        if qwtVerifyRange(numSamples, from_, to) > 0:
            painter.save()
            painter.setPen(self.d_data.pen)
            self.drawCurve(painter, self.d_data.style, xMap, yMap, canvasRect,
                           from_, to)
            painter.restore()
            if self.d_data.symbol and\
               self.d_data.symbol.style() != QwtSymbol.NoSymbol:
                painter.save()
                self.drawSymbols(painter, self.d_data.symbol,
                                 xMap, yMap, canvasRect, from_, to)
                painter.restore()

