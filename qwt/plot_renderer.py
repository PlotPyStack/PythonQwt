# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see qwt/LICENSE for details)

from __future__ import division

from qwt.painter import QwtPainter
from qwt.plot import QwtPlot
from qwt.plot_layout import QwtPlotLayout
from qwt.scale_draw import QwtScaleDraw
from qwt.scale_map import QwtScaleMap

from qwt.qt.QtGui import (QPrinter, QPainter, QImageWriter, QImage, QColor,
                          QPaintDevice, QTransform, QPalette, QFileDialog,
                          QPainterPath, QPen)
from qwt.qt.QtCore import Qt, QRect, QRectF, QObject, QSizeF
from qwt.qt.QtSvg import QSvgGenerator
from qwt.qt.compat import getsavefilename

import numpy as np
import os.path as osp


def qwtCanvasClip(canvas, canvasRect):
    x1 = np.ceil(canvasRect.left())
    x2 = np.floor(canvasRect.right())
    y1 = np.ceil(canvasRect.top())
    y2 = np.floor(canvasRect.bottom())
    r = QRect(x1, y1, x2-x1-1, y2-y1-1)
    return canvas.borderPath(r)


class QwtPlotRenderer_PrivateData(object):
    def __init__(self):
        self.discardFlags = QwtPlotRenderer.DiscardNone
        self.layoutFlags = QwtPlotRenderer.DefaultLayout

class QwtPlotRenderer(QObject):
    
    # enum DiscardFlag
    DiscardNone = 0x00
    DiscardBackground = 0x01
    DiscardTitle = 0x02
    DiscardLegend = 0x04
    DiscardCanvasBackground = 0x08
    DiscardFooter = 0x10
    DiscardCanvasFrame = 0x20
    
    # enum LayoutFlag
    DefaultLayout = 0x00
    FrameWithScales = 0x01
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.__data = QwtPlotRenderer_PrivateData()
    
    def setDiscardFlag(self, flag, on):
        if on:
            self.__data.discardFlags |= flag
        else:
            self.__data.discardFlags &= ~flag
    
    def testDiscardFlag(self, flag):
        return self.__data.discardFlags & flag
    
    def setDiscardFlags(self, flags):
        self.__data.discardFlags = flags
    
    def discardFlags(self):
        return self.__data.discardFlags
    
    def setLayoutFlag(self, flag, on):
        if on:
            self.__data.layoutFlags |= flag
        else:
            self.__data.layoutFlags &= ~flag
    
    def testLayoutFlag(self, flag):
        return self.__data.layoutFlags & flag

    def setLayoutFlags(self, flags):
        self.__data.layoutFlags = flags
    
    def layoutFlags(self):
        return self.__data.layoutFlags
    
    def renderDocument(self, plot, filename, sizeMM=(300, 200), resolution=85,
                       format_=None):
        if isinstance(sizeMM, tuple):
            sizeMM = QSizeF(*sizeMM)
        if format_ is None:
            ext = osp.splitext(filename)[1]
            if not ext:
                raise TypeError("Unable to determine target format from filename")
            format_ = ext[1:]
        if plot is None or sizeMM.isEmpty() or resolution <= 0:
            return
        title = plot.title().text()
        if not title:
            title = "Plot Document"
        mmToInch = 1./25.4
        size = sizeMM * mmToInch * resolution
        documentRect = QRectF(0.0, 0.0, size.width(), size.height())
        fmt = format_.lower()
        if fmt in ("pdf", "ps"):
            printer = QPrinter()
            if fmt == "pdf":
                printer.setOutputFormat(QPrinter.PdfFormat)
            else:
                printer.setOutputFormat(QPrinter.PostScriptFormat)
            printer.setColorMode(QPrinter.Color)
            printer.setFullPage(True)
            printer.setPaperSize(sizeMM, QPrinter.Millimeter)
            printer.setDocName(title)
            printer.setOutputFileName(filename)
            printer.setResolution(resolution)
            painter = QPainter(printer)
            self.render(plot, painter, documentRect)
            painter.end()
        elif fmt == "svg":
            generator = QSvgGenerator()
            generator.setTitle(title)
            generator.setFileName(filename)
            generator.setResolution(resolution)
            generator.setViewBox(documentRect)
            painter = QPainter(generator)
            self.render(plot, painter, documentRect)
            painter.end()
        elif fmt in QImageWriter.supportedImageFormats():
            imageRect = documentRect.toRect()
            dotsPerMeter = int(round(resolution*mmToInch*1000.))
            image = QImage(imageRect.size(), QImage.Format_ARGB32)
            image.setDotsPerMeterX(dotsPerMeter)
            image.setDotsPerMeterY(dotsPerMeter)
            image.fill(QColor(Qt.white).rgb())
            painter = QPainter(image)
            self.render(plot, painter, imageRect)
            painter.end()
            image.save(filename, fmt)
        else:
            raise TypeError("Unsupported file format '%s'" % fmt)

    def renderTo(self, plot, dest):
        if isinstance(dest, QPaintDevice):
            w = dest.width()
            h = dest.height()
            rect = QRectF(0, 0, w, h)
        elif isinstance(dest, QPrinter):
            w = dest.width()
            h = dest.height()
            rect = QRectF(0, 0, w, h)
            aspect = rect.width()/rect.height()
            if aspect < 1.:
                rect.setHeight(aspect*rect.width())
        elif isinstance(dest, QSvgGenerator):
            rect = dest.viewBoxF()
            if rect.isEmpty():
                rect.setRect(0, 0, dest.width(), dest.height())
            if rect.isEmpty():
                rect.setRect(0, 0, 800, 600)
        p = QPainter(dest)
        self.render(plot, p, rect)
    
    def render(self, plot, painter, plotRect):
        if painter == 0 or not painter.isActive() or not plotRect.isValid()\
           or plot.size().isNull():
            return
        if not self.__data.discardFlags & self.DiscardBackground:
            QwtPainter.drawBackground(painter, plotRect, plot)

        transform = QTransform()
        transform.scale(float(painter.device().logicalDpiX())/plot.logicalDpiX(),
                        float(painter.device().logicalDpiY())/plot.logicalDpiY())
        
        invtrans, _ok = transform.inverted()
        layoutRect = invtrans.mapRect(plotRect)
        if not (self.__data.discardFlags & self.DiscardBackground):
            left, top, right, bottom = plot.getContentsMargins()
            layoutRect.adjust(left, top, -right, -bottom)

        layout = plot.plotLayout()
        baseLineDists = [None]*QwtPlot.axisCnt
        canvasMargins = [None]*QwtPlot.axisCnt

        for axisId in range(QwtPlot.axisCnt):
            canvasMargins[axisId] = layout.canvasMargin(axisId)
            if self.__data.layoutFlags & self.FrameWithScales:
                scaleWidget = plot.axisWidget(axisId)
                if scaleWidget:
                    baseLineDists[axisId] = scaleWidget.margin()
                    scaleWidget.setMargin(0)
                if not plot.axisEnabled(axisId):
                    left, right, top, bottom = 0, 0, 0, 0
                    if axisId == QwtPlot.yLeft:
                        layoutRect.adjust(1, 0, 0, 0)
                    elif axisId == QwtPlot.yRight:
                        layoutRect.adjust(0, 0, -1, 0)
                    elif axisId == QwtPlot.xTop:
                        layoutRect.adjust(0, 1, 0, 0)
                    elif axisId == QwtPlot.xBottom:
                        layoutRect.adjust(0, 0, 0, -1)
                    layoutRect.adjust(left, top, right, bottom)
        
        layoutOptions = QwtPlotLayout.IgnoreScrollbars
        
        if self.__data.layoutFlags & self.FrameWithScales or\
           self.__data.discardFlags & self.DiscardCanvasFrame:
            layoutOptions |= QwtPlotLayout.IgnoreFrames
        
        if self.__data.discardFlags & self.DiscardLegend:
            layoutOptions |= QwtPlotLayout.IgnoreLegend
        if self.__data.discardFlags & self.DiscardTitle:
            layoutOptions |= QwtPlotLayout.IgnoreTitle
        if self.__data.discardFlags & self.DiscardFooter:
            layoutOptions |= QwtPlotLayout.IgnoreFooter
        
        layout.activate(plot, layoutRect, layoutOptions)

        maps = self.buildCanvasMaps(plot, layout.canvasRect())
        if self.updateCanvasMargins(plot, layout.canvasRect(), maps):
            layout.activate(plot, layoutRect, layoutOptions)
            maps = self.buildCanvasMaps(plot, layout.canvasRect())
        
        painter.save()
        painter.setWorldTransform(transform, True)
        
        self.renderCanvas(plot, painter, layout.canvasRect(), maps)
        
        if (not self.__data.discardFlags & self.DiscardTitle) and\
           plot.titleLabel().text():
            self.renderTitle(plot, painter, layout.titleRect())
        
        if (not self.__data.discardFlags & self.DiscardFooter) and\
           plot.titleLabel().text():
            self.renderFooter(plot, painter, layout.footerRect())
            
        if (not self.__data.discardFlags & self.DiscardLegend) and\
           plot.titleLabel().text():
            self.renderLegend(plot, painter, layout.legendRect())
            
        for axisId in range(QwtPlot.axisCnt):
            scaleWidget = plot.axisWidget(axisId)
            if scaleWidget:
                baseDist = scaleWidget.margin()
                startDist, endDist = scaleWidget.getBorderDistHint()
                self.renderScale(plot, painter, axisId, startDist, endDist,
                                 baseDist, layout.scaleRect(axisId))
        
        painter.restore()
        
        for axisId in range(QwtPlot.axisCnt):
            if self.__data.layoutFlags & self.FrameWithScales:
                scaleWidget = plot.axisWidget(axisId)
                if scaleWidget:
                    scaleWidget.setMargin(baseLineDists[axisId])
            layout.setCanvasMargin(canvasMargins[axisId])

        layout.invalidate()
    
    def renderTitle(self, plot, painter, rect):
        painter.setFont(plot.titleLabel().font())
        color = plot.titleLabel().palette().color(QPalette.Active, QPalette.Text)
        painter.setPen(color)
        plot.titleLabel().text().draw(painter, rect)
    
    def renderFooter(self, plot, painter, rect):
        painter.setFont(plot.footerLabel().font())
        color = plot.footerLabel().palette().color(QPalette.Active, QPalette.Text)
        painter.setPen(color)
        plot.footerLabel().text().draw(painter, rect)
    
    def renderLegend(self, plot, painter, rect):
        if plot.legend():
            fillBackground = not self.__data.discardFlags & self.DiscardBackground
            plot.legend().renderLegend(painter, rect, fillBackground)
        
    def renderScale(self, plot, painter, axisId, startDist, endDist,
                    baseDist, rect):
        if not plot.axisEnabled(axisId):
            return
        scaleWidget = plot.axisWidget(axisId)
        if scaleWidget.isColorBarEnabled() and scaleWidget.colorBarWidth() > 0:
            scaleWidget.drawColorBar(painter, scaleWidget.colorBarRect(rect))
            baseDist += scaleWidget.colorBarWidth() + scaleWidget.spacing()
        painter.save()
        if axisId == QwtPlot.yLeft:
            x = rect.right() - 1.0 - baseDist
            y = rect.y() + startDist
            w = rect.height() - startDist - endDist
            align = QwtScaleDraw.LeftScale
        elif axisId == QwtPlot.yRight:
            x = rect.left() + baseDist
            y = rect.y() + startDist
            w = rect.height() - startDist - endDist
            align = QwtScaleDraw.RightScale
        elif axisId == QwtPlot.xTop:
            x = rect.left() + startDist
            y = rect.bottom() - 1.0 - baseDist
            w = rect.width() - startDist - endDist
            align = QwtScaleDraw.TopScale
        elif axisId == QwtPlot.xBottom:
            x = rect.left() + startDist
            y = rect.top() + baseDist
            w = rect.width() - startDist - endDist
            align = QwtScaleDraw.BottomScale
        
        scaleWidget.drawTitle(painter, align, rect)
        painter.setFont(scaleWidget.font())
        sd = scaleWidget.scaleDraw()
        sdPos = sd.pos()
        sdLength = sd.length()
        sd.move(x, y)
        sd.setLength(w)
        palette = scaleWidget.palette()
        palette.setCurrentColorGroup(QPalette.Active)
        sd.draw(painter, palette)
        sd.move(sdPos)
        sd.setLength(sdLength)
        painter.restore()
        
    def renderCanvas(self, plot, painter, canvasRect, maps):
        canvas = plot.canvas()
        r = canvasRect.adjusted(0., 0., -1., 1.)
        if self.__data.layoutFlags & self.FrameWithScales:
            painter.save()
            r.adjust(-1., -1., 1., 1.)
            painter.setPen(QPen(Qt.black))
            if not (self.__data.discardFlags & self.DiscardCanvasBackground):
                bgBrush = canvas.palette().brush(plot.backgroundRole())
                painter.setBrush(bgBrush)
            QwtPainter.drawRect(painter, r)
            painter.restore()
            painter.save()
            painter.setClipRect(canvasRect)
            plot.drawItems(painter, canvasRect, maps)
            painter.restore()
        elif canvas.testAttribute(Qt.WA_StyledBackground):
            clipPath = QPainterPath()
            painter.save()
            if not self.__data.discardFlags & self.DiscardCanvasBackground:
                QwtPainter.drawBackground(painter, r, canvas)
                clipPath = qwtCanvasClip(canvas, canvasRect)
            painter.restore()
            painter.save()
            if clipPath.isEmpty():
                painter.setClipRect(canvasRect)
            else:
                painter.setClipPath(clipPath)
            plot.drawItems(painter, canvasRect, maps)
            painter.restore()
        else:
            clipPath = QPainterPath()
            frameWidth = 0
            if not self.__data.discardFlags & self.DiscardCanvasFrame:
                frameWidth = canvas.frameWidth()
                clipPath = qwtCanvasClip(canvas, canvasRect)
            innerRect = canvasRect.adjusted(frameWidth, frameWidth,
                                            -frameWidth, -frameWidth)
            painter.save()
            if clipPath.isEmpty():
                painter.setClipRect(innerRect)
            else:
                painter.setClipPath(clipPath)
            if not self.__data.discardFlags & self.DiscardCanvasBackground:
                QwtPainter.drawBackground(painter, innerRect, canvas)
            plot.drawItems(painter, innerRect, maps)
            painter.restore()
            if frameWidth > 0:
                painter.save()
                frameStyle = canvas.frameShadow() | canvas.frameShape()
                frameWidth = canvas.frameWidth()
                borderRadius = canvas.borderRadius()
                if borderRadius > 0.:
                    QwtPainter.drawRoundedFrame(painter, canvasRect, r, r,
                                                canvas.palette(), frameWidth,
                                                frameStyle)
                else:
                    midLineWidth = canvas.midLineWidth()
                    QwtPainter.drawFrame(painter, canvasRect, canvas.palette(),
                                         canvas.foregroundRole(), frameWidth,
                                         midLineWidth, frameStyle)
                painter.restore()

    def buildCanvasMaps(self, plot, canvasRect):
        maps = []
        for axisId in range(QwtPlot.axisCnt):
            map_ = QwtScaleMap()
            map_.setTransformation(
                                plot.axisScaleEngine(axisId).transformation())
            sd = plot.axisScaleDiv(axisId)
            map_.setScaleInterval(sd.lowerBound(), sd.upperBound())
            if plot.axisEnabled(axisId):
                s = plot.axisWidget(axisId)
                scaleRect = plot.plotLayout().scaleRect(axisId)
                if axisId in (QwtPlot.xTop, QwtPlot.xBottom):
                    from_ = scaleRect.left() + s.startBorderDist()
                    to = scaleRect.right() - s.endBorderDist()
                else:
                    from_ = scaleRect.bottom() - s.endBorderDist()
                    to = scaleRect.top() + s.startBorderDist()
            else:
                margin = 0
                if not plot.plotLayout().alignCanvasToScale(axisId):
                    margin = plot.plotLayout().canvasMargin(axisId)
                if axisId in (QwtPlot.yLeft, QwtPlot.yRight):
                    from_ = canvasRect.bottom() - margin
                    to = canvasRect.top() + margin
                else:
                    from_ = canvasRect.left() + margin
                    to = canvasRect.right() - margin
            map_.setPaintInterval(from_, to)
            maps.append(map_)
        return maps
            
    def updateCanvasMargins(self, plot, canvasRect, maps):
        margins = plot.getCanvasMarginsHint(maps, canvasRect)
        marginsChanged = False
        for axisId in range(QwtPlot.axisCnt):
            if margins[axisId] >= 0.:
                m = np.ceil(margins[axisId])
                plot.plotLayout().setCanvasMargin(m, axisId)
                marginsChanged = True
        return marginsChanged
    
    def exportTo(self, plot, documentname, sizeMM=None, resolution=85):
        if plot is None:
            return
        if sizeMM is None:
            sizeMM = QSizeF(300, 200)
        filename = documentname
        imageFormats = QImageWriter.supportedImageFormats()
        filter_ = ["PDF documents (*.pdf)",
                   "SVG documents (*.svg)",
                   "Postscript documents (*.ps)"]
        if imageFormats:
            imageFilter = "Images"
            imageFilter += " ("
            for idx, fmt in enumerate(imageFormats):
                if idx > 0:
                    imageFilter += " "
                imageFilter += "*."+str(fmt)
            imageFilter += ")"
            filter_ += [imageFilter]
        filename, _s = getsavefilename(plot, "Export File Name", filename,
                                   ";;".join(filter_),
                                   options=QFileDialog.DontConfirmOverwrite)
        if not filename:
            return False
        self.renderDocument(plot, filename, sizeMM, resolution)
        return True
