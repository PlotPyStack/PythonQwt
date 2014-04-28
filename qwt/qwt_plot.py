# -*- coding: utf-8 -*-

from qwt.qt.QtGui import (QWidget, QFont, QSizePolicy, QFrame, QApplication,
                          QRegion, QPainter, QPalette)
from qwt.qt.QtCore import Qt, SIGNAL, QEvent, QSize, QRectF

from qwt.qwt_text import QwtText, QwtTextLabel
from qwt.qwt_scale_widget import QwtScaleWidget
from qwt.qwt_scale_draw import QwtScaleDraw
from qwt.qwt_scale_engine import QwtLinearScaleEngine
from qwt.qwt_plot_canvas import QwtPlotCanvas
from qwt.qwt_scale_div import QwtScaleDiv
from qwt.qwt_scale_map import QwtScaleMap
from qwt.qwt_graphic import QwtGraphic
from qwt.qwt_legend_data import QwtLegendData
from qwt.qwt_interval import QwtInterval

import numpy as np


def qwtEnableLegendItems(plot, on):
    if on:
        plot.connect(plot, QwtPlot.LEGEND_DATA_CHANGED,
                     plot.updateLegendItems)
    else:
        plot.disconnect(plot, QwtPlot.LEGEND_DATA_CHANGED,
                        plot.updateLegendItems)

def qwtSetTabOrder(first, second, with_children):
    tab_chain = [first, second]
    if with_children:
        children = second.findChildren()
        w = second.nextInFocusChain()
        while w in children:
            while w in children:
                children.remove(w)
            tab_chain += [w]
            w = w.nextInFocusChain()
    for idx in range(len(tab_chain)-1):
        w_from = tab_chain[idx]
        w_to = tab_chain[idx+1]
        policy1, policy2 = w_from.focusPolicy(), w_to.focusPolicy()
        proxy1, proxy2 = w_from.focusProxy(), w_to.focusProxy()
        for w in (w_from, w_to):
            w.setFocusPolicy(Qt.TabFocus)
            w.setFocusProxy(None)
        QWidget.setTabOrder(w_from, w_to)
        for w, pl, px in ((w_from, policy1, proxy1), (w_to, policy2, proxy2)):
            w.setFocusPolicy(pl)
            w.setFocusProxy(px)


class ItemList(list):
    def sortItems(self):
        self.sort(cmp=lambda item1, item2: cmp(item1.z(), item2.z()))

    def insertItem(self, obj):
        self.append(obj)
        self.sortItems()
        
    def removeItem(self, obj):
        self.remove(obj)
        self.sortItems()


class QwtPlotDict_PrivateData(object):
    def __init__(self):
        self.itemList = ItemList()
        self.autoDelete = True


class QwtPlotDict(object):
    def __init__(self):
        self.d_data = QwtPlotDict_PrivateData()
    
    def setAutoDelete(self, autoDelete):
        self.d_data.autoDelete = autoDelete
    
    def autoDelete(self):
        return self.d_data.autoDelete
    
    def insertItem(self, item):
        self.d_data.itemList.insertItem(item)
    
    def removeItem(self, item):
        self.d_data.itemList.removeItem(item)

    def detachItems(self, rtti, autoDelete):
        for item in self.d_data.itemList[:]:
            if rtti == QwtPlotItem.Rtti_PlotItem and item.rtti() == rtti:
                item.attach(None)
                if self.autoDelete:
                    self.d_data.itemList.remove(item)

    def itemList(self, rtti=None):
        if rtti is None or rtti == QwtPlotItem.Rtti_PlotItem:
            return self.d_data.itemList
        return [item for item in self.d_data.itemList if item.rtti() == rtti]


class QwtPlot_PrivateData(QwtPlotDict_PrivateData):
    def __init__(self):
        super(QwtPlot_PrivateData, self).__init__()
        self.titleLabel = None
        self.footerLabel = None
        self.canvas = None
        self.legend = None
        self.layout = None
        self.autoReplot = None


class AxisData(object):
    def __init__(self):
        self.isEnabled = None
        self.doAutoScale = None
        self.minValue = None
        self.maxValue = None
        self.stepSize = None
        self.maxMajor = None
        self.maxMinor = None
        self.isValid = None
        self.scaleDiv = None # QwtScaleDiv
        self.scaleEngine = None # QwtScaleEngine
        self.scaleWidget = None # QwtScaleWidget


class QwtPlot(QFrame, QwtPlotDict):
    ITEM_ATTACHED = SIGNAL("itemAttached(PyQt_PyObject,bool)")
    LEGEND_DATA_CHANGED = SIGNAL("legendDataChanged(PyQt_PyObject,bool)")

    # enum Axis
    yLeft, yRight, xBottom, xTop, axisCnt = range(5)
    
    # enum LegendPosition
    LeftLegend, RightLegend, BottomLegend, TopLegend = range(4)
    
    def __init__(self, *args):
        if len(args) == 0:
            title, parent = "", None
        elif len(args) == 1:
            title = ""
            parent, = args
        elif len(args) == 2:
            title, parent = args
        super(QwtPlot, self).__init__(parent)
        
        self.d_data = QwtPlot_PrivateData()
        from qwt.qwt_plot_layout import QwtPlotLayout
        self.d_data.layout = QwtPlotLayout()
        self.d_data.autoReplot = False
                
        self.setAutoReplot(True)
#        self.setPlotLayout(self.d_data.layout)
        
        # title
        self.d_data.titleLabel = QwtTextLabel(self)
        self.d_data.titleLabel.setObjectName("QwtPlotTitle")
        self.d_data.titleLabel.setFont(QFont(self.fontInfo().family(), 14,
                                             QFont.Bold))
        text = QwtText(title)
        text.setRenderFlags(Qt.AlignCenter|Qt.TextWordWrap)
        self.d_data.titleLabel.setText(text)
        
        # footer
        self.d_data.footerLabel = QwtTextLabel(self)
        self.d_data.footerLabel.setObjectName("QwtPlotFooter")
        footer = QwtText()
        footer.setRenderFlags(Qt.AlignCenter|Qt.TextWordWrap)
        self.d_data.footerLabel.setText(footer)
        
        # legend
        self.d_data.legend = None
        
        # axis
        self.d_axisData = []
        self.initAxesData()
        
        # canvas
        self.d_data.canvas = QwtPlotCanvas(self)
        self.d_data.canvas.setObjectName("QwtPlotCanvas")
        self.d_data.canvas.installEventFilter(self)
        
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)
        
        self.resize(200, 200)
        
        focusChain = [self, self.d_data.titleLabel, self.axisWidget(self.xTop),
                      self.axisWidget(self.yLeft), self.d_data.canvas,
                      self.axisWidget(self.yRight),
                      self.axisWidget(self.xBottom), self.d_data.footerLabel]
        
        for idx in range(len(focusChain)-1):
            qwtSetTabOrder(focusChain[idx], focusChain[idx+1], False)
        
        qwtEnableLegendItems(self, True)
        
    def initAxesData(self):
        self.d_axisData = [AxisData() for axisId in range(self.axisCnt)]
        
        self.d_axisData[self.yLeft].scaleWidget = \
            QwtScaleWidget(QwtScaleDraw.LeftScale, self)
        self.d_axisData[self.yRight].scaleWidget = \
            QwtScaleWidget(QwtScaleDraw.RightScale, self)
        self.d_axisData[self.xTop].scaleWidget = \
            QwtScaleWidget(QwtScaleDraw.TopScale, self)
        self.d_axisData[self.xBottom].scaleWidget = \
            QwtScaleWidget(QwtScaleDraw.BottomScale, self)

        self.d_axisData[self.yLeft
                        ].scaleWidget.setObjectName("QwtPlotAxisYLeft")
        self.d_axisData[self.yRight
                        ].scaleWidget.setObjectName("QwtPlotAxisYRight")
        self.d_axisData[self.xTop
                        ].scaleWidget.setObjectName("QwtPlotAxisXTop")
        self.d_axisData[self.xBottom
                        ].scaleWidget.setObjectName("QwtPlotAxisXBottom")

        fscl = QFont(self.fontInfo().family(), 10)
        fttl = QFont(self.fontInfo().family(), 12, QFont.Bold)
        
        for axisId in range(self.axisCnt):
            d = self.d_axisData[axisId]

            d.scaleEngine = QwtLinearScaleEngine()

            d.scaleWidget.setTransformation(d.scaleEngine.transformation())
            d.scaleWidget.setFont(fscl)
            d.scaleWidget.setMargin(2)

            text = d.scaleWidget.title()
            text.setFont(fttl)
            d.scaleWidget.setTitle(text)
            
            d.doAutoScale = True
            d.minValue = 0.0
            d.maxValue = 1000.0
            d.stepSize = 0.0            
            d.maxMinor = 5
            d.maxMajor = 8
            d.isValid = False
            
        self.d_axisData[self.yLeft].isEnabled = True
        self.d_axisData[self.yRight].isEnabled = False
        self.d_axisData[self.xBottom].isEnabled = True
        self.d_axisData[self.xTop].isEnabled = False

    def axisWidget(self, axisId):
        if self.axisValid(axisId):
            return self.d_axisData[axisId].scaleWidget
    
    def setAxisScaleEngine(self, axisId, scaleEngine):
        if self.axisValid(axisId) and scaleEngine is not None:
            d = self.d_axisData[axisId]
            d.scaleEngine = scaleEngine
            self.d_axisData[axisId].scaleWidget.setTransformation(
                                                scaleEngine.transformation)
            d.isValid = False
            self.autoRefresh()
    
    def axisScaleEngine(self, axisId):
        if self.axisValid(axisId):
            return self.d_axisData[axisId].scaleEngine

    def axisAutoScale(self, axisId):
        if self.axisValid(axisId):
            return self.d_axisData[axisId].doAutoScale
    
    def axisEnabled(self, axisId):
        if self.axisValid(axisId):
            return self.d_axisData[axisId].isEnabled
    
    def axisFont(self, axisId):
        if self.axisValid(axisId):
            return self.axisWidget(axisId).font()
        else:
            return QFont()
    
    def axisMaxMajor(self, axisId):
        if self.axisValid(axisId):
            return self.axisWidget(axisId).maxMajor
        else:
            return 0

    def axisMaxMinor(self, axisId):
        if self.axisValid(axisId):
            return self.axisWidget(axisId).maxMinor
        else:
            return 0
    
    def axisScaleDiv(self, axisId):
        return self.d_axisData[axisId].scaleDiv
    
    def axisScaleDraw(self, axisId):
        if self.axisValid(axisId):
            return self.axisWidget(axisId).scaleDraw()

    def axisStepSize(self, axisId):
        if self.axisValid(axisId):
            return self.axisWidget(axisId).stepSize
        else:
            return 0
    
    def axisInterval(self, axisId):
        if self.axisValid(axisId):
            return self.axisWidget(axisId).scaleDiv.interval()
        else:
            return QwtInterval()

    def axisTitle(self, axisId):
        if self.axisValid(axisId):
            return self.axisWidget(axisId).title()
        else:
            return QwtText()
    
    def enableAxis(self, axisId, tf):
        if self.axisValid(axisId) and tf != self.d_axisData[axisId].isEnabled:
            self.d_axisData[axisId].isEnabled = tf
            self.updateLayout()
            
    def invTransform(self, axisId, pos):
        if self.axisValid(axisId):
            return self.canvasMap(axisId).invTransform(pos)
        else:
            return 0.
            
    def transform(self, axisId, value):
        if self.axisValid(axisId):
            return self.canvasMap(axisId).transform(value)
        else:
            return 0.

    def setAxisFont(self, axisId, font):
        if self.axisValid(axisId):
            return self.axisWidget(axisId).setFont(font)
    
    def setAxisAutoScale(self, axisId, on):
        if self.axisValid(axisId) and self.d_axisData[axisId].doAutoScale != on:
            self.d_axisData[axisId].doAutoScale = on
            self.autoRefresh()
    
    def setAxisScale(self, axisId, min_, max_, stepSize):
        if self.axisValid(axisId):
            d = self.d_axisData[axisId]
            d.doAutoScale = False
            d.isValid = False
            d.minValue = min_
            d.maxValue = max_
            d.stepSize = stepSize
            self.autoRefresh()
    
    def setAxisScaleDiv(self, axisId, scaleDiv):
        if self.axisValid(axisId):
            d = self.d_axisData[axisId]
            d.doAutoScale = False
            d.scaleDiv = scaleDiv
            d.isValid = True
            self.autoRefresh()
        
    def setAxisScaleDraw(self, axisId, scaleDraw):
        if self.axisValid(axisId):
            self.axisWidget(axisId).setScaleDraw(scaleDraw)
            self.autoRefresh()
    
    def setAxisLabelAlignment(self, axisId, alignment):
        if self.axisValid(axisId):
            self.axisWidget(axisId).setLabelAlignment(alignment)
            
    def setAxisLabelRotation(self, axisId, rotation):
        if self.axisValid(axisId):
            self.axisWidget(axisId).setLabelRotation(rotation)
            
    def setAxisMaxMinor(self, axisId, maxMinor):
        if self.axisValid(axisId):
            maxMinor = max([0, min([maxMinor, 100])])
            d = self.d_axisData[axisId]
            if maxMinor != d.maxMinor:
                d.maxMinor = maxMinor
                d.isValid = False
                self.autoRefresh()

    def setAxisMaxMajor(self, axisId, maxMajor):
        if self.axisValid(axisId):
            maxMajor = max([1, min([maxMajor, 10000])])
            d = self.d_axisData[axisId]
            if maxMajor != d.maxMajor:
                d.maxMajor = maxMajor
                d.isValid = False
                self.autoRefresh()

    def setAxisTitle(self, axisId, title):
        if self.axisValid(axisId):
            self.axisWidget(axisId).setTitle(title)

    def updateAxes(self):
        intv = [QwtInterval() for _i in range(self.axisCnt)]
        itmList = self.itemList()
        for item in itmList:
            if not item.testItemAttribute(QwtPlotItem.AutoScale):
                continue
            if not item.isVisible():
                continue
            if self.axisAutoScale(item.xAxis()) or self.axisAutoScale(item.yAxis()):
                rect = item.boundingRect()
                if rect.width() >= 0.:
                    intv[item.xAxis()] |= QwtInterval(rect.left(), rect.right())
                if rect.height() >= 0.:
                    intv[item.yAxis()] |= QwtInterval(rect.top(), rect.bottom())
        for axisId in range(self.axisCnt):
            d = self.d_axisData[axisId]
            minValue = d.minValue
            maxValue = d.maxValue
            stepSize = d.stepSize
            if d.doAutoScale and intv[axisId].isValid():
                d.isValid = False
                minValue = intv[axisId].minValue()
                maxValue = intv[axisId].maxValue()
                d.scaleEngine.autoScale(d.maxMajor, minValue, maxValue, stepSize)
            if not d.isValid:
                d.scaleDiv = d.scaleEngine.divideScale(minValue, maxValue,
                                           d.maxMajor, d.maxMinor, stepSize)
                d.isValid = True
            scaleWidget = self.axisWidget(axisId)
            scaleWidget.setScaleDiv(d.scaleDiv)
            startDist, endDist = scaleWidget.getBorderDistHint()
            scaleWidget.setBorderDist(startDist, endDist)
        for item in itmList:
            if item.testItemInterest(QwtPlotItem.ScaleInterest):
                item.updateScaleDiv(self.axisScaleDiv(item.xAxis()),
                                    self.axisScaleDiv(item.yAxis()))
    
    def setCanvas(self, canvas):
        if canvas == self.d_data.canvas:
            return
        self.d_data.canvas = canvas
        if canvas:
            canvas.setParent(self)
            canvas.installEventFilter(self)
            if self.isVisible():
                canvas.show()
    
    def event(self, event):
        ok = QFrame.event(self, event)
        if event.type() == QEvent.LayoutRequest:
            self.updateLayout()
        elif event.type() == QEvent.PolishRequest:
            self.replot()
        return ok

    def eventFilter(self, obj, event):
        if obj == self.d_data.canvas:
            if event.type() == QEvent.Resize:
                self.updateCanvasMargins()
            elif event.type() == 178:#QEvent.ContentsRectChange:
                self.updateLayout()
        return QFrame.eventFilter(self, obj, event)
    
    def autoRefresh(self):
        if self.d_data.autoReplot:
            self.replot()
    
    def setAutoReplot(self, tf):
        self.d_data.autoReplot = tf
    
    def autoReplot(self):
        return self.d_data.autoReplot
    
    def setTitle(self, title):
        current_title = self.d_data.titleLabel.text()
        if isinstance(title, QwtText) and current_title == title:
            return
        elif not isinstance(title, QwtText) and current_title.text() == title:
            return
        self.d_data.titleLabel.setText(title)
        self.updateLayout()
    
    def title(self):
        return self.d_data.titleLabel.text()
    
    def titleLabel(self):
        return self.d_data.titleLabel
    
    def setFooter(self, text):
        current_footer = self.d_data.footerLabel.text()
        if isinstance(text, QwtText) and current_footer == text:
            return
        elif not isinstance(text, QwtText) and current_footer.text() == text:
            return
        self.d_data.footerLabel.setText(text)
        self.updateLayout()
    
    def footer(self):
        return self.d_data.footerLabel.text()
    
    def footerLabel(self):
        return self.d_data.footerLabel

    def setPlotLayout(self, layout):
        if layout != self.d_data.layout:
            self.d_data.layout = layout
            self.updateLayout()
    
    def plotLayout(self):
        return self.d_data.layout
    
    def legend(self):
        return self.d_data.legend
    
    def canvas(self):
        return self.d_data.canvas
    
    def sizeHint(self):
        dw = dh = 0
        for axisId in range(self.axisCnt):
            if self.axisEnabled(axisId):
                niceDist = 40
                scaleWidget = self.axisWidget(axisId)
                scaleDiv = scaleWidget.scaleDraw().scaleDiv()
                majCnt = scaleDiv.ticks(QwtScaleDiv.MajorTick).count()
                if axisId in (self.yLeft, self.yRight):
                    hDiff = (majCnt-1)*niceDist-scaleWidget.minimumSizeHint().height()
                    if hDiff > dh:
                        dh = hDiff
                else:
                    wDiff = (majCnt-1)*niceDist-scaleWidget.minimumSizeHint().width()
                    if wDiff > dw:
                        dw = wDiff
        return self.minimumSizeHint() + QSize(dw, dh)
    
    def minimumSizeHint(self):
        hint = self.d_data.layout.minimumSizeHint(self)
        hint += QSize(2*self.frameWidth(), 2*self.frameWidth())
        return hint
    
    def resizeEvent(self, e):
        QFrame.resizeEvent(self, e)
        self.updateLayout()
    
    def replot(self):
        doAutoReplot = self.autoReplot()
        self.setAutoReplot(False)
        self.updateAxes()
        
        QApplication.sendPostedEvents(self, QEvent.LayoutRequest)
        
        if self.d_data.canvas:
            try:
                self.d_data.canvas.replot()
                ok = True
            except (AttributeError, TypeError):
                ok = False
            if not ok:
                self.d_data.canvas.update(self.d_data.canvas.contentsRect())
        
        self.setAutoReplot(doAutoReplot)
    
    def updateLayout(self):
        self.d_data.layout.activate(self, self.contentsRect())
        
        titleRect = self.d_data.layout.titleRect().toRect()
        footerRect = self.d_data.layout.footerRect().toRect()
        scaleRect = [None] * self.axisCnt
        for axisId in range(self.axisCnt):
            scaleRect[axisId] = self.d_data.layout.scaleRect(axisId).toRect()
        legendRect = self.d_data.layout.legendRect().toRect()
        canvasRect = self.d_data.layout.canvasRect().toRect()
        
        if self.d_data.titleLabel.text():
            self.d_data.titleLabel.setGeometry(titleRect)
            if not self.d_data.titleLabel.isVisibleTo(self):
                self.d_data.titleLabel.show()
        else:
            self.d_data.titleLabel.hide()

        if self.d_data.footerLabel.text():
            self.d_data.footerLabel.setGeometry(footerRect)
            if not self.d_data.footerLabel.isVisibleTo(self):
                self.d_data.footerLabel.show()
        else:
            self.d_data.footerLabel.hide()
        
        for axisId in range(self.axisCnt):
            if self.axisEnabled(axisId):
                self.axisWidget(axisId).setGeometry(scaleRect[axisId])
                
                if axisId in (self.xBottom, self.xTop):
                    r = QRegion(scaleRect[axisId])
                    if self.axisEnabled(self.yLeft):
                        r = r.subtracted(QRegion(scaleRect[self.yLeft]))
                    if self.axisEnabled(self.yRight):
                        r = r.subtracted(QRegion(scaleRect[self.yRight]))
                    r.translate(-scaleRect[axisId].x(), -scaleRect[axisId].y())
                    
                    self.axisWidget(axisId).setMask(r)
                    
                if not self.axisWidget(axisId).isVisibleTo(self):
                    self.axisWidget(axisId).show()
                
            else:
                self.axisWidget(axisId).hide()
            
        if self.d_data.legend:
            if self.d_data.legend.isEmpty():
                self.d_data.legend.hide()
            else:
                self.d_data.legend.setGeometry(legendRect)
                self.d_data.legend.show()
        
        self.d_data.canvas.setGeometry(canvasRect)
    
    def getCanvasMarginsHint(self, maps, canvasRect):
        """Calculate the canvas margins
        (``margins`` is a list which is modified inplace)"""
        left = top = right = bottom = -1.

        for item in self.itemList():
            if item.testItemAttribute(QwtPlotItem.Margins):
                m = item.getCanvasMarginHint(maps, canvasRect)
                left = max([left, m[self.yLeft]])
                top = max([top, m[self.xTop]])
                right = max([right, m[self.yRight]])
                bottom = max([bottom, m[self.xBottom]])

        return left, top, right, bottom
    
    def updateCanvasMargins(self):
        maps = [self.canvasMap(axisId) for axisId in range(self.axisCnt)]
        margins = self.getCanvasMarginsHint(maps, self.canvas().contentsRect())
        
        doUpdate = False
        
        for axisId in range(self.axisCnt):
            if margins[axisId] >= 0.:
                m = np.ceil(margins[axisId])
                self.plotLayout().setCanvasMargin(m, axisId)
                doUpdate = True
        
        if doUpdate:
            self.updateLayout()
    
    def drawCanvas(self, painter):
        maps = [self.canvasMap(axisId) for axisId in range(self.axisCnt)]
        self.drawItems(painter, self.d_data.canvas.contentsRect(), maps)
    
    def drawItems(self, painter, canvasRect, maps):
        for item in self.itemList():
            if item and item.isVisible():
                painter.save()
                painter.setRenderHint(QPainter.Antialiasing,
                          item.testRenderHint(QwtPlotItem.RenderAntialiased))
                painter.setRenderHint(QPainter.HighQualityAntialiasing,
                          item.testRenderHint(QwtPlotItem.RenderAntialiased))
                item.draw(painter, maps, canvasRect)
                painter.restore()

    def canvasMap(self, axisId):
        map_ = QwtScaleMap()
        if not self.d_data.canvas:
            return map_
        
        map_.setTransformation(self.axisScaleEngine(axisId).transformation())
        sd = self.axisScaleDiv(axisId)
        map_.setScaleInterval(sd.lowerBound(), sd.upperBound())
        
        if self.axisEnabled(axisId):
            s = self.axisWidget(axisId)
            if axisId in (self.yLeft, self.yRight):
                y = s.y() + s.startBorderDist() - self.d_data.canvas.y()
                h = s.height() - s.startBorderDist() - s.endBorderDist()
                map_.setPaintInterval(y+h, y)
            else:
                x = s.x() + s.startBorderDist() - self.d_data.canvas.x()
                w = s.width() - s.startBorderDist() - s.endBorderDist()
                map_.setPaintInterval(x, x+w)
        else:
            margin = 0
            if not self.plotLayout().alignCanvasToScale(axisId):
                margin = self.plotLayout().canvasMargin(axisId)
            canvasRect = self.d_data.canvas.contentsRect()
            if axisId in (self.yLeft, self.yRight):
                map_.setPaintInterval(canvasRect.bottom()-margin,
                                      canvasRect.top()+margin)
            else:
                map_.setPaintInterval(canvasRect.left()+margin,
                                      canvasRect.right()-margin)
        return map_
    
    def setCanvasBackground(self, brush):
        pal = self.d_data.canvas.palette()
        pal.setBrush(QPalette.Window, brush)
        self.canvas().setPalette(pal)
    
    def canvasBackground(self):
        return self.canvas().palette().brush(QPalette.Normal, QPalette.Window)
    
    def axisValid(self, axisId):
        return axisId in range(QwtPlot.axisCnt)
    
    def insertLegend(self, legend, pos, ratio):
        self.d_data.layout.setLegendPosition(pos, ratio)
        if legend != self.d_data.legend:
            if self.d_data.legend and self.d_data.legend.parent() is self:
                del self.d_data.legend
            self.d_data.legend = legend
            if self.d_data.legend:
                self.connect(self, QwtPlot.LEGEND_DATA_CHANGED,
                             self.updateLegend)
                if self.d_data.legend.parent() is not self:
                    self.d_data.legend.setParent(self)
                
                qwtEnableLegendItems(self, False)
                self.updateLegend()
                qwtEnableLegendItems(self, True)
                
                lpos = self.d_data.layout.legendPosition()

                if legend:
                    if lpos in (self.LeftLegend, self.RightLegend):
                        if legend.maxColumns() == 0:
                            legend.setMaxColumns(1)
                    elif lpos in (self.TopLegend, self.BottomLegend):
                        legend.setMaxColumns(0)
                
                previousInChain = None
                if lpos == self.LeftLegend:
                    previousInChain = self.axisWidget(QwtPlot.xTop)
                elif lpos == self.TopLegend:
                    previousInChain = self
                elif lpos == self.RightLegend:
                    previousInChain = self.axisWidget(QwtPlot.yRight)
                elif lpos == self.BottomLegend:
                    previousInChain = self.footerLabel()
                
            if previousInChain:
                qwtSetTabOrder(previousInChain, legend, True)
        
        self.updateLayout()
    
    def updateLegend(self, plotItem=None):
        if plotItem is None:
            items = [plotItem for plotItem in self.itemList()]
        else:
            items = [plotItem]
        for plotItem in items:
            if plotItem is None:
                continue
            legendData = []
            if plotItem.testItemAttribute(QwtPlotItem.Legend):
                legendData = plotItem.legendData()
            self.emit(QwtPlot.LEGEND_DATA_CHANGED, plotItem, legendData)

    def updateLegendItems(self, plotItem, legendData):
        if plotItem:
            for item in self.itemList():
                if item.testItemInterest(QwtPlotItem.LegendInterest):
                    item.updateLegend(plotItem, legendData)
    
    def attachItem(self, plotItem, on):
        if plotItem.testItemInterest(QwtPlotItem.LegendInterest):
            for item in self.itemList():
                legendData = []
                if on and item.testItemAttribute(QwtPlotItem.Legend):
                    legendData = item.legendData()
                    plotItem.updateLegend(item, legendData)
    
        if on:
            self.insertItem(plotItem)
        else:
            self.removeItem(plotItem)
        
        self.emit(QwtPlot.ITEM_ATTACHED, plotItem, on)
        
        if plotItem.testItemAttribute(QwtPlotItem.Legend):
            if on:
                self.updateLegend(plotItem)
            else:
                self.emit(QwtPlot.LEGEND_DATA_CHANGED, plotItem, [])
        
        if self.autoReplot():
            self.update()


class QwtPlotItem_PrivateData(object):
    def __init__(self):
        self.plot = None
        self.isVisible = True
        self.attributes = 0
        self.interests = 0
        self.renderHints = 0
        self.renderThreadCount = 1
        self.z = 0.
        self.xAxis = QwtPlot.xBottom
        self.yAxis = QwtPlot.yLeft
        self.legendIconSize = QSize(8, 8)
        self.title = None # QwtText


class QwtPlotItem(object):
    
    # enum RttiValues
    (Rtti_PlotItem, Rtti_PlotGrid, Rtti_PlotScale, Rtti_PlotLegend,
     Rtti_PlotMarker, Rtti_PlotCurve, Rtti_PlotSpectroCurve,
     Rtti_PlotIntervalCurve, Rtti_PlotHistogram, Rtti_PlotSpectrogram,
     Rtti_PlotSVG, Rtti_PlotTradingCurve, Rtti_PlotBarChart,
     Rtti_PlotMultiBarChart, Rtti_PlotShape, Rtti_PlotTextLabel,
     Rtti_PlotZone) = range(17)
    Rtti_PlotUserItem = 1000
    
    # enum ItemAttribute
    Legend = 0x01
    AutoScale = 0x02
    Margins = 0x04
    
    # enum ItemInterest
    ScaleInterest = 0x01
    LegendInterest = 0x02
    
    # enum RenderHint
    RenderAntialiased = 0x1
    
    def __init__(self, title):
        """title: QwtText"""
        self.d_data = QwtPlotItem_PrivateData()
        self.d_data.title = title

    def attach(self, plot):
        if plot is self.d_data.plot:
            return
        
        if self.d_data.plot:
            self.d_data.plot.attachItem(self, False)
        
        self.d_data.plot = plot
        
        if self.d_data.plot:
            self.d_data.plot.attachItem(self, True)
    
    def detach(self):
        self.attach(None)
    
    def rtti(self):
        return self.Rtti_PlotItem
    
    def plot(self):
        return self.d_data.plot
        
    def z(self):
        return self.d_data.z
        
    def setZ(self, z):
        if self.d_data.z != z:
            if self.d_data.plot:
                self.d_data.plot.attachItem(self, False)
            self.d_data.z = z
            if self.d_data.plot:
                self.d_data.plot.attachItem(self, True)
            self.itemChanged()
    
    def setTitle(self, title):
        if not isinstance(title, QwtText):
            title = QwtText(title)
        if self.d_data.title != title:
            self.d_data.title = title
        self.legendChanged()
    
    def title(self):
        return self.d_data.title
    
    def setItemAttribute(self, attribute, on):
        if self.d_data.attributes.testFlag(attribute) != on:
            if on:
                self.d_data.attributes |= attribute
            else:
                self.d_data.attributes &= not attribute
            if attribute == QwtPlotItem.Legend:
                self.legendChanged()
            self.itemChanged()
    
    def testItemAttribute(self, attribute):
        return self.d_data.attributes.testFlag(attribute)
    
    def setItemInterest(self, interest, on):
        if self.d_data.interests.testFlag(interest) != on:
            if on:
                self.d_data.interests |= interest
            else:
                self.d_data.interests &= not interest
            self.itemChanged()
    
    def testItemInterest(self, interest):
        return self.d_data.interests.testFlag(interest)
    
    def setRenderHint(self, hint, on):
        if self.d_data.renderHints.testFlag(hint) != on:
            if on:
                self.d_data.renderHints |= hint
            else:
                self.d_data.renderHints &= not hint
            self.itemChanged()
    
    def testRenderHint(self, hint):
        return self.d_data.renderHints.testFlag(hint)
    
    def setRenderThreadCount(self, numThreads):
        self.d_data.renderThreadCount = numThreads
    
    def renderThreadCount(self):
        return self.d_data.renderThreadCount
    
    def setLegendIconSize(self, size):
        if self.d_data.legendIconSize != size:
            self.d_data.legendIconSize = size
            self.legendChanged()
    
    def legendIconSize(self):
        return self.d_data.legendIconSize
    
    def legendIcon(self, index, size):
        return QwtGraphic()
    
    def defaultIcon(brush, size):
        icon = QwtGraphic()
        if not size.isEmpty():
            icon.setDefaultSize(size)
            r = QRectF(0, 0, size.width(), size.height())
            painter = QPainter(icon)
            painter.fillRect(r, brush)
        return icon
    
    def show(self):
        self.setVisible(True)
    
    def hide(self):
        self.setVisible(False)
    
    def setVisible(self, on):
        if on != self.d_data.isVisible:
            self.d_data.isVisible = on
            self.itemChanged()
    
    def isVisible(self):
        return self.d_data.isVisible
    
    def itemChanged(self):
        if self.d_data.plot:
            self.d_data.plot.autoRefresh()
    
    def legendChanged(self):
        if self.testItemAttribute(QwtPlotItem.Legend) and self.d_data.plot:
            self.d_data.plot.updateLegend(self)
    
    def setAxes(self, xAxis, yAxis):
        if xAxis == QwtPlot.xBottom or xAxis == QwtPlot.xTop:
            self.d_data.xAxis = xAxis
        if yAxis == QwtPlot.yLeft or yAxis == QwtPlot.yRight:
            self.d_data.yAxis = yAxis
        self.itemChanged()
    
    def setXAxis(self, axis):
        if axis in (QwtPlot.xBottom, QwtPlot.xTop):
            self.d_data.xAxis = axis
            self.itemChanged()
    
    def setYAxis(self, axis):
        if axis in (QwtPlot.yLeft, QwtPlot.yRight):
            self.d_data.yAxis = axis
            self.itemChanged()

    def xAxis(self):
        return self.d_data.xAxis
    
    def yAxis(self):
        return self.d_data.yAxis
    
    def boundingRect(self):
        return QRectF(1.0, 1.0, -2.0, -2.0)
    
    def getCanvasMarginHint(self, xMap, yMap, canvasRect):
        left = top = right = bottom = 0.
        return left, top, right, bottom
    
    def legendData(self):
        data = QwtLegendData()
        label = self.title()
        label.setRenderFlags(label.renderFlags() & Qt.AlignLeft)
        data.setValue(QwtLegendData.TitleRole, label)
        graphic = self.legendIcon(0, self.legendIconSize())
        if not graphic.isNull():
            data.setValue(QwtLegendData.IconRole, graphic)
        return [data]
    
    def updateLegend(self, item, data):
        pass

    def scaleRect(self, xMap, yMap):
        return QRectF(xMap.s1(), yMap.s1(), xMap.sDist(), yMap.sDist())
    
    def paintRect(self, xMap, yMap):
        return QRectF(xMap.p1(), yMap.p1(), xMap.pDist(), yMap.pDist())
