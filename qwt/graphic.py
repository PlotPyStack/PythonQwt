# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License, Copyright (C) 2002 Uwe Rathmann
# (see qwt/LICENSE for details)

from qwt.null_paintdevice import QwtNullPaintDevice
from qwt.painter_command import QwtPainterCommand

from qwt.qt.QtGui import (QPainter, QPainterPathStroker, QPaintEngine, QPixmap,
                          QTransform, QImage)
from qwt.qt.QtCore import Qt, QRectF, QSizeF, QSize, QPointF, QRect

import numpy as np


def qwtHasScalablePen(painter):
    pen = painter.pen()
    scalablePen = False
    if pen.style() != Qt.NoPen and pen.brush().style() != Qt.NoBrush:
        scalablePen = not pen.isCosmetic()
        if not scalablePen and pen.widthF() == 0.:
            hints = painter.renderHints()
            if hints & QPainter.NonCosmeticDefaultPen:
                scalablePen = True
    return scalablePen


def qwtStrokedPathRect(painter, path):
    stroker = QPainterPathStroker()
    stroker.setWidth(painter.pen().widthF())
    stroker.setCapStyle(painter.pen().capStyle())
    stroker.setJoinStyle(painter.pen().joinStyle())
    stroker.setMiterLimit(painter.pen().miterLimit())
    rect = QRectF()
    if qwtHasScalablePen(painter):
        stroke = stroker.createStroke(path)
        rect = painter.transform().map(stroke).boundingRect()
    else:
        mappedPath = painter.transform().map(path)
        mappedPath = stroker.createStroke(mappedPath)
        rect = mappedPath.boundingRect()
    return rect


def qwtExecCommand(painter, cmd, renderHints, transform, initialTransform):
    if cmd.type() == QwtPainterCommand.Path:
        doMap = False
        if bool(renderHints & QwtGraphic.RenderPensUnscaled)\
           and painter.transform().isScaling():
            isCosmetic = painter.pen().isCosmetic()
            if isCosmetic and painter.pen().widthF() == 0.:
                hints = painter.renderHints()
                if hints & QPainter.NonCosmeticDefaultPen:
                    isCosmetic = False
            doMap = not isCosmetic
        if doMap:
            tr = painter.transform()
            painter.resetTransform()
            path = tr.map(cmd.path())
            if initialTransform:
                painter.setTransform(initialTransform)
                invt, _ok = initialTransform.inverted()
                path = invt.map(path)
            painter.drawPath(path)
            painter.setTransform(tr)
        else:
            painter.drawPath(cmd.path())
    elif cmd.type() == QwtPainterCommand.Pixmap:
        data = cmd.pixmapData()
        painter.drawPixmap(data.rect, data.pixmap, data.subRect)
    elif cmd.type() == QwtPainterCommand.Image:
        data = cmd.imageData()
        painter.drawImage(data.rect, data.image, data.subRect, data.flags)
    elif cmd.type() == QwtPainterCommand.State:
        data = cmd.stateData()
        if data.flags & QPaintEngine.DirtyPen:
            painter.setPen(data.pen)
        if data.flags & QPaintEngine.DirtyBrush:
            painter.setBrush(data.brush)
        if data.flags & QPaintEngine.DirtyBrushOrigin:
            painter.setBrushOrigin(data.brushOrigin)
        if data.flags & QPaintEngine.DirtyFont:
            painter.setFont(data.font)
        if data.flags & QPaintEngine.DirtyBackground:
            painter.setBackgroundMode(data.backgroundMode)
            painter.setBackground(data.backgroundBrush)
        if data.flags & QPaintEngine.DirtyTransform:
            painter.setTransform(data.transform)
        if data.flags & QPaintEngine.DirtyClipEnabled:
            painter.setClipping(data.isClipEnabled)
        if data.flags & QPaintEngine.DirtyClipRegion:
            painter.setClipRegion(data.clipRegion, data.clipOperation)
        if data.flags & QPaintEngine.DirtyClipPath:
            painter.setClipPath(data.clipPath, data.clipOperation)
        if data.flags & QPaintEngine.DirtyHints:
            for hint in (QPainter.Antialiasing,
                         QPainter.TextAntialiasing,
                         QPainter.SmoothPixmapTransform,
                         QPainter.HighQualityAntialiasing,
                         QPainter.NonCosmeticDefaultPen):
                painter.setRenderHint(hint, bool(data.renderHints & hint))
        if data.flags & QPaintEngine.DirtyCompositionMode:
            painter.setCompositionMode(data.compositionMode)
        if data.flags & QPaintEngine.DirtyOpacity:
            painter.setOpacity(data.opacity)


class PathInfo(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.__scalablePen = False
        elif len(args) == 3:
            pointRect, boundingRect, scalablePen = args
            self.__pointRect = pointRect
            self.__boundingRect = boundingRect
            self.__scalablePen = scalablePen
        else:
            raise TypeError("%s() takes 0 or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def scaledBoundingRect(self, sx, sy, scalePens):
        if sx == 1. and sy == 1.:
            return self.__boundingRect
        transform = QTransform()
        transform.scale(sx, sy)
        if scalePens and self.__scalablePen:
            rect = transform.mapRect(self.__boundingRect)
        else:
            rect = transform.mapRect(self.__pointRect)
            l = abs(self.__pointRect.left()-self.__boundingRect.left())
            r = abs(self.__pointRect.right()-self.__boundingRect.right())
            t = abs(self.__pointRect.top()-self.__boundingRect.top())
            b = abs(self.__pointRect.bottom()-self.__boundingRect.bottom())
            rect.adjust(-l, -t, r, b)
        return rect
    
    def scaleFactorX(self, pathRect, targetRect, scalePens):
        if pathRect.width() <= 0.0:
            return 0.
        p0 = self.__pointRect.center()
        l = abs(pathRect.left()-p0.x())
        r = abs(pathRect.right()-p0.x())
        w = 2.*min([l, r])*targetRect.width()/pathRect.width()
        if scalePens and self.__scalablePen:
            sx = w/self.__boundingRect.width()
        else:
            pw = max([abs(self.__boundingRect.left()-self.__pointRect.left()),
                      abs(self.__boundingRect.right()-self.__pointRect.right())])
            sx = (w-2*pw)/self.__pointRect.width()
        return sx
    
    def scaleFactorY(self, pathRect, targetRect, scalePens):
        if pathRect.height() <= 0.0:
            return 0.
        p0 = self.__pointRect.center()
        t = abs(pathRect.top()-p0.y())
        b = abs(pathRect.bottom()-p0.y())
        h = 2.*min([t, b])*targetRect.height()/pathRect.height()
        if scalePens and self.__scalablePen:
            sy = h/self.__boundingRect.height()
        else:
            pw = max([abs(self.__boundingRect.top()-self.__pointRect.top()),
                      abs(self.__boundingRect.bottom()-self.__pointRect.bottom())])
            sy = (h-2*pw)/self.__pointRect.height()
        return sy
    

class QwtGraphic_PrivateData(object):
    def __init__(self):
        self.boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.pointRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.initialTransform = None
        self.defaultSize = QSizeF()
        self.commands = []
        self.pathInfos = []
        self.renderHints = 0


class QwtGraphic(QwtNullPaintDevice):
    
    # enum RenderHint
    RenderPensUnscaled = 0x1
    
    def __init__(self, *args):
        QwtNullPaintDevice.__init__(self)
        if len(args) == 0:
            self.setMode(QwtNullPaintDevice.PathMode)
            self.__data = QwtGraphic_PrivateData()
        elif len(args) == 1:
            other, = args
            self.setMode(other.mode())
            self.__data = other.__data
        else:
            raise TypeError("%s() takes 0 or 1 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def reset(self):
        self.__data.commands = []
        self.__data.pathInfos = []
        self.__data.boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.__data.pointRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.__data.defaultSize = QSizeF()
    
    def isNull(self):
        return len(self.__data.commands) == 0
    
    def isEmpty(self):
        return self.__data.boundingRect.isEmpty()
    
    def setRenderHint(self, hint, on=True):
        if on:
            self.__data.renderHints |= hint
        else:
            self.__data.renderHints &= ~hint
    
    def testRenderHint(self, hint):
        return bool(self.__data.renderHints & hint)
    
    def boundingRect(self):
        if self.__data.boundingRect.width() < 0:
            return QRectF()
        return self.__data.boundingRect
    
    def controlPointRect(self):
        if self.__data.pointRect.width() < 0:
            return QRectF()
        return self.__data.pointRect
    
    def scaledBoundingRect(self, sx, sy):
        if sx == 1. and sy == 1.:
            return self.__data.boundingRect
        transform = QTransform()
        transform.scale(sx, sy)
        rect = transform.mapRect(self.__data.pointRect)
        for pathInfo in self.__data.pathInfos:
            rect |= pathInfo.scaledBoundingRect(sx, sy,
                not bool(self.__data.renderHints & self.RenderPensUnscaled))
        return rect
    
    def sizeMetrics(self):
        sz = self.defaultSize()
        return QSize(np.ceil(sz.width()), np.ceil(sz.height()))
        
    def setDefaultSize(self, size):
        w = max([0., size.width()])
        h = max([0., size.height()])
        self.__data.defaultSize = QSizeF(w, h)
        
    def defaultSize(self):
        if not self.__data.defaultSize.isEmpty():
            return self.__data.defaultSize
        return self.boundingRect().size()
    
    def render(self, *args):
        if len(args) == 1:
            painter, = args
            if self.isNull():
                return
            transform = painter.transform()
            painter.save()
            for command in self.__data.commands:
                qwtExecCommand(painter, command, self.__data.renderHints,
                               transform, self.__data.initialTransform)
            painter.restore()
        elif len(args) in (2, 3) and isinstance(args[1], QSizeF):
            painter, size = args[:2]
            aspectRatioMode = Qt.IgnoreAspectRatio
            if len(args) == 3:
                aspectRatioMode = args[-1]
            r = QRectF(0., 0., size.width(), size.height())
            self.render(painter, r, aspectRatioMode)
        elif len(args) in (2, 3) and isinstance(args[1], QRectF):
            painter, rect = args[:2]
            aspectRatioMode = Qt.IgnoreAspectRatio
            if len(args) == 3:
                aspectRatioMode = args[-1]
            if self.isEmpty() or rect.isEmpty():
                return
            sx = 1.
            sy = 1.
            if self.__data.pointRect.width() > 0.:
                sx = rect.width()/self.__data.pointRect.width()
            if self.__data.pointRect.height() > 0.:
                sy = rect.height()/self.__data.pointRect.height()
            scalePens = not bool(self.__data.renderHints & self.RenderPensUnscaled)
            for info in self.__data.pathInfos:
                ssx = info.scaleFactorX(self.__data.pointRect, rect, scalePens)
                if ssx > 0.:
                    sx = min([sx, ssx])
                ssy = info.scaleFactorY(self.__data.pointRect, rect, scalePens)
                if ssy > 0.:
                    sy = min([sy, ssy])
            if aspectRatioMode == Qt.KeepAspectRatio:
                s = min([sx, sy])
                sx = s
                sy = s
            elif aspectRatioMode == Qt.KeepAspectRatioByExpanding:
                s = max([sx, sy])
                sx = s
                sy = s
            tr = QTransform()
            tr.translate(rect.center().x()-.5*sx*self.__data.pointRect.width(),
                         rect.center().y()-.5*sy*self.__data.pointRect.height())
            tr.scale(sx, sy)
            tr.translate(-self.__data.pointRect.x(),
                         -self.__data.pointRect.y())
            transform = painter.transform()
            if not scalePens and transform.isScaling():
                #  we don't want to scale pens according to sx/sy,
                #  but we want to apply the scaling from the 
                #  painter transformation later
                self.__data.initialTransform = QTransform()
                self.__data.initialTransform.scale(transform.m11(),
                                                   transform.m22())
            painter.setTransform(tr, True)
            self.render(painter)
            painter.setTransform(transform)
            self.__data.initialTransform = None
        elif len(args) in (2, 3) and isinstance(args[1], QPointF):
            painter, pos = args[:2]
            alignment = Qt.AlignTop|Qt.AlignLeft
            if len(args) == 3:
                alignment = args[-1]
            r = QRectF(pos, self.defaultSize())
            if alignment & Qt.AlignLeft:
                r.moveLeft(pos.x())
            elif alignment & Qt.AlignHCenter:
                r.moveCenter(QPointF(pos.x(), r.center().y()))
            elif alignment & Qt.AlignRight:
                r.moveRight(pos.x())
            if alignment & Qt.AlignTop:
                r.moveTop(pos.y())
            elif alignment & Qt.AlignVCenter:
                r.moveCenter(QPointF(r.center().x(), pos.y()))
            elif alignment & Qt.AlignBottom:
                r.moveBottom(pos.y())
            self.render(painter, r)
        else:
            raise TypeError("%s().render() takes 1, 2 or 3 argument(s) (%s "\
                            "given)" % (self.__class__.__name__, len(args)))
    
    def toPixmap(self, *args):
        if len(args) == 0:
            if self.isNull():
                return QPixmap()
            sz = self.defaultSize()
            w = np.ceil(sz.width())
            h = np.ceil(sz.height())
            pixmap = QPixmap(w, h)
            pixmap.fill(Qt.transparent)
            r = QRectF(0., 0., sz.width(), sz.height())
            painter = QPainter(pixmap)
            self.render(painter, r, Qt.KeepAspectRatio)
            painter.end()
            return pixmap
        elif len(args) in (1, 2):
            size = args[0]
            aspectRatioMode = Qt.IgnoreAspectRatio
            if len(args) == 2:
                aspectRatioMode = args[-1]
            pixmap = QPixmap(size)
            pixmap.fill(Qt.transparent)
            r = QRect(0, 0, size.width(), size.height())
            painter = QPainter(pixmap)
            self.render(painter, r, aspectRatioMode)
            painter.end()
            return pixmap
        
    def toImage(self, *args):
        if len(args) == 0:
            if self.isNull():
                return QImage()
            sz = self.defaultSize()
            w = np.ceil(sz.width())
            h = np.ceil(sz.height())
            image = QImage(w, h, QImage.Format_ARGB32)
            image.fill(0)
            r = QRect(0, 0, sz.width(), sz.height())
            painter = QPainter(image)
            self.render(painter, r, Qt.KeepAspectRatio)
            painter.end()
            return image
        elif len(args) in (1, 2):
            size = args[0]
            aspectRatioMode = Qt.IgnoreAspectRatio
            if len(args) == 2:
                aspectRatioMode = args[-1]
            image = QImage(size, QImage.Format_ARGB32_Premultiplied)
            image.fill(0)
            r = QRect(0, 0, size.width(), size.height())
            painter = QPainter(image)
            self.render(painter, r, aspectRatioMode)
            return image
        
    def drawPath(self, path):
        painter = self.paintEngine().painter()
        if painter is None:
            return
        self.__data.commands += [QwtPainterCommand(path)]
        if not path.isEmpty():
            scaledPath = painter.transform().map(path)
            pointRect = scaledPath.boundingRect()
            boundingRect = QRectF(pointRect)
            if painter.pen().style() != Qt.NoPen\
               and painter.pen().brush().style() != Qt.NoBrush:
                boundingRect = qwtStrokedPathRect(painter, path)
            self.updateControlPointRect(pointRect)
            self.updateBoundingRect(boundingRect)
            self.__data.pathInfos += [PathInfo(pointRect, boundingRect,
                                               qwtHasScalablePen(painter))]
    
    def drawPixmap(self, rect, pixmap, subRect):
        painter = self.paintEngine().painter()
        if painter is None:
            return
        self.__data.commands += [QwtPainterCommand(rect, pixmap, subRect)]
        r = painter.transform().mapRect(rect)
        self.updateControlPointRect(r)
        self.updateBoundingRect(r)
    
    def drawImage(self, rect, image, subRect, flags):
        painter = self.paintEngine().painter()
        if painter is None:
            return
        self.__data.commands += [QwtPainterCommand(rect, image, subRect, flags)]
        r = painter.transform().mapRect(rect)
        self.updateControlPointRect(r)
        self.updateBoundingRect(r)
        
    def updateState(self, state):
        #XXX: shall we call the parent's implementation of updateState?
        self.__data.commands += [QwtPainterCommand(state)]
        
    def updateBoundingRect(self, rect):
        br = QRectF(rect)
        painter = self.paintEngine().painter()
        if painter and painter.hasClipping():
            #XXX: there's something fishy about the following lines...
            cr = painter.clipRegion().boundingRect()
            cr = painter.transform().mapRect(br)
            br &= cr
        if self.__data.boundingRect.width() < 0:
            self.__data.boundingRect = br
        else:
            self.__data.boundingRect |= br
            
    def updateControlPointRect(self, rect):
        if self.__data.pointRect.width() < 0.:
            self.__data.pointRect = rect
        else:
            self.__data.pointRect |= rect
    
    def commands(self):
        return self.__data.commands
    
    def setCommands(self, commands):
        self.reset()
        painter = QPainter(self)
        for cmd in commands:
            qwtExecCommand(painter, cmd, 0, QTransform(), None)
        painter.end()
