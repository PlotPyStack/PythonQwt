# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtPainterClass
---------------

.. autoclass:: QwtPainterClass
   :members:
"""

from qwt.clipper import QwtClipper
from qwt.color_map import QwtColorMap

from qwt.qt.QtGui import (QPaintEngine, QApplication, QFont, QFontInfo, QFrame,
                          QPixmap, QPainter, QPolygonF, QPalette, QStyle, QPen,
                          QAbstractTextDocumentLayout, QStyleOptionFocusRect,
                          QBrush, QLinearGradient, QPainterPath, QColor,
                          QStyleOption, QPolygon, QTransform)
from qwt.qt.QtCore import (QSize, QRectF, Qt, QPointF, QSizeF, QRect, QPoint,
                           QT_VERSION)

import numpy as np

QWIDGETSIZE_MAX = (1<<24)-1


def qwtIsClippingNeeded(painter):
    doClipping = False
    clipRect = QRectF()
    #TODO: remove next line when QwtClipper will be implemented
    return doClipping, clipRect
    pe = painter.paintEngine()
    if pe and pe.type() == QPaintEngine.SVG:
        if painter.hasClipping():
            doClipping = True
            clipRect = painter.clipRegion().boundingRect()
    return doClipping, clipRect


def qwtDrawPolyline(painter, points, pointCount, polylineSplitting):
    doSplit = False
    if polylineSplitting:
        pe = painter.paintEngine()
        if pe and pe.type() == QPaintEngine.Raster:
            doSplit = True
    if False:#doSplit:  #FIXME: uncomment "doSplit", and fix associated bug (or solve performance issue...)
        splitSize = 6
        for i in range(0, pointCount, splitSize):
            n = min([splitSize+1, pointCount-i])
            painter.drawPolyline(points+i, n)
    else:
        painter.drawPolyline(points)


def qwtScreenResolution():
    screenResolution = QSize()
    if not screenResolution.isValid():
        desktop = QApplication.desktop()
        if desktop is not None:
            screenResolution.setWidth(desktop.logicalDpiX())
            screenResolution.setHeight(desktop.logicalDpiY())
    return screenResolution


def qwtUnscaleFont(painter):
    if painter.font().pixelSize() >= 0:
        return
    screenResolution = qwtScreenResolution()
    pd = painter.device()
    if pd.logicalDpiX() != screenResolution.width() or\
       pd.logicalDpiY() != screenResolution.height():
        pixelFont = QFont(painter.font(), QApplication.desktop())
        pixelFont.setPixelSize(QFontInfo(pixelFont).pixelSize())
        painter.setFont(pixelFont)


def isX11GraphicsSystem():
    pm = QPixmap(1, 1)
    painter = QPainter(pm)
    isX11 = painter.paintEngine().type() == QPaintEngine.X11
    del painter
    return isX11


class QwtPainterClass(object):
    """A collection of `QPainter` workarounds"""
    
    def __init__(self):
        self.__polylineSplitting = True
        self.__roundingAlignment = True
        
    def isAligning(self, painter):
        """
        Check if the painter is using a paint engine, that aligns
        coordinates to integers. Today these are all paint engines
        beside `QPaintEngine.Pdf` and `QPaintEngine.SVG`.

        If we have an integer based paint engine it is also
        checked if the painter has a transformation matrix,
        that rotates or scales.
        
        :param QPainter painter: Painter
        :return: true, when the painter is aligning

        .. seealso::
        
            :py:meth:`setRoundingAlignment()`
        """
        if painter and painter.isActive():
            if painter.paintEngine().type() in (QPaintEngine.Pdf,
                                                QPaintEngine.SVG):
                return False
            tr = painter.transform()
            if tr.isRotating() or tr.isScaling():
                return False
        return True
    
    def setRoundingAlignment(self, enable):
        """
        Enable whether coordinates should be rounded, before they are 
        painted to a paint engine that floors to integer values. For other 
        paint engines this ( PDF, SVG ), this flag has no effect.
        `QwtPainter` stores this flag only, the rounding itself is done in 
        the painting code ( f.e the plot items ).
        
        The default setting is true.
        
        :param bool enable: enable/disable

        .. seealso::
        
            :py:meth:`roundingAlignment()`, :py:meth:`isAligning()`
        """
        self.__roundingAlignment = enable
    
    def roundingAlignment(self, painter=None):
        if painter is None:
            return self.__roundingAlignment
        else:
            return self.__roundingAlignment and self.isAligning(painter)
    
    def setPolylineSplitting(self, enable):
        """
        En/Disable line splitting for the raster paint engine

        In some Qt versions the raster paint engine paints polylines of 
        many points much faster when they are split in smaller chunks: 
        f.e all supported Qt versions >= Qt 5.0 when drawing an 
        antialiased polyline with a pen width >=2.
        
        :param bool enable: enable/disable

        .. seealso::
        
            :py:meth:`polylineSplitting()`
        """
        self.__polylineSplitting = enable
    
    def polylineSplitting(self):
        return self.__polylineSplitting
    
    def drawPath(self, painter, path):
        painter.drawPath(path)
    
    def drawRect(self, *args):
        if len(args) == 5:
            painter, x, y, w, h = args
            self.drawRect(painter, QRectF(x, y, w, h))
        elif len(args) == 2:
            painter, rect = args
            r = rect
            deviceClipping, clipRect = qwtIsClippingNeeded(painter)
            if deviceClipping:
                if not clipRect.intersects(r):
                    return
                if not clipRect.contains(r):
                    self.fillRect(painter, r & clipRect, painter.brush())
                    painter.save()
                    painter.setBrush(Qt.NoBrush)
                    self.drawPolyline(painter, QPolygonF(r))
                    painter.restore()
                    return
            painter.drawRect(r)
        else:
            raise TypeError("QwtPainter.drawRect() takes 2 or 5 argument(s) "\
                            "(%s given)" % len(args))
    
    def fillRect(self, painter, rect, brush):
        if not rect.isValid():
            return
        deviceClipping, clipRect = qwtIsClippingNeeded(painter)
        if deviceClipping:
            clipRect &= painter.window()
        else:
            clipRect = painter.window()
        if painter.hasClipping():
            clipRect &= painter.clipRegion().boundingRect()
        r = rect
        if deviceClipping:
            r = r.intersected(clipRect)
        if r.isValid():
            painter.fillRect(r, brush)
    
    def drawPie(self, painter, rect, a, alen):
        deviceClipping, clipRect = qwtIsClippingNeeded(painter)
        if deviceClipping and not clipRect.contains(rect):
            return
        painter.drawPie(rect, a, alen)
        
    def drawEllipse(self, painter, rect):
        deviceClipping, clipRect = qwtIsClippingNeeded(painter)
        if deviceClipping and not clipRect.contains(rect):
            return
        painter.drawEllipse(rect)
    
    def drawText(self, *args):
        if len(args) == 4:
            if isinstance(args[1], (QRectF, QRect)):
                painter, rect, flags, text = args
                painter.save()
                qwtUnscaleFont(painter)
                painter.drawText(rect, flags, text)
                painter.restore()
            else:
                painter, x, y, text = args
                self.drawText(painter, QPointF(x, y), text)
        elif len(args) == 3:
            painter, pos, text = args
            deviceClipping, clipRect = qwtIsClippingNeeded(painter)
            if deviceClipping and not clipRect.contains(pos):
                return
            painter.save()
            qwtUnscaleFont(painter)
            painter.drawText(pos, text)
            painter.restore()        
        elif len(args) == 7:
            painter, x, y, w, h, flags, text = args
            self.drawText(painter, QRectF( x, y, w, h ), flags, text)
        else:
            raise TypeError("QwtPainter.drawText() takes 3, 4 or 7 argument"\
                            "(s) (%s given)" % len(args))
    
    def drawSimpleRichText(self, painter, rect, flags, text):
        """
        Draw a text document into a rectangle
        
        :param QPainter painter: Painter
        :param QRectF rect: Target rectangle
        :param int flags: Alignments/Text flags, see `QPainter.drawText()`
        :param QTextDocument text: Text document
        """
        txt = text.clone()
        painter.save()
        unscaledRect = QRectF(rect)
        if painter.font().pixelSize() < 0:
            res = qwtScreenResolution()
            pd = painter.device()
            if pd.logicalDpiX() != res.width()\
               or pd.logicalDpiY() != res.height():
                transform = QTransform()
                transform.scale(res.width()/float(pd.logicalDpiX()),
                                res.height()/float(pd.logicalDpiY()))
                painter.setWorldTransform(transform, True)
                invtrans, _ok = transform.inverted()
                unscaledRect = invtrans.mapRect(rect)
        txt.setDefaultFont(painter.font())
        txt.setPageSize(QSizeF(unscaledRect.width(), QWIDGETSIZE_MAX))
        layout = txt.documentLayout()
        height = layout.documentSize().height()
        y = unscaledRect.y()
        if flags & Qt.AlignBottom:
            y += unscaledRect.height()-height
        elif flags & Qt.AlignVCenter:
            y += (unscaledRect.height()-height)/2
        context = QAbstractTextDocumentLayout.PaintContext()
        context.palette.setColor(QPalette.Text, painter.pen().color())
        painter.translate(unscaledRect.x(), y)
        layout.draw(painter, context)
        painter.restore()
        
    def drawLine(self, *args):
        if len(args) == 3:
            painter, p1, p2 = args
            if isinstance(p1, QPointF):
                p1 = p1.toPoint()
            if isinstance(p2, QPointF):
                p2 = p2.toPoint()
            deviceClipping, clipRect = qwtIsClippingNeeded(painter)
            if deviceClipping and not clipRect.contains(p1)\
               and not clipRect.contains(p2):
                polygon = QPolygonF()
                polygon += p1
                polygon += p2
                self.drawPolyline(painter, polygon)
                return
            painter.drawLine(p1, p2)
        elif len(args) == 5:
            painter, x1, y1, x2, y2 = args
            self.drawLine(painter, QPointF(x1, y1), QPointF(x2, y2))
        elif len(args) == 2:
            painter, line = args
            self.drawLine(painter, line.p1(), line.p2())
        else:
            raise TypeError("QwtPainter.drawLine() takes 2, 3 or 5 argument"\
                            "(s) (%s given)" % len(args))
    
    def drawPolygon(self, painter, polygon):
        deviceClipping, clipRect = qwtIsClippingNeeded(painter)
        cpa = polygon
        if deviceClipping:
            if isinstance(polygon, QPolygonF):
                cpa = QwtClipper().clipPolygonF(clipRect, polygon)
            else:
                cpa = QwtClipper().clipPolygon(clipRect, polygon)
        painter.drawPolygon(cpa)
    
    def drawPolyline(self, *args):
        if len(args) == 2:
            painter, polygon = args
            deviceClipping, clipRect = qwtIsClippingNeeded(painter)
            cpa = polygon
            if deviceClipping:
                if isinstance(polygon, QPolygonF):
                    cpa = QwtClipper().clipPolygonF(clipRect, polygon)
                else:
                    cpa = QwtClipper().clipPolygon(clipRect, polygon)
            qwtDrawPolyline(painter, cpa, cpa.size(),
                            self.__polylineSplitting)
        elif len(args) == 3:
            painter, points, pointCount = args
            deviceClipping, clipRect = qwtIsClippingNeeded(painter)
            if deviceClipping:
                if isinstance(points[0], QPointF):
                    polygon = QPolygonF(points)
                    polygon = QwtClipper().clipPolygonF(clipRect, polygon)
                else:
                    polygon = QPolygon(points)
                    polygon = QwtClipper().clipPolygon(clipRect, polygon)
                qwtDrawPolyline(painter, polygon,
                                polygon.size(), self.__polylineSplitting)
#                polygon = QPolygonF(pointCount)
#                pointer = polygon.data()
#                pointer.setsize(pointCount*2*np.finfo(float).dtype.itemsize)
#                memory = np.frombuffer(pointer, float)
#                memory[0::2] = xdata
#                memory[1::2] = ydata
            else:
                qwtDrawPolyline(painter, points, pointCount,
                                self.__polylineSplitting)
        else:
            raise TypeError("QwtPainter.drawPolyline() takes 2 or 3 argument"\
                            "(s) (%s given)" % len(args))
    
    def drawPoint(self, painter, pos):
        deviceClipping, clipRect = qwtIsClippingNeeded(painter)
        if isinstance(pos, QPointF):
            if deviceClipping and not clipRect.contains(pos):
                return
        else:
            if deviceClipping:
                minX = np.ceil(clipRect.left())
                maxX = np.floor(clipRect.right())
                minY = np.ceil(clipRect.top())
                maxY = np.floor(clipRect.bottom())
                if pos.x() < minX or pos.x() > maxX or\
                   pos.y() < minY or pos.y() > maxY:
                    return
        painter.drawPoint(pos)

    def drawPoints(self, painter, *args):
        if len(args) == 2:
            points, pointCount = args
        else:
            polygon, = args
            points, pointCount = polygon.data(), polygon.size()
            if isinstance(polygon, QPolygonF):
                points.setsize(pointCount*np.finfo(float).dtype.itemsize)
            else:
                points.setsize(pointCount*np.iinfo(int).dtype.itemsize)
        deviceClipping, clipRect = qwtIsClippingNeeded(painter)
        if deviceClipping:
            if isinstance(polygon, QPointF):
                minX = np.ceil(clipRect.left())
                maxX = np.floor(clipRect.right())
                minY = np.ceil(clipRect.top())
                maxY = np.floor(clipRect.bottom())
                clipRect = QRect(minX, minY, maxX-minX, maxY-minY)
            clippedPolygon = polygon.intersected(QPolygon(clipRect))
            painter.drawPoints(clippedPolygon)
        else:
            painter.drawPoints(polygon)
    
    def drawImage(self, painter, rect, image):
        alignedRect = rect.toAlignedRect()
        if alignedRect != rect:
            clipRect = rect.adjusted(0., 0., -1., -1.)
            painter.save()
            painter.setClipRect(clipRect, Qt.IntersectClip)
            painter.drawImage(alignedRect, image)
            painter.restore()
        else:
            painter.drawImage(alignedRect, image)
    
    def drawPixmap(self, painter, rect, pixmap):
        alignedRect = rect.toAlignedRect()
        if alignedRect != rect:
            clipRect = rect.adjusted(0., 0., -1., -1.)
            painter.save()
            painter.setClipRect(clipRect, Qt.IntersectClip)
            painter.drawPixmap(alignedRect, pixmap)
            painter.restore()
        else:
            painter.drawPixmap(alignedRect, pixmap)
    
    def drawFocusRect(self, *args):
        if len(args) == 2:
            painter, widget = args
            self.drawFocusRect(painter, widget, widget.rect())
        elif len(args) == 3:
            painter, widget, rect = args
            opt = QStyleOptionFocusRect()
            opt.initFrom(widget)
            opt.rect = rect
            opt.state |= QStyle.State_HasFocus
            widget.style().drawPrimitive(QStyle.PE_FrameFocusRect,
                                         opt, painter, widget)
        else:
            raise TypeError("QwtPainter.drawFocusRect() takes 2 or 3 argument"\
                            "(s) (%s given)" % len(args))
    
    def drawRoundFrame(self, painter, rect, palette, lineWidth, frameStyle):
        """
        Draw a round frame
        
        :param QPainter painter: Painter
        :param QRectF rect: Target rectangle
        :param QPalette palette: `QPalette.WindowText` is used for plain borders, `QPalette.Dark` and `QPalette.Light` for raised or sunken borders
        :param int lineWidth: Line width
        :param int frameStyle: bitwise OR´ed value of `QFrame.Shape` and `QFrame.Shadow`
        """
        Plain, Sunken, Raised = list(range(3))
        style = Plain
        if (frameStyle & QFrame.Sunken) == QFrame.Sunken:
            style = Sunken
        elif (frameStyle & QFrame.Raised) == QFrame.Raised:
            style = Raised
        lw2 = .5*lineWidth
        r = rect.adjusted(lw2, lw2, -lw2, -lw2)
        if style != Plain:
            c1 = palette.color(QPalette.Light)
            c2 = palette.color(QPalette.Dark)
            if style == Sunken:
                c1, c2 = c2, c1
            gradient = QLinearGradient(r.topLeft(), r.bottomRight())
            gradient.setColorAt(0., c1)
            gradient.setColorAt(1., c2)
            brush = QBrush(gradient)
        else:
            brush = palette.brush(QPalette.WindowText)
        painter.save()
        painter.setPen(QPen(brush, lineWidth))
        painter.drawEllipse(r)
        painter.restore()
    
    def drawFrame(self, painter, rect, palette, foregroundRole,
                  frameWidth, midLineWidth, frameStyle):
        """
        Draw a rectangular frame
        
        :param QPainter painter: Painter
        :param QRectF rect: Frame rectangle
        :param QPalette palette: Palette
        :param QPalette.ColorRole foregroundRole: Palette
        :param int frameWidth: Frame width
        :param int midLineWidth: Used for `QFrame.Box`
        :param int frameStyle: bitwise OR´ed value of `QFrame.Shape` and `QFrame.Shadow`
        """
        if frameWidth <= 0 or rect.isEmpty():
            return
        shadow = frameStyle & QFrame.Shadow_Mask
        painter.save()
        if shadow == QFrame.Plain:
            outerRect = rect.adjusted(0., 0., -1., -1.)
            innerRect = outerRect.adjusted(
                            frameWidth, frameWidth, -frameWidth, -frameWidth)
            path = QPainterPath()
            path.addRect(outerRect)
            path.addRect(innerRect)
            painter.setPen(Qt.NoPen)
            painter.setBrush(palette.color(foregroundRole))
            painter.drawPath(path)
        else:
            shape = frameStyle & QFrame.Shape_Mask
            if shape == QFrame.Box:
                outerRect = rect.adjusted(0., 0., -1., -1.)
                midRect1 = outerRect.adjusted(
                    frameWidth, frameWidth, -frameWidth, -frameWidth)
                midRect2 = midRect1.adjusted(
                    midLineWidth, midLineWidth, -midLineWidth, -midLineWidth)
                innerRect = midRect2.adjusted(
                    frameWidth, frameWidth, -frameWidth, -frameWidth)
                path1 = QPainterPath()
                path1.moveTo(outerRect.bottomLeft())
                path1.lineTo(outerRect.topLeft())
                path1.lineTo(outerRect.topRight())
                path1.lineTo(midRect1.topRight())
                path1.lineTo(midRect1.topLeft())
                path1.lineTo(midRect1.bottomLeft())
                path2 = QPainterPath()
                path2.moveTo(outerRect.bottomLeft())
                path2.lineTo(outerRect.bottomRight())
                path2.lineTo(outerRect.topRight())
                path2.lineTo(midRect1.topRight())
                path2.lineTo(midRect1.bottomRight())
                path2.lineTo(midRect1.bottomLeft())
                path3 = QPainterPath()
                path3.moveTo(midRect2.bottomLeft())
                path3.lineTo(midRect2.topLeft())
                path3.lineTo(midRect2.topRight())
                path3.lineTo(innerRect.topRight())
                path3.lineTo(innerRect.topLeft())
                path3.lineTo(innerRect.bottomLeft())
                path4 = QPainterPath()
                path4.moveTo(midRect2.bottomLeft())
                path4.lineTo(midRect2.bottomRight())
                path4.lineTo(midRect2.topRight())
                path4.lineTo(innerRect.topRight())
                path4.lineTo(innerRect.bottomRight())
                path4.lineTo(innerRect.bottomLeft())
                path5 = QPainterPath()
                path5.addRect(midRect1)
                path5.addRect(midRect2)
                painter.setPen(Qt.NoPen)
                brush1 = palette.dark().color()
                brush2 = palette.light().color()
                if shadow == QFrame.Raised:
                    brush1, brush2 = brush2, brush1
                painter.setBrush(brush1)
                painter.drawPath(path1)
                painter.drawPath(path4)
                painter.setBrush(brush2)
                painter.drawPath(path2)
                painter.drawPath(path3)
                painter.setBrush(palette.mid())
                painter.drawPath(path5)
            else:
                outerRect = rect.adjusted(0., 0., -1., -1.)
                innerRect = outerRect.adjusted(frameWidth-1., frameWidth-1.,
                                           -(frameWidth-1.), -(frameWidth-1.))
                path1 = QPainterPath()
                path1.moveTo(outerRect.bottomLeft())
                path1.lineTo(outerRect.topLeft())
                path1.lineTo(outerRect.topRight())
                path1.lineTo(innerRect.topRight())
                path1.lineTo(innerRect.topLeft())
                path1.lineTo(innerRect.bottomLeft())
                path2 = QPainterPath()
                path2.moveTo(outerRect.bottomLeft())
                path2.lineTo(outerRect.bottomRight())
                path2.lineTo(outerRect.topRight())
                path2.lineTo(innerRect.topRight())
                path2.lineTo(innerRect.bottomRight())
                path2.lineTo(innerRect.bottomLeft())
                painter.setPen(Qt.NoPen)
                brush1 = palette.dark().color()
                brush2 = palette.light().color()
                if shadow == QFrame.Raised:
                    brush1, brush2 = brush2, brush1
                painter.setBrush(brush1)
                painter.drawPath(path1)
                painter.setBrush(brush2)
                painter.drawPath(path2)
        painter.restore()
        
    def drawRoundedFrame(self, painter, rect, xRadius, yRadius,
                         palette, lineWidth, frameStyle):
        """
        Draw a rectangular frame with rounded borders
        
        :param QPainter painter: Painter
        :param QRectF rect: Frame rectangle
        :param float xRadius: x-radius of the ellipses defining the corners
        :param float yRadius: y-radius of the ellipses defining the corners
        :param QPalette palette: `QPalette.WindowText` is used for plain borders, `QPalette.Dark` and `QPalette.Light` for raised or sunken borders
        :param int lineWidth: Line width
        :param int frameStyle: bitwise OR´ed value of `QFrame.Shape` and `QFrame.Shadow`
        """
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(Qt.NoBrush)
        lw2 = lineWidth*.5
        r = rect.adjusted(lw2, lw2, -lw2, -lw2)
        path = QPainterPath()
        path.addRoundedRect(r, xRadius, yRadius)
        Plain, Sunken, Raised = list(range(3))
        style = Plain
        if (frameStyle & QFrame.Sunken) == QFrame.Sunken:
            style = Sunken
        if (frameStyle & QFrame.Raised) == QFrame.Raised:
            style = Raised
        if style != Plain and path.elementCount() == 17:
            pathList = [QPainterPath() for _i in range(8)]
            for i in range(4):
                j = i*4+1
                pathList[2*i].moveTo(path.elementAt(j-1).x,
                                     path.elementAt(j-1).y)
                pathList[2*i].cubicTo(
                        path.elementAt(j+0).x, path.elementAt(j+0).y,
                        path.elementAt(j+1).x, path.elementAt(j+1).y,
                        path.elementAt(j+2).x, path.elementAt(j+2).y)
                pathList[2*i+1].moveTo(path.elementAt(j+2).x,
                                       path.elementAt(j+2).y)
                pathList[2*i+1].lineTo(path.elementAt(j+3).x,
                                       path.elementAt(j+3).y)
            c1 = QColor(palette.color(QPalette.Dark))
            c2 = QColor(palette.color(QPalette.Light))
            if style == Raised:
                c1, c2 = c2, c1
            for i in range(5):
                r = pathList[2*i].controlPointRect()
                arcPen = QPen()
                arcPen.setCapStyle(Qt.FlatCap)
                arcPen.setWidth(lineWidth)
                linePen = QPen()
                linePen.setCapStyle(Qt.FlatCap)
                linePen.setWidth(lineWidth)
                if i == 0:
                    arcPen.setColor(c1)
                    linePen.setColor(c1)
                elif i == 1:
                    gradient = QLinearGradient()
                    gradient.setStart(r.topLeft())
                    gradient.setFinalStop(r.bottomRight())
                    gradient.setColorAt(0., c1)
                    gradient.setColorAt(1., c2)
                    arcPen.setBrush(gradient)
                    linePen.setColor(c2)
                elif i == 2:
                    arcPen.setColor(c2)
                    linePen.setColor(c2)
                elif i == 3:
                    gradient = QLinearGradient()
                    gradient.setStart(r.bottomRight())
                    gradient.setFinalStop(r.topLeft())
                    gradient.setColorAt(0., c2)
                    gradient.setColorAt(1., c1)
                    arcPen.setBrush(gradient)
                    linePen.setColor(c1)
                painter.setPen(arcPen)
                painter.drawPath(pathList[2*i])
                painter.setPen(linePen)
                painter.drawPath(pathList[2*i+1])
        else:
            pen = QPen(palette.color(QPalette.WindowText), lineWidth)
            painter.setPen(pen)
            painter.drawPath(path)
        painter.restore()
        
    def drawColorBar(self, painter, colorMap, interval, scaleMap,
                     orientation, rect):
        """
        Draw a color bar into a rectangle
        
        :param QPainter painter: Painter
        :param qwt.color_map.QwtColorMap colorMap: Color map
        :param qwt.interval.QwtInterval interval: Value range
        :param qwt.scalemap.QwtScaleMap scaleMap: Scale map
        :param Qt.Orientation orientation: Orientation
        :param QRectF rect: Target rectangle
        """
        colorTable = []
        if colorMap.format() == QwtColorMap.Indexed:
            colorTable = colorMap.colorTable(interval)
        c = QColor()
        devRect = rect.toAlignedRect()
        pixmap = QPixmap(devRect.size())
        pixmap.fill(Qt.transparent)
        pmPainter = QPainter(pixmap)
        pmPainter.translate(-devRect.x(), -devRect.y())
        if orientation == Qt.Horizontal:
            sMap = scaleMap
            sMap.setPaintInterval(rect.left(), rect.right())
            for x in range(devRect.left(), devRect.right()+1):
                value = sMap.invTransform(x)
                if colorMap.format() == QwtColorMap.RGB:
                    c.setRgba(colorMap.rgb(interval, value))
                else:
                    c = colorTable[colorMap.colorIndex(interval, value)]
                pmPainter.setPen(c)
                pmPainter.drawLine(x, devRect.top(), devRect.bottom())
        else:
            sMap = scaleMap
            sMap.setPaintInterval(rect.bottom(), rect.top())
            for y in range(devRect.top(), devRect.bottom()+1):
                value = sMap.invTransform(y)
                if colorMap.format() == QwtColorMap.RGB:
                    c.setRgba(colorMap.rgb(interval, value))
                else:
                    c = colorTable[colorMap.colorIndex(interval, value)]
                pmPainter.setPen(c)
                pmPainter.drawLine(devRect.left(), y, devRect.right(), y)
        pmPainter.end()
        self.drawPixmap(painter, rect, pixmap)
    
    def fillPixmap(self, widget, pixmap, offset=None):
        """
        Fill a pixmap with the content of a widget

        In Qt >= 5.0 `QPixmap.fill()` is a nop, in Qt 4.x it is buggy
        for backgrounds with gradients. Thus `fillPixmap()` offers 
        an alternative implementation.
        
        :param QWidget widget: Widget
        :param QPixmap pixmap: Pixmap to be filled
        :param QPoint offset: Offset
        
        .. seealso::
        
            :py:meth:`QPixmap.fill()`
        """
        if offset is None:
            offset = QPoint()
        rect = QRect(offset, pixmap.size())
        painter = QPainter(pixmap)
        painter.translate(-offset)
        autoFillBrush = widget.palette().brush(widget.backgroundRole())
        if not (widget.autoFillBackground() and autoFillBrush.isOpaque()):
            bg = widget.palette().brush(QPalette.Window)
            qwtFillRect(widget, painter, rect, bg)
        if widget.autoFillBackground():
            qwtFillRect(widget, painter, rect, autoFillBrush)
        if widget.testAttribute(Qt.WA_StyledBackground):
            painter.setClipRegion(rect)
            opt = QStyleOption()
            opt.initFrom(widget)
            widget.style().drawPrimitive(QStyle.PE_Widget, opt,
                                         painter, widget)
    
    def drawBackground(self, painter, rect, widget):
        """
        Fill rect with the background of a widget
        
        :param QPainter painter: Painter
        :param QRectF rect: Rectangle to be filled
        :param QWidget widget: Widget
        
        .. seealso::
        
            :py:data:`QStyle.PE_Widget`, :py:meth:`QWidget.backgroundRole()`
        """
        if widget.testAttribute(Qt.WA_StyledBackground):
            opt = QStyleOption()
            opt.initFrom(widget)
            opt.rect = rect.toAlignedRect()
            widget.style().drawPrimitive(QStyle.PE_Widget, opt,
                                         painter, widget)
        else:
            brush = widget.palette().brush(widget.backgroundRole())
            painter.fillRect(rect, brush)
        
    def backingStore(self, widget, size):
        """
        :param QWidget widget: Widget, for which the backinstore is intended
        :param QSize size: Size of the pixmap
        :return: A pixmap that can be used as backing store
        """
        if QT_VERSION >= 0x050000:
            pixelRatio = 1.
            if widget and widget.windowHandle():
                pixelRatio = widget.windowHandle().devicePixelRatio()
            else:
                from qwt.qt.QtGui import qApp
                if qApp is not None:
                    try:
                        pixelRatio = qApp.devicePixelRatio()
                    except RuntimeError:
                        pass
            pm = QPixmap(size*pixelRatio)
            pm.setDevicePixelRatio(pixelRatio)
        else:
            pm = QPixmap(size)
        if QT_VERSION < 0x050000 and widget and isX11GraphicsSystem():
            if pm.x11Info().screen() != widget.x11Info().screen():
                pm.x11SetScreen(widget.x11Info().screen())
        return pm

QwtPainter = QwtPainterClass()


def qwtFillRect(widget, painter, rect, brush):
    if brush.style() == Qt.TexturePattern:
        painter.save()
        painter.setClipRect(rect)
        painter.drawTiledPixmap(rect, brush.texture(), rect.topLeft())
        painter.restore()
    elif brush.gradient():
        painter.save()
        painter.setClipRect(rect)
        painter.fillRect(0, 0, widget.width(), widget.height(), brush)
        painter.restore()
    else:
        painter.fillRect(rect, brush)
