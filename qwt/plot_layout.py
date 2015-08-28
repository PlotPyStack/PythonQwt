# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License, Copyright (C) 2002 Uwe Rathmann
# (see qwt/LICENSE for details)

from qwt.text import QwtText
from qwt.scale_widget import QwtScaleWidget
from qwt.plot import QwtPlot
from qwt.scale_draw import QwtAbstractScaleDraw

from qwt.qt.QtGui import QFont, QRegion
from qwt.qt.QtCore import QSize, Qt, QRectF

import numpy as np

QWIDGETSIZE_MAX = (1<<24)-1


class LegendData(object):
    def __init__(self):
        self.frameWidth = None
        self.hScrollExtent = None
        self.vScrollExtent = None
        self.hint = QSize()

class TitleData(object):
    def __init__(self):
        self.text = QwtText()
        self.frameWidth = None

class FooterData(object):
    def __init__(self):
        self.text = QwtText()
        self.frameWidth = None

class ScaleData(object):
    def __init__(self):
        self.isEnabled = None
        self.scaleWidget = QwtScaleWidget()
        self.scaleFont = QFont()
        self.start = None
        self.end = None
        self.baseLineOffset = None
        self.tickOffset = None
        self.dimWithoutTitle = None

class CanvasData(object):
    def __init__(self):
        self.contentsMargins = [0 for _i in range(QwtPlot.axisCnt)]

class QwtPlotLayout_LayoutData(object):
    def __init__(self):
        self.legend = LegendData()
        self.title = TitleData()
        self.footer = FooterData()
        self.scale = [ScaleData() for _i in range(QwtPlot.axisCnt)]
        self.canvas = CanvasData()
    
    def init(self, plot, rect):
        # legend
        if plot.legend():
            self.legend.frameWidth = plot.legend().frameWidth()
            self.legend.hScrollExtent = plot.legend().scrollExtent(Qt.Horizontal)
            self.legend.vScrollExtent = plot.legend().scrollExtent(Qt.Vertical)
            hint = plot.legend().sizeHint()
            w = min([hint.width(), np.floor(rect.width())])
            h = plot.legend().heightForWidth(w)
            if h <= 0:
                h = hint.height()
            if h > rect.height():
                w += self.legend.hScrollExtent
            self.legend.hint = QSize(w, h)
        # title
        self.title.frameWidth = 0
        self.title.text = QwtText()
        if plot.titleLabel():
            label = plot.titleLabel()
            self.title.text = label.text()
            if not self.title.text.testPaintAttribute(QwtText.PaintUsingTextFont):
                self.title.text.setFont(label.font())
            self.title.frameWidth = plot.titleLabel().frameWidth()
        # footer
        self.footer.frameWidth = 0
        self.footer.text = QwtText()
        if plot.footerLabel():
            label = plot.footerLabel()
            self.footer.text = label.text()
            if not self.footer.text.testPaintAttribute(QwtText.PaintUsingTextFont):
                self.footer.text.setFont(label.font())
            self.footer.frameWidth = plot.footerLabel().frameWidth()
        # scales
        for axis in range(QwtPlot.axisCnt):
            if plot.axisEnabled(axis):
                scaleWidget = plot.axisWidget(axis)
                self.scale[axis].isEnabled = True
                self.scale[axis].scaleWidget = scaleWidget
                self.scale[axis].scaleFont = scaleWidget.font()
                self.scale[axis].start = scaleWidget.startBorderDist()
                self.scale[axis].end = scaleWidget.endBorderDist()
                self.scale[axis].baseLineOffset = scaleWidget.margin()
                self.scale[axis].tickOffset = scaleWidget.margin()
                if scaleWidget.scaleDraw().hasComponent(QwtAbstractScaleDraw.Ticks):
                    self.scale[axis].tickOffset += scaleWidget.scaleDraw().maxTickLength()
                self.scale[axis].dimWithoutTitle = scaleWidget.dimForLength(
                                QWIDGETSIZE_MAX, self.scale[axis].scaleFont)
                if not scaleWidget.title().isEmpty():
                    self.scale[axis].dimWithoutTitle -= \
                            scaleWidget.titleHeightForWidth(QWIDGETSIZE_MAX)
            else:
                self.scale[axis].isEnabled = False
                self.scale[axis].start = 0
                self.scale[axis].end = 0
                self.scale[axis].baseLineOffset = 0
                self.scale[axis].tickOffset = 0.
                self.scale[axis].dimWithoutTitle = 0
        self.canvas.contentsMargins = plot.canvas().getContentsMargins()


class QwtPlotLayout_PrivateData(object):
    def __init__(self):
        self.spacing = 5
        self.titleRect = QRectF()
        self.footerRect = QRectF()
        self.legendRect = QRectF()
        self.scaleRect = [QRectF() for _i in range(QwtPlot.axisCnt)]
        self.canvasRect = QRectF()
        self.layoutData = QwtPlotLayout_LayoutData()
        self.legendPos = None
        self.legendRatio = None
        self.canvasMargin = [0] * QwtPlot.axisCnt
        self.alignCanvasToScales = [False] * QwtPlot.axisCnt


class QwtPlotLayout(object):
    
    # enum Option
    AlignScales = 0x01
    IgnoreScrollbars = 0x02
    IgnoreFrames = 0x04
    IgnoreLegend = 0x08
    IgnoreTitle = 0x10
    IgnoreFooter = 0x20
    
    def __init__(self):
        self.__data = QwtPlotLayout_PrivateData()
        self.setLegendPosition(QwtPlot.BottomLegend)
        self.setCanvasMargin(4)
        self.setAlignCanvasToScales(False)
        self.invalidate()
    
    def setCanvasMargin(self, margin, axis=-1):
        if margin < 1:
            margin = -1
        if axis == -1:
            for axis in range(QwtPlot.axisCnt):
                self.__data.canvasMargin[axis] = margin
        elif axis >= 0 and axis < QwtPlot.axisCnt:
            self.__data.canvasMargin[axis] = margin
    
    def canvasMargin(self, axisId):
        if axisId < 0 or axisId >= QwtPlot.axisCnt:
            return 0
        return self.__data.canvasMargin[axisId]
    
    def setAlignCanvasToScales(self, *args):
        if len(args) == 1:
            on, = args
            for axis in range(QwtPlot.axisCnt):
                self.__data.alignCanvasToScales[axis] = on
        elif len(args) == 2:
            axisId, on = args
            if axis >= 0 and axis < QwtPlot.axisCnt:
                self.__data.alignCanvasToScales[axisId] = on
        else:
            raise TypeError("%s().setAlignCanvasToScales() takes 1 or 2 "\
                            "argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))

    def alignCanvasToScale(self, axisId):
        if axisId < 0 or axisId >= QwtPlot.axisCnt:
            return False
        return self.__data.alignCanvasToScales[axisId]
    
    def setSpacing(self, spacing):
        self.__data.spacing = max([0, spacing])
        
    def spacing(self):
        return self.__data.spacing
    
    def setLegendPosition(self, *args):
        if len(args) == 2:
            pos, ratio = args
            if ratio > 1.:
                ratio = 1.
            if pos in (QwtPlot.TopLegend, QwtPlot.BottomLegend):
                if ratio <= 0.:
                    ratio = .33
                self.__data.legendRatio = ratio
                self.__data.legendPos = pos
            elif pos in (QwtPlot.LeftLegend, QwtPlot.RightLegend):
                if ratio <= 0.:
                    ratio = .5
                self.__data.legendRatio = ratio
                self.__data.legendPos = pos
        elif len(args) == 1:
            pos, = args
            self.setLegendPosition(pos, 0.)
        else:
            raise TypeError("%s().setLegendPosition() takes 1 or 2 argument(s)"\
                            "(%s given)" % (self.__class__.__name__, len(args)))
    
    def legendPosition(self):
        return self.__data.legendPos
    
    def setLegendRatio(self, ratio):
        self.setLegendPosition(self.legendPosition(), ratio)
    
    def legendRatio(self):
        return self.__data.legendRatio
    
    def setTitleRect(self, rect):
        self.__data.titleRect = rect
    
    def titleRect(self):
        return self.__data.titleRect
    
    def setFooterRect(self, rect):
        self.__data.footerRect = rect
    
    def footerRect(self):
        return self.__data.footerRect
        
    def setLegendRect(self, rect):
        self.__data.legendRect = rect
    
    def legendRect(self):
        return self.__data.legendRect
    
    def setScaleRect(self, axis, rect):
        if axis >= 0 and axis < QwtPlot.axisCnt:
            self.__data.scaleRect[axis] = rect
    
    def scaleRect(self, axis):
        if axis < 0 or axis >= QwtPlot.axisCnt:
            return QRectF()
        return self.__data.scaleRect[axis]
    
    def setCanvasRect(self, rect):
        self.__data.canvasRect = rect
    
    def canvasRect(self):
        return self.__data.canvasRect
    
    def invalidate(self):
        self.__data.titleRect = QRectF()
        self.__data.footerRect = QRectF()
        self.__data.legendRect = QRectF()
        self.__data.canvasRect = QRectF()
        for axis in range(QwtPlot.axisCnt):
            self.__data.scaleRect[axis] = QRectF()
    
    def minimumSizeHint(self, plot):
        class _ScaleData(object):
            def __init__(self):
                self.w = 0
                self.h = 0
                self.minLeft = 0
                self.minRight = 0
                self.tickOffset = 0
        scaleData = [_ScaleData() for _i in range(QwtPlot.axisCnt)]
        canvasBorder = [0 for _i in range(QwtPlot.axisCnt)]
        fw, _, _, _ = plot.canvas().getContentsMargins()
        for axis in range(QwtPlot.axisCnt):
            if plot.axisEnabled(axis):
                scl = plot.axisWidget(axis)
                sd = scaleData[axis]
                hint = scl.minimumSizeHint()
                sd.w = hint.width()
                sd.h = hint.height()
                sd.minLeft, sd.minLeft = scl.getBorderDistHint()
                sd.tickOffset = scl.margin()
                if scl.scaleDraw().hasComponent(QwtAbstractScaleDraw.Ticks):
                    sd.tickOffset += np.ceil(scl.scaleDraw().maxTickLength())
            canvasBorder[axis] = fw + self.__data.canvasMargin[axis] + 1
        for axis in range(QwtPlot.axisCnt):
            sd = scaleData[axis]
            if sd.w and axis in (QwtPlot.xBottom, QwtPlot.xTop):
                if sd.minLeft > canvasBorder[QwtPlot.yLeft]\
                   and scaleData[QwtPlot.yLeft].w:
                    shiftLeft = sd.minLeft - canvasBorder[QwtPlot.yLeft]
                    if shiftLeft > scaleData[QwtPlot.yLeft].w:
                        shiftLeft = scaleData[QwtPlot.yLeft].w
                    sd.w -= shiftLeft
                if sd.minRight > canvasBorder[QwtPlot.yRight]\
                   and scaleData[QwtPlot.yRight].w:
                    shiftRight = sd.minRight - canvasBorder[QwtPlot.yRight]
                    if shiftRight > scaleData[QwtPlot.yRight].w:
                        shiftRight = scaleData[QwtPlot.yRight].w
                    sd.w -= shiftRight
            if sd.h and axis in (QwtPlot.yLeft, QwtPlot.yRight):
                if sd.minLeft > canvasBorder[QwtPlot.xBottom]\
                   and scaleData[QwtPlot.xBottom].h:
                    shiftBottom = sd.minLeft - canvasBorder[QwtPlot.xBottom]
                    if shiftBottom > scaleData[QwtPlot.xBottom].tickOffset:
                        shiftBottom = scaleData[QwtPlot.xBottom].tickOffset
                    sd.h -= shiftBottom
                if sd.minLeft > canvasBorder[QwtPlot.xTop]\
                   and scaleData[QwtPlot.xTop].h:
                    shiftTop = sd.minRight - canvasBorder[QwtPlot.xTop]
                    if shiftTop > scaleData[QwtPlot.xTop].tickOffset:
                        shiftTop = scaleData[QwtPlot.xTop].tickOffset
                    sd.h -= shiftTop
        canvas = plot.canvas()
        left, top, right, bottom = canvas.getContentsMargins()
        minCanvasSize = canvas.minimumSize()
        w = scaleData[QwtPlot.yLeft].w + scaleData[QwtPlot.yRight].w
        cw = max([scaleData[QwtPlot.xBottom].w,
                  scaleData[QwtPlot.xTop].w]) + left + 1 + right + 1
        w += max([cw, minCanvasSize.width()])
        h = scaleData[QwtPlot.xBottom].h + scaleData[QwtPlot.xTop].h
        ch = max([scaleData[QwtPlot.yLeft].h,
                  scaleData[QwtPlot.yRight].h]) + top + 1 + bottom + 1
        h += max([ch, minCanvasSize.height()])
        for label in [plot.titleLabel(), plot.footerLabel()]:
            if label and not label.text().isEmpty():
                centerOnCanvas = not plot.axisEnabled(QwtPlot.yLeft)\
                                 and plot.axisEnabled(QwtPlot.yRight)
                labelW = w
                if centerOnCanvas:
                    labelW -= scaleData[QwtPlot.yLeft].w +\
                              scaleData[QwtPlot.yRight].w
                labelH = label.heightForWidth(labelW)
                if labelH > labelW:
                    w = labelW = labelH
                    if centerOnCanvas:
                        w += scaleData[QwtPlot.yLeft].w +\
                             scaleData[QwtPlot.yRight].w
                    labelH = label.heightForWidth(labelW)
                h += labelH + self.__data.spacing
        legend = plot.legend()
        if legend and not legend.isEmpty():
            if self.__data.legendPos in (QwtPlot.LeftLegend,
                                         QwtPlot.RightLegend):
                legendW = legend.sizeHint().width()
                legendH = legend.heightForWidth(legendW)
                if legend.frameWidth() > 0:
                    w += self.__data.spacing
                if legendH > h:
                    legendW += legend.scrollExtent(Qt.Horizontal)
                if self.__data.legendRatio < 1.:
                    legendW = min([legendW, int(w/(1.-self.__data.legendRatio))])
                w += legendW + self.__data.spacing
            else:
                legendW = min([legend.sizeHint().width(), w])
                legendH = legend.heightForWidth(legendW)
                if legend.frameWidth() > 0:
                    h += self.__data.spacing
                if self.__data.legendRatio < 1.:
                    legendH = min([legendH, int(h/(1.-self.__data.legendRatio))])
                h += legendH + self.__data.spacing
        return QSize(w, h)
    
    def layoutLegend(self, options, rect):
        hint = self.__data.layoutData.legend.hint
        if self.__data.legendPos in (QwtPlot.LeftLegend, QwtPlot.RightLegend):
            dim = min([hint.width(), int(rect.width()*self.__data.legendRatio)])
            if not (options & self.IgnoreScrollbars):
                if hint.height() > rect.height():
                    dim += self.__data.layoutData.legend.hScrollExtent
        else:
            dim = min([hint.height(), int(rect.height()*self.__data.legendRatio)])
            dim = max([dim, self.__data.layoutData.legend.vScrollExtent])
        legendRect = QRectF(rect)
        if self.__data.legendPos == QwtPlot.LeftLegend:
            legendRect.setWidth(dim)
        elif self.__data.legendPos == QwtPlot.RightLegend:
            legendRect.setX(rect.right()-dim)
            legendRect.setWidth(dim)
        elif self.__data.legendPos == QwtPlot.TopLegend:
            legendRect.setHeight(dim)
        elif self.__data.legendPos == QwtPlot.BottomLegend:
            legendRect.setY(rect.bottom()-dim)
            legendRect.setHeight(dim)
        return legendRect
    
    def alignLegend(self, canvasRect, legendRect):
        alignedRect = legendRect
        if self.__data.legendPos in (QwtPlot.BottomLegend, QwtPlot.TopLegend):
            if self.__data.layoutData.legend.hint.width() < canvasRect.width():
                alignedRect.setX(canvasRect.x())
                alignedRect.setWidth(canvasRect.width())
        else:
            if self.__data.layoutData.legend.hint.height() < canvasRect.height():
                alignedRect.setY(canvasRect.y())
                alignedRect.setHeight(canvasRect.height())
        return alignedRect
    
    def expandLineBreaks(self, options, rect):
        dimTitle = dimFooter = 0
        dimAxis = [0 for axis in range(QwtPlot.axisCnt)]
        backboneOffset = [0 for _i in range(QwtPlot.axisCnt)]
        for axis in range(QwtPlot.axisCnt):
            if not (options & self.IgnoreFrames):
                backboneOffset[axis] += self.__data.layoutData.canvas.contentsMargins[axis]
            if not self.__data.alignCanvasToScales[axis]:
                backboneOffset[axis] += self.__data.canvasMargin[axis]
        done = False
        while not done:
            done = True
            if not ((options & self.IgnoreTitle) or \
                    self.__data.layoutData.title.text.isEmpty()):
                w = rect.width()
                if self.__data.layoutData.scale[QwtPlot.yLeft].isEnabled !=\
                   self.__data.layoutData.scale[QwtPlot.yRight].isEnabled:
                    w -= dimAxis[QwtPlot.yLeft]+dimAxis[QwtPlot.yRight]
                d = np.ceil(self.__data.layoutData.title.text.heightForWidth(w))
                if not (options & self.IgnoreFrames):
                    d += 2*self.__data.layoutData.title.frameWidth
                if d > dimTitle:
                    dimTitle = d
                    done = False
            if not ((options & self.IgnoreFooter) or \
                    self.__data.layoutData.footer.text.isEmpty()):
                w = rect.width()
                if self.__data.layoutData.scale[QwtPlot.yLeft].isEnabled !=\
                   self.__data.layoutData.scale[QwtPlot.yRight].isEnabled:
                    w -= dimAxis[QwtPlot.yLeft]+dimAxis[QwtPlot.yRight]
                d = np.ceil(self.__data.layoutData.footer.text.heightForWidth(w))
                if not (options & self.IgnoreFrames):
                    d += 2*self.__data.layoutData.footer.frameWidth
                if d > dimFooter:
                    dimFooter = d
                    done = False
            for axis in range(QwtPlot.axisCnt):
                scaleData = self.__data.layoutData.scale[axis]
                if scaleData.isEnabled:
                    if axis in (QwtPlot.xTop, QwtPlot.xBottom):
                        length = rect.width()-dimAxis[QwtPlot.yLeft]-dimAxis[QwtPlot.yRight]
                        length -= scaleData.start + scaleData.end
                        if dimAxis[QwtPlot.yRight] > 0:
                            length -= 1
                        length += min([dimAxis[QwtPlot.yLeft],
                               scaleData.start-backboneOffset[QwtPlot.yLeft]])
                        length += min([dimAxis[QwtPlot.yRight],
                               scaleData.end-backboneOffset[QwtPlot.yRight]])
                    else:
                        length = rect.height()-dimAxis[QwtPlot.xTop]-dimAxis[QwtPlot.xBottom]
                        length -= scaleData.start + scaleData.end
                        length -= 1
                        if dimAxis[QwtPlot.xBottom] <= 0:
                            length -= 1
                        if dimAxis[QwtPlot.xTop] <= 0:
                            length -= 1
                        if dimAxis[QwtPlot.xBottom] > 0:
                            length += min([self.__data.layoutData.scale[QwtPlot.xBottom].tickOffset,
                                           float(scaleData.start-backboneOffset[QwtPlot.xBottom])])
                        if dimAxis[QwtPlot.xTop] > 0:
                            length += min([self.__data.layoutData.scale[QwtPlot.xTop].tickOffset,
                                           float(scaleData.end-backboneOffset[QwtPlot.xTop])])
                        if dimTitle > 0:
                            length -= dimTitle + self.__data.spacing
                    d = scaleData.dimWithoutTitle
                    if not scaleData.scaleWidget.title().isEmpty():
                        d += scaleData.scaleWidget.titleHeightForWidth(np.floor(length))
                    if d > dimAxis[axis]:
                        dimAxis[axis] = d
                        done = False
        return dimTitle, dimFooter, dimAxis
                        
    def alignScales(self, options, canvasRect, scaleRect):
        backboneOffset = [0 for _i in range(QwtPlot.axisCnt)]
        for axis in range(QwtPlot.axisCnt):
            backboneOffset[axis] = 0
            if not self.__data.alignCanvasToScales[axis]:
                backboneOffset[axis] += self.__data.canvasMargin[axis]
            if not options & self.IgnoreFrames:
                backboneOffset[axis] += self.__data.layoutData.canvas.contentsMargins[axis]
        for axis in range(QwtPlot.axisCnt):
            if not scaleRect[axis].isValid():
                continue
            startDist = self.__data.layoutData.scale[axis].start
            endDist = self.__data.layoutData.scale[axis].end
            axisRect = scaleRect[axis]
            if axis in (QwtPlot.xTop, QwtPlot.xBottom):
                leftScaleRect = scaleRect[QwtPlot.yLeft]
                leftOffset = backboneOffset[QwtPlot.yLeft]-startDist
                if leftScaleRect.isValid():
                    dx = leftOffset + leftScaleRect.width()
                    if self.__data.alignCanvasToScales[QwtPlot.yLeft] and dx < 0.:
                        cLeft = canvasRect.left()
                        canvasRect.setLeft(max([cLeft, axisRect.left()-dx]))
                    else:
                        minLeft = leftScaleRect.left()
                        left = axisRect.left()+leftOffset
                        axisRect.setLeft(max([left, minLeft]))
                else:
                    if self.__data.alignCanvasToScales[QwtPlot.yLeft] and leftOffset < 0:
                        canvasRect.setLeft(max([canvasRect.left(),
                                                axisRect.left()-leftOffset]))
                    else:
                        if leftOffset > 0:
                            axisRect.setLeft(axisRect.left()+leftOffset)
                rightScaleRect = scaleRect[QwtPlot.yRight]
                rightOffset = backboneOffset[QwtPlot.yRight]-endDist+1
                if rightScaleRect.isValid():
                    dx = rightOffset+rightScaleRect.width()
                    if self.__data.alignCanvasToScales[QwtPlot.yRight] and dx < 0:
                        cRight = canvasRect.right()
                        canvasRect.setRight(min([cRight, axisRect.right()+dx]))
                    maxRight = rightScaleRect.right()
                    right = axisRect.right()-rightOffset
                    axisRect.setRight(min([right, maxRight]))
                else:
                    if self.__data.alignCanvasToScales[QwtPlot.yRight] and rightOffset < 0:
                        canvasRect.setRight(min([canvasRect.right(),
                                                 axisRect.right()+rightOffset]))
                    else:
                        if rightOffset > 0:
                            axisRect.setRight(axisRect.right()-rightOffset)
            else:
                bottomScaleRect = scaleRect[QwtPlot.xBottom]
                bottomOffset = backboneOffset[QwtPlot.xBottom]-endDist+1
                if bottomScaleRect.isValid():
                    dy = bottomOffset+bottomScaleRect.height()
                    if self.__data.alignCanvasToScales[QwtPlot.xBottom] and dy < 0:
                        cBottom = canvasRect.bottom()
                        canvasRect.setBottom(min([cBottom, axisRect.bottom()+dy]))
                    else:
                        maxBottom = bottomScaleRect.top()+\
                            self.__data.layoutData.scale[QwtPlot.xBottom].tickOffset
                        bottom = axisRect.bottom()-bottomOffset
                        axisRect.setBottom(min([bottom, maxBottom]))
                else:
                    if self.__data.alignCanvasToScales[QwtPlot.xBottom] and bottomOffset < 0:
                        canvasRect.setBottom(min([canvasRect.bottom(),
                                                  axisRect.bottom()+bottomOffset]))
                    else:
                        if bottomOffset > 0:
                            axisRect.setBottom(axisRect.bottom()-bottomOffset)
                topScaleRect = scaleRect[QwtPlot.xTop]
                topOffset = backboneOffset[QwtPlot.xTop]-startDist
                if topScaleRect.isValid():
                    dy = topOffset+topScaleRect.height()
                    if self.__data.alignCanvasToScales[QwtPlot.xTop] and dy < 0:
                        cTop = canvasRect.top()
                        canvasRect.setTop(max([cTop, axisRect.top()-dy]))
                    else:
                        minTop = topScaleRect.bottom()-\
                                 self.__data.layoutData.scale[QwtPlot.xTop].tickOffset
                        top = axisRect.top()+topOffset
                        axisRect.setTop(max([top, minTop]))
                else:
                    if self.__data.alignCanvasToScales[QwtPlot.xTop] and topOffset < 0:
                        canvasRect.setTop(max([canvasRect.top(),
                                               axisRect.top()-topOffset]))
                    else:
                        if topOffset > 0:
                            axisRect.setTop(axisRect.top()+topOffset)
        for axis in range(QwtPlot.axisCnt):
            sRect = scaleRect[axis]
            if not sRect.isValid():
                continue
            if axis in (QwtPlot.xBottom, QwtPlot.xTop):
                if self.__data.alignCanvasToScales[QwtPlot.yLeft]:
                    y = canvasRect.left()-self.__data.layoutData.scale[axis].start
                    if not options & self.IgnoreFrames:
                        y += self.__data.layoutData.canvas.contentsMargins[QwtPlot.yLeft]
                    sRect.setLeft(y)
                if self.__data.alignCanvasToScales[QwtPlot.yRight]:
                    y = canvasRect.right()-1+self.__data.layoutData.scale[axis].end
                    if not options & self.IgnoreFrames:
                        y -= self.__data.layoutData.canvas.contentsMargins[QwtPlot.yRight]
                    sRect.setRight(y)
                if self.__data.alignCanvasToScales[axis]:
                    if axis == QwtPlot.xTop:
                        sRect.setBottom(canvasRect.top())
                    else:
                        sRect.setTop(canvasRect.bottom())
            else:
                if self.__data.alignCanvasToScales[QwtPlot.xTop]:
                    x = canvasRect.top()-self.__data.layoutData.scale[axis].start
                    if not options & self.IgnoreFrames:
                        x += self.__data.layoutData.canvas.contentsMargins[QwtPlot.xTop]
                    sRect.setTop(x)
                if self.__data.alignCanvasToScales[QwtPlot.xBottom]:
                    x = canvasRect.bottom()-1+self.__data.layoutData.scale[axis].end
                    if not options & self.IgnoreFrames:
                        x -= self.__data.layoutData.canvas.contentsMargins[QwtPlot.xBottom]
                    sRect.setBottom(x)
                if self.__data.alignCanvasToScales[axis]:
                    if axis == QwtPlot.yLeft:
                        sRect.setRight(canvasRect.left())
                    else:
                        sRect.setLeft(canvasRect.right())
    
    def activate(self, plot, plotRect, options=0x00):
        self.invalidate()
        rect = QRectF(plotRect)
        self.__data.layoutData.init(plot, rect)
        if not (options & self.IgnoreLegend) and plot.legend() and\
           not plot.legend().isEmpty():
            self.__data.legendRect = self.layoutLegend(options, rect)
            region = QRegion(rect.toRect())
            rect = region.subtracted(QRegion(self.__data.legendRect.toRect())
                                     ).boundingRect()
            if self.__data.legendPos == QwtPlot.LeftLegend:
                rect.setLeft(rect.left()+self.__data.spacing)
            elif self.__data.legendPos == QwtPlot.RightLegend:
                rect.setRight(rect.right()-self.__data.spacing)
            elif self.__data.legendPos == QwtPlot.TopLegend:
                rect.setTop(rect.top()+self.__data.spacing)
            elif self.__data.legendPos == QwtPlot.BottomLegend:
                rect.setBottom(rect.bottom()-self.__data.spacing)
        
#     +---+-----------+---+
#     |       Title       |
#     +---+-----------+---+
#     |   |   Axis    |   |
#     +---+-----------+---+
#     | A |           | A |
#     | x |  Canvas   | x |
#     | i |           | i |
#     | s |           | s |
#     +---+-----------+---+
#     |   |   Axis    |   |
#     +---+-----------+---+
#     |      Footer       |
#     +---+-----------+---+

        dimTitle, dimFooter, dimAxes = self.expandLineBreaks(options, rect)
        if dimTitle > 0:
            self.__data.titleRect.setRect(rect.left(), rect.top(),
                                          rect.width(), dimTitle)
            rect.setTop(self.__data.titleRect.bottom()+self.__data.spacing)
            if self.__data.layoutData.scale[QwtPlot.yLeft].isEnabled !=\
               self.__data.layoutData.scale[QwtPlot.yRight].isEnabled:
                self.__data.titleRect.setX(rect.left()+dimAxes[QwtPlot.yLeft])
                self.__data.titleRect.setWidth(rect.width()\
                            -dimAxes[QwtPlot.yLeft]-dimAxes[QwtPlot.yRight])
        if dimFooter > 0:
            self.__data.footerRect.setRect(rect.left(),
                           rect.bottom()-dimFooter, rect.width(), dimFooter)
            rect.setBottom(self.__data.footerRect.top()-self.__data.spacing)
            if self.__data.layoutData.scale[QwtPlot.yLeft].isEnabled !=\
               self.__data.layoutData.scale[QwtPlot.yRight].isEnabled:
                self.__data.footerRect.setX(rect.left()+dimAxes[QwtPlot.yLeft])
                self.__data.footerRect.setWidth(rect.width()\
                            -dimAxes[QwtPlot.yLeft]-dimAxes[QwtPlot.yRight])
        self.__data.canvasRect.setRect(
                rect.x()+dimAxes[QwtPlot.yLeft],
                rect.y()+dimAxes[QwtPlot.xTop],
                rect.width()-dimAxes[QwtPlot.yRight]-dimAxes[QwtPlot.yLeft],
                rect.height()-dimAxes[QwtPlot.xBottom]-dimAxes[QwtPlot.xTop])
        for axis in range(QwtPlot.axisCnt):
            if dimAxes[axis]:
                dim = dimAxes[axis]
                scaleRect = self.__data.scaleRect[axis]
                scaleRect.setRect(*self.__data.canvasRect.getRect())
                if axis == QwtPlot.yLeft:
                    scaleRect.setX(self.__data.canvasRect.left()-dim)
                    scaleRect.setWidth(dim)
                elif axis == QwtPlot.yRight:
                    scaleRect.setX(self.__data.canvasRect.right())
                    scaleRect.setWidth(dim)
                elif axis == QwtPlot.xBottom:
                    scaleRect.setY(self.__data.canvasRect.bottom())
                    scaleRect.setHeight(dim)
                elif axis == QwtPlot.xTop:
                    scaleRect.setY(self.__data.canvasRect.top()-dim)
                    scaleRect.setHeight(dim)
                scaleRect = scaleRect.normalized()
                
#       +---+-----------+---+
#       |  <-   Axis   ->   |
#       +-^-+-----------+-^-+
#       | | |           | | |
#       |   |           |   |
#       | A |           | A |
#       | x |  Canvas   | x |
#       | i |           | i |
#       | s |           | s |
#       |   |           |   |
#       | | |           | | |
#       +-V-+-----------+-V-+
#       |   <-  Axis   ->   |
#       +---+-----------+---+
                
        self.alignScales(options, self.__data.canvasRect,
                         self.__data.scaleRect)
        if not self.__data.legendRect.isEmpty():
            self.__data.legendRect = self.alignLegend(self.__data.canvasRect,
                                                      self.__data.legendRect)
