# -*- coding: utf-8 -*-

from qwt.qwt_null_paintdevice import QwtNullPaintDevice
from qwt.qwt_painter_command import QwtPainterCommand

from qwt.qt.QtGui import (QPainter, QPainterPathStroker, QPaintEngine, QPixmap,
                          QTransform, QImage)
from qwt.qt.QtCore import Qt, QRectF, QSizeF, QSize, QPointF, QRect

from math import ceil


def qwtHasScalablePen(painter):
    pen = painter.pen()
    scalablePen = False
    if pen.style() != Qt.NoPen and pen.brush().style() != Qt.NoBrush:
        scalablePen = not pen.isCosmetic()
        if not scalablePen and pen.widthF() == 0.:
            hints = painter.renderHints()
            if hints.testFlag(QPainter.NonCosmeticDefaultPen):
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


def qwtExecCommand(painter, cmd, renderHints, transform):
    if cmd.type() == QwtPainterCommand.Path:
        doMap = False
        if bool(renderHints & QwtGraphic.RenderPensUnscaled)\
           and painter.transform().isScaling():
            isCosmetic = painter.pen().isCosmetic()
            if isCosmetic and painter.pen().widthF() == 0.:
                hints = painter.renderHints()
                if hints.testFlag(QPainter.NonCosmeticDefaultPen):
                    isCosmetic = False
            doMap = not isCosmetic
        if doMap:
            transform = painter.transform()
            painter.resetTransform()
            painter.drawPath(transform.map(cmd.path()))
            painter.setTransform(transform)
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
            self.d_scalablePen = False
        elif len(args) == 3:
            pointRect, boundingRect, scalablePen = args
            self.d_pointRect = pointRect
            self.d_boundingRect = boundingRect
            self.d_scalablePen = scalablePen
        else:
            raise TypeError("%s() takes 0 or 3 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def scaledBoundingRect(self, sx, sy, scalePens):
        if sx == 1. and sy == 1.:
            return self.d_boundingRect
        transform = QTransform()
        transform.scale(sx, sy)
        if scalePens and self.d_scalablePen:
            rect = transform.mapRect(self.d_boundingRect)
        else:
            rect = transform.mapRect(self.d_pointRect)
            l = abs(self.d_pointRect.left()-self.d_boundingRect.left())
            r = abs(self.d_pointRect.right()-self.d_boundingRect.right())
            t = abs(self.d_pointRect.top()-self.d_boundingRect.top())
            b = abs(self.d_pointRect.bottom()-self.d_boundingRect.bottom())
            rect.adjust(-l, -t, r, b)
        return rect
    
    def scaleFactorX(self, pathRect, targetRect, scalePens):
        if pathRect.width() <= 0.0:
            return 0.
        p0 = self.d_pointRect.center()
        l = abs(pathRect.left()-p0.x())
        r = abs(pathRect.right()-p0.x())
        w = 2.*min([l, r])*targetRect.width()/pathRect.width()
        if scalePens and self.d_scalablePen:
            sx = w/self.d_boundingRect.width()
        else:
            pw = max([abs(self.d_boundingRect.left()-self.d_pointRect.left()),
                      abs(self.d_boundingRect.right()-self.d_pointRect.right())])
            sx = (w-2*pw)/self.d_pointRect.width()
        return sx
    
    def scaleFactorY(self, pathRect, targetRect, scalePens):
        if pathRect.height() <= 0.0:
            return 0.
        p0 = self.d_pointRect.center()
        t = abs(pathRect.top()-p0.y())
        b = abs(pathRect.bottom()-p0.y())
        h = 2.*min([t, b])*targetRect.height()/pathRect.height()
        if scalePens and self.d_scalablePen:
            sy = h/self.d_boundingRect.height()
        else:
            pw = max([abs(self.d_boundingRect.top()-self.d_pointRect.top()),
                      abs(self.d_boundingRect.bottom()-self.d_pointRect.bottom())])
            sy = (h-2*pw)/self.d_pointRect.height()
        return sy
    

class QwtGraphic_PrivateData(object):
    def __init__(self):
        self.boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.pointRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.defaultSize = QSizeF()
        self.commands = []
        self.pathInfos = []
        self.renderHints = None


class QwtGraphic(QwtNullPaintDevice):
    
    # enum RenderHint
    RenderPensUnscaled = 0x1
    
    def __init__(self, *args):
        QwtNullPaintDevice.__init__(self)
        if len(args) == 0:
            self.setMode(QwtNullPaintDevice.PathMode)
            self.d_data = QwtGraphic_PrivateData()
        elif len(args) == 1:
            other, = args
            self.setMode(other.mode())
            self.d_data = other.d_data
        else:
            raise TypeError("%s() takes 0 or 1 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def reset(self):
        self.d_data.commands = []
        self.d_data.pathInfos = []
        self.d_data.boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.d_data.pointRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.d_data.defaultSize = QSizeF()
    
    def isNull(self):
        return len(self.d_data.commands) == 0
    
    def isEmpty(self):
        return self.d_data.boundingRect.isEmpty()
    
    def setRenderHints(self, hint, on):
        if on:
            self.d_data.renderHints |= hint
        else:
            self.d_data.renderHints &= ~hint
    
    def testRenderHint(self, hint):
        return bool(self.d_data.renderHints & hint)
    
    def boundingRect(self):
        if self.d_data.boundingRect.width() < 0:
            return QRectF()
        return self.d_data.boundingRect
    
    def controlPointRect(self):
        if self.d_data.pointRect.width() < 0:
            return QRectF()
        return self.d_data.pointRect
    
    def scaledBoundingRect(self, sx, sy):
        if sx == 1. and sy == 1.:
            return self.d_data.boundingRect
        transform = QTransform()
        transform.scale(sx, sy)
        rect = transform.mapRect(self.d_data.pointRect)
        for pathInfo in self.d_data.pathInfos:
            rect |= pathInfo.scaledBoundingRect(sx, sy,
                not bool(self.d_data.renderHints & self.RenderPensUnscaled))
        return rect
    
    def sizeMetrics(self):
        sz = self.defaultSize()
        return QSize(ceil(sz.width()), ceil(sz.height()))
        
    def setDefaultSize(self, size):
        w = max([0., size.width()])
        h = max([0., size.height()])
        self.d_data.defaultSize = QSizeF(w, h)
        
    def defaultSize(self):
        if not self.d_data.defaultSize.isEmpty():
            return self.d_data.defaultSize
        return self.boundingRect().size()
    
    def render(self, *args):
        if len(args) == 1:
            painter, = args
            if self.isNull():
                return
            transform = painter.transform()
            painter.save()
            for command in self.d_data.commands:
                qwtExecCommand(painter, command, self.d_data.renderHints, transform)
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
            if self.d_data.pointRect.width() > 0.:
                sx = rect.width()/self.d_data.pointRect.width()
            if self.d_data.pointRect.height() > 0.:
                sy = rect.height()/self.d_data.pointRect.height()
            scalePens = not bool(self.d_data.renderHints & self.RenderPensUnscaled)
            for info in self.d_data.pathInfos:
                ssx = info.scaleFactorX(self.d_data.pointRect, rect, scalePens)
                if ssx > 0.:
                    sx = min([sx, ssx])
                ssy = info.scaleFactorY(self.d_data.pointRect, rect, scalePens)
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
            tr.translate(rect.center().x()-.5*sx*self.d_data.pointRect.width(),
                         rect.center().y()-.5*sy*self.d_data.pointRect.height())
            tr.scale(sx, sy)
            tr.translate(-self.d_data.pointRect.x(),
                         -self.d_data.pointRect.y())
            transform = painter.transform()
            painter.setTransform(tr, True)
            self.render(painter)
            painter.setTransform(transform)
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
            w = ceil(sz.width())
            h = ceil(sz.height())
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
            w = ceil(sz.width())
            h = ceil(sz.height())
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
        self.d_data.commands += [QwtPainterCommand(path)]
        if not path.isEmpty():
            scaledPath = painter.transform().map(path)
            pointRect = scaledPath.boundingRect()
            boundingRect = pointRect
            if painter.pen().style() != Qt.NoPen\
               and painter.pen().brush().style() != Qt.NoBrush:
                boundingRect = qwtStrokedPathRect(painter, path)
            self.updateControlPointRect(pointRect)
            self.updateBoundingRect(boundingRect)
            self.d_data.pathInfos += [PathInfo(pointRect, boundingRect,
                                               qwtHasScalablePen(painter))]
    
    def drawPixmap(self, rect, pixmap, subRect):
        painter = self.paintEngine().painter()
        if painter is None:
            return
        self.d_data.commands += [QwtPainterCommand(rect, pixmap, subRect)]
        r = painter.transform().mapRect(rect)
        self.updateControlPointRect(r)
        self.updateBoundingRect(r)
    
    def drawImage(self, rect, image, subRect, flags):
        painter = self.paintEngine().painter()
        if painter is None:
            return
        self.d_data.commands += [QwtPainterCommand(rect, image, subRect, flags)]
        r = painter.transform().mapRect(rect)
        self.updateControlPointRect(r)
        self.updateBoundingRect(r)
        
    def updateState(self, state):
        #XXX: shall we call the parent's implementation of updateState?
        self.d_data.commands += QwtPainterCommand(state)
        
    def updateBoundingRect(self, rect):
        br = rect
        painter = self.paintEngine().painter()
        if painter and painter.hasClipping():
            #XXX: there's something fishy about the following lines...
            cr = painter.clipRegion().boundingRect()
            cr = painter.transform().mapRect(br)
            br &= cr
        if self.d_data.boundingRect.width() < 0:
            self.d_data.boundingRect = br
        else:
            self.d_data.boundingRect |= br
            
    def updateControlPointRect(self, rect):
        if self.d_data.pointRect.width() < 0.:
            self.d_data.pointRect = rect
        else:
            self.d_data.pointRect |= rect
    
    def commands(self):
        return self.d_data.commands
    
    def setCommands(self, commands):
        self.reset()
        painter = QPainter(self)
        for cmd in commands:
            qwtExecCommand(painter, cmd, 0, QTransform())
        painter.end()
