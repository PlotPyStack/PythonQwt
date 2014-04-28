# -*- coding: utf-8 -*-

from qwt.qwt_null_paintdevice import QwtNullPaintDevice
from qwt.qwt_painter import QwtPainter

from qwt.qt.QtGui import (QFrame, QPaintEngine, QPen, QBrush, QRegion, QImage,
                          QPainterPath, QPixmap, QGradient, QPainter, qAlpha,
                          QPolygonF, QStyleOption, QStyle, QStyleOptionFrame)
from qwt.qt.QtCore import Qt, QSizeF, QT_VERSION, QEvent, QPointF, QRectF


class Border(object):
    def __init__(self):
        self.pathlist = []
        self.rectList = []
        self.clipRegion = QRegion()


class Background(object):
    def __init__(self):
        self.path = QPainterPath()
        self.brush = QBrush()
        self.origin = QPointF()


class QwtStyleSheetRecorder(QwtNullPaintDevice):
    def __init__(self, size):
        super(QwtStyleSheetRecorder, self).__init__()
        self.d_size = size
        self.d_pen = QPen()
        self.d_brush = QBrush()
        self.d_origin = QPointF()
        self.clipRects = []
        self.border = Border()
        self.background = Background()
        
    def updateState(self, state):
        if state.state() & QPaintEngine.DirtyPen:
            self.d_pen = state.pen()
        if state.state() & QPaintEngine.DirtyBrush:
            self.d_brush = state.brush()
        if state.state() & QPaintEngine.DirtyBrushOrigin:
            self.d_origin = state.brushOrigin()
    
    def drawRects(self, rects, count):
        for i in range(count):
            self.border.rectList += rects[i]
    
    def drawPath(self, path):
        rect = QRectF(QPointF(0., 0.), self.d_size)
        if path.controlPointRect().contains(rect.center()):
            self.setCornerRects(path)
            self.alignCornerRects(rect)
            self.background.path = path
            self.background.brush = self.d_brush
            self.background.origin = self.d_origin
        else:
            self.border.pathlist += [path]
    
    def setCornerRects(self, path):
        pos = QPointF(0., 0.)
        for i in range(path.elementCount()):
            el = path.elementAt(i)
            if el.type in (QPainterPath.MoveToElement,
                           QPainterPath.LineToElement):
                pos.setX(el.x)
                pos.setY(el.y)
            elif el.type == QPainterPath.CurveToElement:
                r = QRectF(pos, QPointF(el.x, el.y))
                self.clipRects += [r.normalized()]
                pos.setX(el.x)
                pos.setY(el.y)
            elif el.type == QPainterPath.CurveToDataElement:
                if self.clipRects:
                    r = self.clipRects[-1]
                    r.setCoords(min([r.left(), el.x]),
                                min([r.top(), el.y]),
                                max([r.right(), el.x]),
                                max([r.bottom(), el.y]))
                    self.clipRects[-1] = r.normalized()
    
    def sizeMetrics(self):
        return self.d_size
    
    def alignCornerRects(self, rect):
        for r in self.clipRects:
            if r.center().x() < rect.center().x():
                r.setLeft(rect.left())
            else:
                r.setRight(rect.right())
            if r.center().y() < rect.center().y():
                r.setTop(rect.top())
            else:
                r.setBottom(rect.bottom())


def qwtDrawBackground(painter, canvas):
    painter.save()
    borderClip = canvas.borderPath(canvas.rect())
    if not borderClip.isEmpty():
        painter.setClipPath(borderClip, Qt.IntersectClip)
    brush = canvas.palette().brush(canvas.backgroundRole())
    if brush.style() == Qt.TexturePattern:
        pm = QPixmap(canvas.size())
        QwtPainter().fillPixmap(canvas, pm)
        painter.drawPixmap(0, 0, pm)
    elif brush.gradient():
        rects = []
        if brush.gradient().coordinateMode() == QGradient.ObjectBoundingMode:
            rects += [canvas.rect()]
        else:
            rects += [painter.clipRegion().rects()]
        useRaster = False
        if painter.paintEngine().type() == QPaintEngine.X11:
            useRaster = True
        if useRaster:
            format_ = QImage.Format_RGB32
            stops = brush.gradient().stops()
            for stop in stops:
                if stop.second.alpha() != 255:
                    format_ = QImage.Format_ARGB32
                    break
            image = QImage(canvas.size(), format_)
            p = QPainter(image)
            p.setPen(Qt.NoPen)
            p.setBrush(brush)
            p.drawRects(rects)
            p.end()
            painter.drawImage(0, 0, image)
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(brush)
            painter.drawRects(rects)
    else:
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawRects(painter.clipRegion().rects())
    painter.restore()


def qwtRevertPath(path):
    if path.elementCount() == 4:
        el0 = path.elementAt(0)
        el3 = path.elementAt(3)
        path.setElementPositionAt(0, el3.x, el3.y)
        path.setElementPositionAt(3, el0.x, el0.y)


def qwtCombinePathList(rect, pathList):
    if not pathList:
        return QPainterPath()
    
    ordered = [None] * 8
    for subPath in pathList:
        index = -1
        br = subPath.controlPointRect()
        if br.center().x() < rect.center().x():
            if br.center().y() < rect.center().y():
                if abs(br.top()-rect.top()) < abs(br.left()-rect.left()):
                    index = 1
                else:
                    index = 0
            else:
                if abs(br.bottom()-rect.bottom) < abs(br.left()-rect.left()):
                    index = 6
                else:
                    index = 7
            if subPath.currentPosition().y() > br.center().y():
                qwtRevertPath(subPath)
        else:
            if br.center().y() < rect.center().y():
                if abs(br.top()-rect.top()) < abs(br.right()-rect.right()):
                    index = 2
                else:
                    index = 3
            else:
                if abs(br.bottom()-rect.bottom()) < abs(br.right()-rect.right()):
                    index = 5
                else:
                    index = 4
            if subPath.currentPosition().y() < br.center().y():
                qwtRevertPath(subPath)
        ordered[index] = subPath
    for i in range(4):
        if ordered[2*i].isEmpty() != ordered[2*i+1].isEmpty():
            return QPainterPath()
    corners = QPolygonF(rect)
    path = QPainterPath()
    for i in range(4):
        if ordered[2*i].isEmpty():
            path.lineTo(corners[i])
        else:
            path.connectPath(ordered[2*i])
            path.connectPath(ordered[2*i+1])
    path.closeSubpath()
    return path


def qwtDrawStyledBackground(w, painter):
    opt = QStyleOption()
    opt.initFrom(w)
    w.style().drawPrimitive(QStyle.PE_Widget, opt, painter, w)


def qwtBackgroundWidget(w):
    if w.parentWidget() is None:
        return w
    if w.autoFillBackground():
        brush = w.palette().brush(w.backgroundRole())
        if brush.color().alpha() > 0:
            return w
    if w.testAttribute(Qt.WA_StyledBackground):
        image = QImage(1, 1, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.translate(-w.rect().center())
        qwtDrawStyledBackground(w, painter)
        painter.end()
        if qAlpha(image.pixel(0, 0)) != 0:
            return w
    return qwtBackgroundWidget(w.parentWidget())


def qwtFillBackground(*args):
    if len(args) == 2:
        painter, canvas = args

        rects = []
        if canvas.testAttribute(Qt.WA_StyledBackground):
            recorder = QwtStyleSheetRecorder(canvas.size())
            p = QPainter(recorder)
            qwtDrawStyledBackground(canvas, p)
            p.end()
            if recorder.background.brush.isOpaque():
                rects = recorder.clipRects
            else:
                rects += [canvas.rect()]
        else:
            r = canvas.rect()
            radius = canvas.borderRadius()
            if radius > 0.:
                sz = QSizeF(radius, radius)
                rects += [QRectF(r.topLeft(), sz),
                          QRectF(r.topRight()-QPointF(radius, 0), sz),
                          QRectF(r.bottomRight()-QPointF(radius, radius), sz),
                          QRectF(r.bottomLeft()-QPointF(0, radius), sz)]

        qwtFillBackground(painter, canvas, rects)

    elif len(args) == 3:
        painter, widget, fillRects = args
        
        if not fillRects:
            return
        if painter.hasClipping():
            clipRegion = painter.transform().map(painter.clipRegion())
        else:
            clipRegion = widget.contentsRect()
        bgWidget = qwtBackgroundWidget(widget.parentWidget())
        for fillRect in fillRects:
            rect = fillRect.toAlignedRect()
            if clipRegion.intersects(rect):
                pm = QPixmap(rect.size())
                QwtPainter().fillPixmap(bgWidget, pm, widget.mapTo(bgWidget, rect.topLeft()))
                painter.drawPixmap(rect, pm)
        
    else:
        raise TypeError("%s() takes 2 or 3 argument(s) (%s given)"\
                        % ("qwtFillBackground", len(args)))


class StyleSheetBackground(object):
    def __init__(self):
        self.brush = QBrush()
        self.origin = QPointF()

class StyleSheet(object):
    def __init__(self):
        self.hasBorder = False
        self.borderPath = QPainterPath()
        self.cornerRects = []
        self.background = StyleSheetBackground()
        
class QwtPlotCanvas_PrivateData(object):
    def __init__(self):
        self.focusIndicator = QwtPlotCanvas.NoFocusIndicator
        self.borderRadius = 0
        self.paintAttributes = 0
        self.backingStore = None
        self.styleSheet = StyleSheet()
        self.styleSheet.hasBorder = False


class QwtPlotCanvas(QFrame):
    
    # enum PaintAttribute
    BackingStore = 1
    Opaque = 2
    HackStyledBackground = 4
    ImmediatePaint = 8
    
    # enum FocusIndicator
    NoFocusIndicator, CanvasFocusIndicator, ItemFocusIndicator = range(3)
    
    def __init__(self, plot=None):
        super(QwtPlotCanvas, self).__init__(plot)
        self.setFrameStyle(QFrame.Panel|QFrame.Sunken)
        self.setLineWidth(2)
        self.d_data = QwtPlotCanvas_PrivateData()
        self.setCursor(Qt.CrossCursor)
        self.setAutoFillBackground(True)
        self.setPaintAttribute(QwtPlotCanvas.BackingStore, True)
        self.setPaintAttribute(QwtPlotCanvas.Opaque, True)
        self.setPaintAttribute(QwtPlotCanvas.HackStyledBackground, True)
    
    def plot(self):
        return self.parent()
    
    def setPaintAttribute(self, attribute, on=True):
        if bool(self.d_data.paintAttributes & attribute) == on:
            return
        if on:
            self.d_data.paintAttributes |= attribute
        else:
            self.d_data.paintAttributes &= not attribute
        if attribute == self.BackingStore:
            if on:
                if self.d_data.backingStore is None:
                    self.d_data.backingStore = QPixmap()
                if self.isVisible():
                    if QT_VERSION >= 0x050000:
                        self.d_data.backingStore = self.grab(self.rect())
                    else:
                        self.d_data.backingStore = QPixmap.grabWidget(self,
                                                                self.rect())
            else:
                self.d_data.backingStore = None
        elif attribute == self.Opaque:
            if on:
                self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        elif attribute in (self.HackStyledBackground, self.ImmediatePaint):
            pass
        
    def testPaintAttribute(self, attribute):
        return self.d_data.paintAttributes & attribute
        
    def backingStore(self):
        return self.d_data.backingStore
    
    def invalidateBackingStore(self):
        if self.d_data.backingStore:
            self.d_data.backingStore = QPixmap()
    
    def setFocusIndicator(self, focusIndicator):
        self.d_data.focusIndicator = focusIndicator
    
    def focusIndicator(self):
        return self.d_data.focusIndicator
    
    def setBorderRadius(self, radius):
        self.d_data.borderRadius = max([0., radius])
        
    def borderRadius(self):
        return self.d_data.borderRadius
        
    def event(self, event):
        if event.type() == QEvent.PolishRequest:
            if self.testPaintAttribute(self.Opaque):
                self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        if event.type() in (QEvent.PolishRequest, QEvent.StyleChange):
            self.updateStyleSheetInfo()
        return QFrame.event(self, event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setClipRegion(event.region())
        if self.testPaintAttribute(self.BackingStore) and\
           self.d_data.backingStore is not None:
            bs = self.d_data.backingStore
            if bs.size() != self.size():
                bs = QwtPainter().backingStore(self, self.size())
                if self.testAttribute(Qt.WA_StyledBackground):
                    p = QPainter(bs)
                    qwtFillBackground(p, self)
                    self.drawCanvas(p, True)
                else:
                    p = QPainter()
                    if self.d_data.borderRadius <= 0.:
#                        print('**DEBUG: QwtPlotCanvas.paintEvent')
                        QwtPainter().fillPixmap(self, bs)
                        p.begin(bs)
                        self.drawCanvas(p, False)
                    else:
                        p.begin(bs)
                        qwtFillBackground(p, self)
                        self.drawCanvas(p, True)
                    if self.frameWidth() > 0:
                        self.drawBorder(p)
                    p.end()
            painter.drawPixmap(0, 0, self.d_data.backingStore)
        else:
            if self.testAttribute(Qt.WA_StyledBackground):
                if self.testAttribute(Qt.WA_OpaquePaintEvent):
                    qwtFillBackground(painter, self)
                    self.drawCanvas(painter, True)
                else:
                    self.drawCanvas(painter, False)
            else:
                if self.testAttribute(Qt.WA_OpaquePaintEvent):
                    if self.autoFillBackground():
                        qwtFillBackground(painter, self)
                        qwtDrawBackground(painter, self)
                else:
                    if self.borderRadius() > 0.:
                        clipPath = QPainterPath()
                        clipPath.addRect(self.rect())
                        clipPath = clipPath.subtracted(self.borderPath(self.rect()))
                        painter.save()
                        painter.setClipPath(clipPath, Qt.IntersectClip)
                        qwtFillBackground(painter, self)
                        qwtDrawBackground(painter, self)
                        painter.restore()
                self.drawCanvas(painter, False)
                if self.frameWidth() > 0:
                    self.drawBorder(painter)
        if self.hasFocus() and self.focusIndicator() == self.CanvasFocusIndicator:
            self.drawFocusIndicator(painter)
    
    def drawCanvas(self, painter, withBackground):
        hackStyledBackground = False
        if withBackground and self.testAttribute(Qt.WA_StyledBackground) and\
           self.testPaintAttribute(self.HackStyledBackground):
            if self.d_data.styleSheet.hasBorder and\
               not self.d_data.styleSheet.borderPath.isEmpty():
                hackStyledBackground = True
        if withBackground:
            painter.save()
            if self.testAttribute(Qt.WA_StyledBackground):
                if hackStyledBackground:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(self.d_data.styleSheet.background.brush)
                    painter.setBrushOrigin(self.d_data.styleSheet.background.origin)
                    painter.setClipPath(self.d_data.styleSheet.borderPath)
                    painter.drawRect(self.contentsRect())
                else:
                    qwtDrawStyledBackground(self, painter)
            elif self.autoFillBackground():
                painter.setPen(Qt.NoPen)
                painter.setBrush(self.palette().brush(self.backgroundRole()))
                if self.d_data.borderRadius > 0. and self.rect() == self.frameRect():
                    if self.frameWidth() > 0:
                        painter.setClipPath(self.borderPath(self.rect()))
                        painter.drawRect(self.rect())
                    else:
                        painter.setRenderHint(QPainter.Antialiasing, True)
                        painter.drawPath(self.borderPath(self.rect()))
                else:
                    painter.drawRect(self.rect())
            painter.restore()
        painter.save()
        if not self.d_data.styleSheet.borderPath.isEmpty():
            painter.setClipPath(self.d_data.styleSheet.borderPath,
                                Qt.IntersectClip)
        else:
            if self.d_data.borderRadius > 0.:
                painter.setClipPath(self.borderPath(self.frameRect()),
                                    Qt.IntersectClip)
            else:
#                print('**DEBUG: QwtPlotCanvas.drawCanvas')
                painter.setClipRect(self.contentsRect(), Qt.IntersectClip)
        self.plot().drawCanvas(painter)
        painter.restore()
        if withBackground and hackStyledBackground:
            opt = QStyleOptionFrame()
            opt.initFrom(self)
            self.style().drawPrimitive(QStyle.PE_Frame, opt, painter, self)
    
    def drawBorder(self, painter):
        if self.d_data.borderRadius > 0:
            if self.frameWidth() > 0:
                QwtPainter().drawRoundedFrame(painter, QRectF(self.frameRect()),
                        self.d_data.borderRadius, self.d_data.borderRadius,
                        self.palette(), self.frameWidth(), self.frameStyle())
        else:
            if QT_VERSION >= 0x040500:
                from qwt.qt.QtGui import QStyleOptionFrameV3
                opt = QStyleOptionFrameV3()
                opt.init(self)
                frameShape = self.frameStyle() & QFrame.Shape_Mask
                frameShadow = self.frameStyle() & QFrame.Shadow_Mask
                opt.frameShape = QFrame.Shape(int(opt.frameShape)|frameShape)
                if frameShape in (QFrame.Box, QFrame.HLine, QFrame.VLine,
                                  QFrame.StyledPanel, QFrame.Panel):
                    opt.lineWidth = self.lineWidth()
                    opt.midLineWidth = self.midLineWidth()
                else:
                    opt.lineWidth = self.frameWidth()
                if frameShadow == self.Sunken:
                    opt.state |= QStyle.State_Sunken
                elif frameShadow == self.Raised:
                    opt.state |= QStyle.State_Raised
                self.style().drawControl(QStyle.CE_ShapedFrame, opt, painter, self)
            else:
                self.drawFrame(painter)
    
    def resizeEvent(self, event):
        QFrame.resizeEvent(self, event)
        self.updateStyleSheetInfo()
    
    def drawFocusIndicator(self, painter):
        margin = 1
        focusRect = self.contentsRect()
        focusRect.setRect(focusRect.x()+margin, focusRect.y()+margin,
                          focusRect.width()-2*margin, focusRect.height()-2*margin)
        QwtPainter().drawFocusRect(painter, self, focusRect)
    
    def replot(self):
        self.invalidateBackingStore()
        if self.testPaintAttribute(self.ImmediatePaint):
            self.repaint(self.contentsRect())
        else:
            self.update(self.contentsRect())
    
    def updateStyleSheetInfo(self):
        if not self.testAttribute(Qt.WA_StyledBackground):
            return
        recorder = QwtStyleSheetRecorder(self.size())
        painter = QPainter(recorder)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        painter.end()
        self.d_data.styleSheet.hasBorder = not recorder.border.rectList.isEmpty()
        self.d_data.styleSheet.cornerRects = recorder.clipRects
        if recorder.background.path.isEmpty():
            if not recorder.border.rectList.isEmpty():
                self.d_data.styleSheet.borderPath =\
                    qwtCombinePathList(self.rect(), recorder.border.pathlist)
        else:
            self.d_data.styleSheet.borderPath = recorder.background.path
            self.d_data.styleSheet.background.brush = recorder.background.brush
            self.d_data.styleSheet.background.origin = recorder.background.origin
    
    def borderPath(self, rect):
        if self.testAttribute(Qt.WA_StyledBackground):
            recorder = QwtStyleSheetRecorder(rect.size())
            painter = QPainter(recorder)
            opt = QStyleOption()
            opt.initFrom(self)
            opt.rect = rect
            self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
            painter.end()
            if not recorder.background.path.isEmpty():
                return recorder.background.path
            if not recorder.border.rectList.isEmpty():
                return qwtCombinePathList(rect, recorder.border.pathlist)
        elif self.d_data.borderRadius > 0.:
            fw2 = self.frameWidth()*.5
            r = QRectF(rect).adjusted(fw2, fw2, -fw2, -fw2)
            path = QPainterPath()
            path.addRoundedRect(r, self.d_data.borderRadius,
                                self.d_data.borderRadius)
            return path
        return QPainterPath()
