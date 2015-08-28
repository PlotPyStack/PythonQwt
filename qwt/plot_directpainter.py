# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

from qwt.qt.QtGui import QPainter, QRegion
from qwt.qt.QtCore import QObject, QT_VERSION, Qt, QEvent

from qwt.plot import QwtPlotItem
from qwt.plot_canvas import QwtPlotCanvas


def qwtRenderItem(painter, canvasRect, seriesItem, from_, to):
    #TODO: A minor performance improvement is possible with caching the maps
    plot = seriesItem.plot()
    xMap = plot.canvasMap(seriesItem.xAxis())
    yMap = plot.canvasMap(seriesItem.yAxis())
    painter.setRenderHint(QPainter.Antialiasing,
                      seriesItem.testRenderHint(QwtPlotItem.RenderAntialiased))
    seriesItem.drawSeries(painter, xMap, yMap, canvasRect, from_, to)


def qwtHasBackingStore(canvas):
    return canvas.testPaintAttribute(QwtPlotCanvas.BackingStore)\
           and canvas.backingStore()


class QwtPlotDirectPainter_PrivateData(object):
    def __init__(self):
        self.attributes = 0
        self.hasClipping = False
        self.seriesItem = None  # QwtPlotSeriesItem
        self.clipRegion = QRegion()
        self.painter = QPainter()
        self.from_ = None
        self.to = None


class QwtPlotDirectPainter(QObject):
    
    # enum Attribute
    AtomicPainter = 0x01
    FullRepaint = 0x02
    CopyBackingStore = 0x04
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.__data = QwtPlotDirectPainter_PrivateData()
    
    def setAttribute(self, attribute, on=True):
        if self.testAttribute(attribute) != on:
            self.__data.attributes |= attribute
        else:
            self.__data.attributes &= ~attribute
        if attribute == self.AtomicPainter and on:
            self.reset()
    
    def testAttribute(self, attribute):
        return self.__data.attributes & attribute
    
    def setClipping(self, enable):
        self.__data.hasClipping = enable
    
    def hasClipping(self):
        return self.__data.hasClipping
    
    def setClipRegion(self, region):
        self.__data.clipRegion = region
        self.__data.hasClipping = True
    
    def clipRegion(self):
        return self.__data.clipRegion
    
    def drawSeries(self, seriesItem, from_, to):
        """When observing an measurement while it is running, new points have 
        to be added to an existing seriesItem. drawSeries() can be used to 
        display them avoiding a complete redraw of the canvas.

        Setting plot().canvas().setAttribute(Qt.WA_PaintOutsidePaintEvent, True)
        will result in faster painting, if the paint engine of the canvas widget
        supports this feature."""
        if seriesItem is None or seriesItem.plot() is None:
            return
        canvas = seriesItem.plot().canvas()
        canvasRect = canvas.contentsRect()
        plotCanvas = canvas  #XXX: cast to QwtPlotCanvas
        if plotCanvas and qwtHasBackingStore(plotCanvas):
            painter = QPainter(plotCanvas.backingStore())  #XXX: cast plotCanvas.backingStore() to QPixmap
            if self.__data.hasClipping:
                painter.setClipRegion(self.__data.clipRegion)
            qwtRenderItem(painter, canvasRect, seriesItem, from_, to)
            if self.testAttribute(self.FullRepaint):
                plotCanvas.repaint()
                return
        immediatePaint = True
        if not canvas.testAttribute(Qt.WA_WState_InPaintEvent):
            if QT_VERSION >= 0x050000 or\
               not canvas.testAttribute(Qt.WA_PaintOutsidePaintEvent):
                immediatePaint = False
        if immediatePaint:
            if not self.__data.painter.isActive():
                self.reset()
                self.__data.painter.begin(canvas)
                canvas.installEventFilter(self)
            if self.__data.hasClipping:
                self.__data.painter.setClipRegion(
                        QRegion(canvasRect) & self.__data.clipRegion)
            elif not self.__data.painter.hasClipping():
                self.__data.painter.setClipRect(canvasRect)
            qwtRenderItem(self.__data.painter,
                          canvasRect, seriesItem, from_, to)
            if self.__data.attributes & self.AtomicPainter:
                self.reset()
            elif self.__data.hasClipping:
                self.__data.painter.setClipping(False)
        else:
            self.reset()
            self.__data.seriesItem = seriesItem
            self.__data.from_ = from_
            self.__data.to = to
            clipRegion = QRegion(canvasRect)
            if self.__data.hasClipping:
                clipRegion &= self.__data.clipRegion
            canvas.installEventFilter(self)
            canvas.repaint(clipRegion)
            canvas.removeEventFilter(self)
            self.__data.seriesItem = None
    
    def reset(self):
        if self.__data.painter.isActive():
            w = self.__data.painter.device()  #XXX: cast to QWidget
            if w:
                w.removeEventFilter(self)
            self.__data.painter.end()
    
    def eventFilter(self, obj_, event):
        if event.type() == QEvent.Paint:
            self.reset()
            if self.__data.seriesItem:
                pe = event  #XXX: cast to QPaintEvent
                canvas = self.__data.seriesItem.plot().canvas()
                painter = QPainter(canvas)
                painter.setClipRegion(pe.region())
                doCopyCache = self.testAttribute(self.CopyBackingStore)
                if doCopyCache:
                    plotCanvas = canvas  #XXX: cast to QwtPlotCanvas
                    if plotCanvas:
                        doCopyCache = qwtHasBackingStore(plotCanvas)
                        if doCopyCache:
                            painter.drawPixmap(plotCanvas.contentsRect().topLeft(),
                                               plotCanvas.backingStore())
                if not doCopyCache:
                    qwtRenderItem(painter, canvas.contentsRect(),
                                  self.__data.seriesItem,
                                  self.__data.from_, self.__data.to)
                return True
        return False
