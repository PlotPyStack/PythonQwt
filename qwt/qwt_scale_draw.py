# -*- coding: utf-8 -*-

from qwt.qwt_scale_div import QwtScaleDiv
from qwt.qwt_scale_map import QwtScaleMap
from qwt.qwt_text import QwtText
from qwt.qwt_math import qwtRadians
from qwt.qwt_painter import QwtPainter

from qwt.qt.QtGui import QPalette, QFontMetrics, QTransform
from qwt.qt.QtCore import (Qt, qFuzzyCompare, QLocale, QRectF, QPointF, QRect,
                           QPoint)

from math import ceil, sin, pi, cos


class QwtAbstractScaleDraw_PrivateData(object):
    def __init__(self):
        self.spacing = 4
        self.penWidth = 0
        self.minExtent = 0.
        
        self.components = QwtAbstractScaleDraw.Backbone|\
                          QwtAbstractScaleDraw.Ticks|\
                          QwtAbstractScaleDraw.Labels
        self.tickLength = [None] * 3
        self.tickLength[QwtScaleDiv.MinorTick] = 4.0
        self.tickLength[QwtScaleDiv.MediumTick] = 6.0
        self.tickLength[QwtScaleDiv.MajorTick] = 8.0
        
        self.map = QwtScaleMap()
        self.scaleDiv = QwtScaleDiv()
        
        self.labelCache = {}
        

class QwtAbstractScaleDraw(object):
    # enum ScaleComponent
    Backbone = 0x01
    Ticks = 0x02
    Labels = 0x04
    def __init__(self):
        self.d_data = QwtAbstractScaleDraw_PrivateData()
    
    def enableComponent(self, component, enable):
        if enable:
            self.d_data.components |= component
        else:
            self.d_data.components &= ~component
    
    def hasComponent(self, component):
        return self.d_data.components & component
    
    def setScaleDiv(self, scaleDiv):
        self.d_data.scaleDiv = scaleDiv
        self.d_data.map.setScaleInterval(scaleDiv.lowerBound(),
                                         scaleDiv.upperBound())
        self.d_data.labelCache.clear()
    
    def setTransformation(self, transformation):
        self.d_data.map.setTransformation(transformation)
    
    def scaleMap(self):
        return self.d_data.map
    
    def scaleDiv(self):
        return self.d_data.scaleDiv
    
    def setPenWidth(self, width):
        if width < 0:
            width = 0
        if width != self.d_data.penWidth:
            self.d_data.penWidth = width

    def penWidth(self):
        return self.d_data.penWidth
    
    def draw(self, painter, palette):
        painter.save()
        
        pen = painter.pen()
        pen.setWidth(self.d_data.penWidth)
        pen.setCosmetic(False)
        painter.setPen(pen)
        
        if self.hasComponent(QwtAbstractScaleDraw.Labels):
            painter.save()
            painter.setPen(palette.color(QPalette.Text))
            majorTicks = self.d_data.scaleDiv.ticks(QwtScaleDiv.MajorTick)
            for v in majorTicks:
                if self.d_data.scaleDiv.contains(v):
                    self.drawLabel(painter, v)
            painter.restore()
        
        if self.hasComponent(QwtAbstractScaleDraw.Ticks):
            painter.save()
            pen = painter.pen()
            pen.setColor(palette.color(QPalette.WindowText))
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)
            for tickType in range(QwtScaleDiv.NTickTypes):
                ticks = self.d_data.scaleDiv.ticks(tickType)
                for v in ticks:
                    if self.d_data.scaleDiv.contains(v):
                        self.drawTick(painter, v,
                                      self.d_data.tickLength[tickType])
            painter.restore()
        
        if self.hasComponent(QwtAbstractScaleDraw.Backbone):
            painter.save()
            pen = painter.pen()
            pen.setColor(palette.color(QPalette.WindowText))
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)
            self.drawBackbone(painter)
            painter.restore()
        
        painter.restore()
        
    def setSpacing(self, spacing):
        if spacing < 0:
            spacing = 0
        self.d_data.spacing = spacing
    
    def spacing(self):
        return self.d_data.spacing
    
    def setMinimumExtent(self, minExtent):
        if minExtent < 0.:
            minExtent = 0.
        self.d_data.minExtent = minExtent
    
    def minimumExtent(self):
        return self.d_data.minExtent
        
    def setTickLength(self, tickType, length):
        if tickType < QwtScaleDiv.MinorTick or\
           tickType > QwtScaleDiv.MajorTick:
            return
        if length < 0.:
            length = 0.
        maxTickLen = 1000.
        if length > maxTickLen:
            length = maxTickLen
        self.d_data.tickLength[tickType] = length
    
    def tickLength(self, tickType):
        if tickType < QwtScaleDiv.MinorTick or\
           tickType > QwtScaleDiv.MajorTick:
            return 0
        return self.d_data.tickLength[tickType]
    
    def maxTickLength(self):
        length = 0.
        for tickType in range(QwtScaleDiv.NTickTypes):
            length = max([length, self.d_data.tickLength[tickType]])
        return length
    
    def label(self, value):
        if qFuzzyCompare(value+1., 1.):
            value = 0.
        return QLocale().toString(value)
    
    def tickLabel(self, font, value):
        lbl = self.d_data.labelCache.get(value)
        if lbl is None:
            lbl = QwtText(self.label(value))
            lbl.setRenderFlags(0)
            lbl.setLayoutAttribute(QwtText.MinimumLayout)
            lbl.textSize(font)
            self.d_data.labelCache[value] = lbl
        return lbl
            


class QwtScaleDraw_PrivateData(QwtAbstractScaleDraw_PrivateData):
    def __init__(self):
        super(QwtScaleDraw_PrivateData, self).__init__()
        self.len = 0
        self.alignment = QwtScaleDraw.BottomScale
        self.labelAlignment = 0
        self.labelRotation = 0.
        
        self.pos = QPointF()


class QwtScaleDraw(QwtAbstractScaleDraw):
    # enum Alignment
    BottomScale, TopScale, LeftScale, RightScale = range(4)
    
    def __init__(self):
        super(QwtAbstractScaleDraw, self).__init__()
        self.d_data = QwtScaleDraw_PrivateData()
        self.setLength(100)
        
    def alignment(self):
        return self.d_data.alignment
    
    def setAlignment(self, align):
        self.d_data.alignment = align
    
    def orientation(self):
        if self.d_data.alignment in (self.TopScale, self.BottomScale):
            return Qt.Horizontal
        elif self.d_data.alignment in (self.LeftScale, self.RightScale):
            return Qt.Vertical
    
    def getBorderDistHint(self, font):
        start, end = 0, 0
        
        if not self.hasComponent(QwtAbstractScaleDraw.Labels):
            return start, end
        
        ticks = self.scaleDiv().ticks(QwtScaleDiv.MajorTick)
        if len(ticks) == 0:
            return start, end
        
        minTick = ticks[0]
        minPos = self.scaleMap().transform(minTick)
        maxTick = minTick
        maxPos = minPos
        
        for tick in ticks:
            tickPos = self.scaleMap().transform(tick)
            if tickPos < minPos:
                minTick = tick
                minPos = tickPos
            if tickPos > self.scaleMap().transform(maxTick):
                maxTick = tick
                maxPos = tickPos
        
        e = 0.
        s = 0.
        if self.orientation() == Qt.Vertical:
            s = -self.labelRect(font, minTick).top()
            s -= abs(minPos - round(self.scaleMap().p2()))
            
            e = self.labelRect(font, maxTick).bottom()
            e -= abs(maxPos - self.scaleMap().p1())
        else:
            s = -self.labelRect(font, minTick).left()
            s -= abs(minPos - self.scaleMap().p1())
            
            e = self.labelRect(font, maxTick).right()
            e -= abs(maxPos - self.scaleMap().p2())
        
        if s < 0.:
            s = 0.
        if e < 0.:
            e = 0.
        
        start = ceil(s)
        end = ceil(e)
        return start, end
    
    def minLabelDist(self, font):
        if not self.hasComponent(QwtAbstractScaleDraw.Labels):
            return 0
        
        ticks = self.scaleDiv().ticks(QwtScaleDiv.MajorTick)
        if not ticks:
            return 0
        
        fm = QFontMetrics(font)
        vertical = self.orientation() == Qt.Vertical
        
        bRect1 = QRectF()
        bRect2 = self.labelRect(font, ticks[0])
        if vertical:
            bRect2.setRect(-bRect2.bottom(), 0.,
                           bRect2.height(), bRect2.width())
        
        maxDist = 0.
        
        for tick in ticks:
            bRect1 = bRect2
            bRect2 = self.labelRect(font, tick)
            if vertical:
                bRect2.setRect(-bRect2.bottom(), 0.,
                               bRect2.height(), bRect2.width())
            
            dist = fm.leading()
            if bRect1.right() > 0:
                dist += bRect1.right()
            if bRect2.left() < 0:
                dist += -bRect2.left()
            
            if dist > maxDist:
                maxDist = dist
            
        angle = qwtRadians(self.labelRotation())
        if vertical:
            angle += pi/2
        
        sinA = sin(angle)
        if qFuzzyCompare(sinA+1., 1.):
            return ceil(maxDist)
        
        fmHeight = fm.ascent()-2
        
        labelDist = fmHeight/sin(angle)*cos(angle)
        if labelDist < 0:
            labelDist = -labelDist
        
        if labelDist > maxDist:
            labelDist = maxDist
        
        if labelDist < fmHeight:
            labelDist = fmHeight
        
        return ceil(labelDist)
        
    def extent(self, font):
        d = 0.
        if self.hasComponent(QwtAbstractScaleDraw.Labels):
            if self.orientation() == Qt.Vertical:
                d = self.maxLabelWidth(font)
            else:
                d = self.maxLabelHeight(font)
            if d > 0:
                d += self.spacing()
        if self.hasComponent(QwtAbstractScaleDraw.Ticks):
            d += self.maxTickLength()
        if self.hasComponent(QwtAbstractScaleDraw.Backbone):
            pw = max([1, self.penWidth()])
            d += pw
        d = max([d, self.minimumExtent()])
        return d
    
    def minLength(self, font):
        startDist, endDist = self.getBorderDistHint(font)
        sd = self.scaleDiv()
        minorCount = len(sd.ticks(QwtScaleDiv.MinorTick))+\
                     len(sd.ticks(QwtScaleDiv.MediumTick))
        majorCount = len(sd.ticks(QwtScaleDiv.MajorTick))
        lengthForLabels = 0
        if self.hasComponent(QwtAbstractScaleDraw.Labels):
            lengthForLabels = self.minLabelDist(font)*majorCount
        lengthForTicks = 0
        if self.hasComponent(QwtAbstractScaleDraw.Ticks):
            pw = max([1, self.penWidth()])
            lengthForTicks = ceil((majorCount+minorCount)*(pw+1.))
        return startDist + endDist + max([lengthForLabels, lengthForTicks])
    
    def labelPosition(self, value):
        tval = self.scaleMap().transform(value)
        dist = self.spacing()
        if self.hasComponent(QwtAbstractScaleDraw.Backbone):
            dist += max([1, self.penWidth()])
        if self.hasComponent(QwtAbstractScaleDraw.Ticks):
            dist += self.tickLength(QwtScaleDiv.MajorTick)
        
        px = 0
        py = 0
        if self.alignment() == self.RightScale:
            px = self.d_data.pos.x() + dist
            py = tval
        elif self.alignment() == self.LeftScale:
            px = self.d_data.pos.x() - dist
            py = tval
        elif self.alignment() == self.BottomScale:
            px = tval
            py = self.d_data.pos.y() + dist
        elif self.alignment() == self.TopScale:
            px = tval
            py = self.d_data.pos.y() - dist
        
        return QPointF(px, py)
    
    def drawTick(self, painter, value, len_):
        if len_ <= 0:
            return
        
        roundingAlignment = QwtPainter().roundingAlignment(painter)
        pos = self.d_data.pos
        tval = self.scaleMap().transform(value)
        if roundingAlignment:
            tval = round(tval)
        
        pw = self.penWidth()
        a = 0
        if pw > 1 and roundingAlignment:
            a = 1
        
        if self.alignment() == self.LeftScale:
            x1 = pos.x() + a
            x2 = pos.x() + a - pw - len_
            if roundingAlignment:
                x1 = round(x1)
                x2 = round(x2)
            QwtPainter().drawLine(painter, x1, tval, x2, tval)
        elif self.alignment() == self.RightScale:
            x1 = pos.x()
            x2 = pos.x() + pw + len_
            if roundingAlignment:
                x1 = round(x1)
                x2 = round(x2)
            QwtPainter().drawLine(painter, x1, tval, x2, tval)
        elif self.alignment() == self.BottomScale:
            y1 = pos.y()
            y2 = pos.y() + pw + len_
            if roundingAlignment:
                y1 = round(y1)
                y2 = round(y2)
            QwtPainter().drawLine(painter, tval, y1, tval, y2)
        elif self.alignment() == self.TopScale:
            y1 = pos.y() + a
            y2 = pos.y() - pw - len_ + a
            if roundingAlignment:
                y1 = round(y1)
                y2 = round(y2)
            QwtPainter().drawLine(painter, tval, y1, tval, y2)
        
    def drawBackbone(self, painter):
        doAlign = QwtPainter().roundingAlignment(painter)
        pos = self.d_data.pos
        len_ = self.d_data.len
        pw = max([self.penWidth(), 1])
        
        if doAlign:
            if self.alignment() in (self.LeftScale, self.TopScale):
                off = (pw-1)/2
            else:
                off = pw/2
        else:
            off = .5*self.penWidth()
            
        if self.alignment() == self.LeftScale:
            x = pos.x() - off
            if doAlign:
                x = round(x)
            QwtPainter().drawLine(painter, x, pos.y(), x, pos.y()+len_)
        elif self.alignment() == self.RightScale:
            x = pos.x() + off
            if doAlign:
                x = round(x)
            QwtPainter().drawLine(painter, x, pos.y(), x, pos.y()+len_)
        elif self.alignment() == self.TopScale:
            y = pos.y() - off
            if doAlign:
                y = round(y)
            QwtPainter().drawLine(painter, pos.x(), y, pos.x()+len_, y)
        elif self.alignment() == self.BottomScale:
            y = pos.y() + off
            if doAlign:
                y = round(y)
            QwtPainter().drawLine(painter, pos.x(), y, pos.x()+len_, y)
        
    def move(self, *args):
        if len(args) == 2:
            x, y = args
            self.move(QPointF(x, y))
        elif len(args) == 1:
            pos, = args
            self.d_data.pos = pos
            self.updateMap()
    
    def pos(self):
        return self.d_data.pos
    
    def setLength(self, length):
        if length >= 0 and length < 10:
            length = 10
        if length < 0 and length > -10:
            length = -10
        self.d_data.len = length
        self.updateMap()
    
    def length(self):
        return self.d_data.len
    
    def drawLabel(self, painter, value):
        lbl = self.tickLabel(painter.font(), value)
        if lbl is None or lbl.isEmpty():
            return
        pos = self.labelPosition(value)
        labelSize = lbl.textSize(painter.font())
        transform = self.labelTransformation(pos, labelSize)
        painter.save()
        painter.setWorldTransform(transform, True)
        lbl.draw(painter, QRect(QPoint(0, 0), labelSize.toSize()))
        painter.restore()
    
    def boundingLabelRect(self, font, value):
        lbl = self.tickLabel(font, value)
        if lbl.isEmpty():
            return QRect()
        pos = self.labelPosition(value)
        labelSize = lbl.textSize(font)
        transform = self.labelTransformation(pos, labelSize)
        return transform.mapRect(QRect(QPoint(0, 0), labelSize.toSize()))
    
    def labelTransformation(self, pos, size):
        transform = QTransform()
        transform.translate(pos.x(), pos.y())
        transform.rotate(self.labelRotation())
        
        flags = self.labelAlignment()
        if flags == 0:
            if self.alignment() == self.RightScale:
                if flags == 0:
                    flags = Qt.AlignRight|Qt.AlignVCenter
            elif self.alignment() == self.LeftScale:
                if flags == 0:
                    flags = Qt.AlignLeft|Qt.AlignVCenter
            elif self.alignment() == self.BottomScale:
                if flags == 0:
                    flags = Qt.AlignHCenter|Qt.AlignBottom
            elif self.alignment() == self.TopScale:
                if flags == 0:
                    flags = Qt.AlignHCenter|Qt.AlignTop
        
        if flags & Qt.AlignLeft:
            x = -size.width()
        elif flags & Qt.AlignRight:
            x = 0.
        else:
            x = -(.5*size.width())
        
        if flags & Qt.AlignTop:
            y = -size.height()
        elif flags & Qt.AlignBottom:
            y = 0
        else:
            y = -(.5*size.height())
        
        transform.translate(x, y)
        
        return transform
    
    def labelRect(self, font, value):
        lbl = self.tickLabel(font, value)
        if not lbl or lbl.isEmpty():
            return QRectF(0., 0., 0., 0.)
        pos = self.labelPosition(value)
        labelSize = lbl.textSize(font)
        transform = self.labelTransformation(pos, labelSize)
        br = transform.mapRect(QRectF(QPointF(0, 0), labelSize))
        br.translate(-pos.x(), -pos.y())
        return br
    
    def labelSize(self, font, value):
        return self.labelRect(font, value).size()
    
    def setLabelRotation(self, rotation):
        self.d_data.labelRotation = rotation
    
    def labelRotation(self):
        return self.d_data.labelRotation
    
    def setLabelAlignment(self, alignment):
        self.d_data.labelAlignment = alignment
    
    def labelAlignment(self):
        return self.d_data.labelAlignment
    
    def maxLabelWidth(self, font):
        return ceil(max([self.labelSize(font, v).width()
                         for v in self.scaleDiv().ticks(QwtScaleDiv.MajorTick)
                         if self.scaleDiv().contains(v)]))
    
    def maxLabelHeight(self, font):
        return ceil(max([self.labelSize(font, v).height()
                         for v in self.scaleDiv().ticks(QwtScaleDiv.MajorTick)
                         if self.scaleDiv().contains(v)]))
    
    def updateMap(self):
        pos = self.d_data.pos
        len_ = self.d_data.len
        sm = self.scaleMap()
        if self.orientation() == Qt.Vertical:
            sm.setPaintInterval(pos.y()+len_, pos.y())
        else:
            sm.setPaintInterval(pos.x(), pos.x()+len_)
