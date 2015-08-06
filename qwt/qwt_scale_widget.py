# -*- coding: utf-8 -*-

from qwt.qwt_scale_draw import QwtScaleDraw
from qwt.qwt_scale_engine import QwtLinearScaleEngine
from qwt.qwt_color_map import QwtLinearColorMap
from qwt.qwt_text import QwtText
from qwt.qwt_painter import QwtPainter
from qwt.qwt_interval import QwtInterval
from qwt.qwt_color_map import QwtColorMap

from qwt.qt.QtGui import (QWidget, QSizePolicy, QPainter, QStyleOption, QStyle,
                          QPalette)
from qwt.qt.QtCore import Qt, QRectF, QSize, SIGNAL

from math import ceil


class ColorBar(object):
    def __init__(self):
        self.isEnabled = None
        self.width = None
        self.interval = QwtInterval()
        self.colorMap = QwtColorMap()

class QwtScaleWidget_PrivateData(object):
    def __init__(self):
        self.scaleDraw = None
        self.borderDist = [None] * 2
        self.minBorderDist = [None] * 2
        self.scaleLength = None
        self.margin = None
        self.titleOffset = None
        self.spacing = None
        self.title = QwtText()
        self.layoutFlags = None
        self.colorBar = ColorBar()


class QwtScaleWidget(QWidget):
    
    SIG_SCALE_DIV_CHANGED = SIGNAL("scaleDivChanged()")
    
    # enum LayoutFlag
    TitleInverted = 1
    
    def __init__(self, *args):
        self.__data = None
        align = QwtScaleDraw.LeftScale
        if len(args) == 0:
            parent = None
        elif len(args) == 1:
            parent, = args
        elif len(args) == 2:
            align, parent = args
        else:
            raise TypeError("%s() takes 0, 1 or 2 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
        super(QwtScaleWidget, self).__init__(parent)
        self.initScale(align)
        
    def initScale(self, align):
        self.__data = QwtScaleWidget_PrivateData()
        self.__data.layoutFlags = 0
        if align == QwtScaleDraw.RightScale:
            self.__data.layoutFlags |= self.TitleInverted

        self.__data.borderDist = [0, 0]
        self.__data.minBorderDist = [0, 0]
        self.__data.margin = 4
        self.__data.titleOffset = 0
        self.__data.spacing = 2

        self.__data.scaleDraw = QwtScaleDraw()
        self.__data.scaleDraw.setAlignment(align)
        self.__data.scaleDraw.setLength(10)
        
        self.__data.scaleDraw.setScaleDiv(
                    QwtLinearScaleEngine().divideScale(0.0, 100.0, 10, 5))
        
        self.__data.colorBar.colorMap = QwtLinearColorMap()
        self.__data.colorBar.isEnabled = False
        self.__data.colorBar.width = 10
        
        flags = Qt.AlignmentFlag(Qt.AlignHCenter|Qt.TextExpandTabs|Qt.TextWordWrap)
        self.__data.title.setRenderFlags(flags)
        self.__data.title.setFont(self.font())
        
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        if self.__data.scaleDraw.orientation() == Qt.Vertical:
            policy.transpose()
        
        self.setSizePolicy(policy)
        
        self.setAttribute(Qt.WA_WState_OwnSizePolicy, False)
    
    def setLayoutFlag(self, flag, on=True):
        if (self.__data.layoutFlags & flag != 0) != on:
            if on:
                self.__data.layoutFlags |= flag
            else:
                self.__data.layoutFlags &= ~flag
    
    def testLayoutFlag(self, flag):
        return self.__data.layoutFlags & flag
    
    def setTitle(self, title):
        if isinstance(title, QwtText):
            flags = title.renderFlags() & (~ int(Qt.AlignTop|Qt.AlignBottom))
            title.setRenderFlags(flags)
            if title != self.__data.title:
                self.__data.title = title
                self.layoutScale()
        else:
            if self.__data.title.text() != title:
                self.__data.title.setText(title)
                self.layoutScale()
    
    def setAlignment(self, alignment):
        if self.__data.scaleDraw:
            self.__data.scaleDraw.setAlignment(alignment)
        if not self.testAttribute(Qt.WA_WState_OwnSizePolicy):
            policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                 QSizePolicy.Fixed)
            if self.__data.scaleDraw.orientation() == Qt.Vertical:
                policy.transpose()
            self.setSizePolicy(policy)
            self.setAttribute(Qt.WA_WState_OwnSizePolicy, False)
        self.layoutScale()
    
    def alignment(self):
        if not self.scaleDraw():
            return QwtScaleDraw.LeftScale
        return self.scaleDraw().alignment()
    
    def setBorderDist(self, dist1, dist2):
        if dist1 != self.__data.borderDist[0] or\
           dist2 != self.__data.borderDist[1]:
            self.__data.borderDist = [dist1, dist2]
            self.layoutScale()
    
    def setMargin(self, margin):
        margin = max([0, margin])
        if margin != self.__data.margin:
            self.__data.margin = margin
            self.layoutScale()
    
    def setSpacing(self, spacing):
        spacing = max([0, spacing])
        if spacing != self.__data.spacing:
            self.__data.spacing = spacing
            self.layoutScale()
    
    def setLabelAlignment(self, alignment):
        self.__data.scaleDraw.setLabelAlignment(alignment)
        self.layoutScale()
    
    def setLabelRotation(self, rotation):
        self.__data.scaleDraw.setLabelRotation(rotation)
        self.layoutScale()
    
    def setScaleDraw(self, scaleDraw):
        if scaleDraw is None or scaleDraw == self.__data.scaleDraw:
            return
        sd = self.__data.scaleDraw
        if sd is not None:
            scaleDraw.setAlignment(sd.alignment())
            scaleDraw.setScaleDiv(sd.scaleDiv())
            transform = None
            if sd.scaleMap().transformation():
                transform = sd.scaleMap().transformation().copy()
            scaleDraw.setTransformation(transform)
        self.__data.scaleDraw = scaleDraw
        self.layoutScale()
    
    def scaleDraw(self):
        return self.__data.scaleDraw
    
    def title(self):
        return self.__data.title
    
    def startBorderDist(self):
        return self.__data.borderDist[0]
    
    def endBorderDist(self):
        return self.__data.borderDist[1]

    def margin(self):
        return self.__data.margin
    
    def spacing(self):
        return self.__data.spacing
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setClipRegion(event.region())
        opt = QStyleOption()
        opt.init(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        self.draw(painter)
    
    def draw(self, painter):
        self.__data.scaleDraw.draw(painter, self.palette())
        if self.__data.colorBar.isEnabled and\
           self.__data.colorBar.width > 0 and\
           self.__data.colorBar.interval.isValid():
            self.drawColorBar(painter, self.colorBarRect(self.contentsRect()))
        
        r = self.contentsRect()
        if self.__data.scaleDraw.orientation() == Qt.Horizontal:
            r.setLeft(r.left() + self.__data.borderDist[0])
            r.setWidth(r.width() - self.__data.borderDist[1])
        else:
            r.setTop(r.top() + self.__data.borderDist[0])
            r.setHeight(r.height() - self.__data.borderDist[1])
        
        if not self.__data.title.isEmpty():
            self.drawTitle(painter, self.__data.scaleDraw.alignment(), r)
    
    def colorBarRect(self, rect):
        cr = QRectF(rect)
        if self.__data.scaleDraw.orientation() == Qt.Horizontal:
            cr.setLeft(cr.left() + self.__data.borderDist[0])
            cr.setWidth(cr.width() - self.__data.borderDist[1] + 1)
        else:
            cr.setTop(cr.top() + self.__data.borderDist[0])
            cr.setHeight(cr.height() - self.__data.borderDist[1] + 1)
        sda = self.__data.scaleDraw.alignment()
        if sda == QwtScaleDraw.LeftScale:
            cr.setLeft(cr.right()-self.__data.margin-self.__data.colorBar.width)
            cr.setWidth(self.__data.colorBar.width)
        elif sda == QwtScaleDraw.RightScale:
            cr.setLeft(cr.left()+self.__data.margin)
            cr.setWidth(self.__data.colorBar.width)
        elif sda == QwtScaleDraw.BottomScale:
            cr.setTop(cr.top()+self.__data.margin)
            cr.setHeight(self.__data.colorBar.width)
        elif sda == QwtScaleDraw.TopScale:
            cr.setTop(cr.bottom()-self.__data.margin-self.__data.colorBar.width)
            cr.setHeight(self.__data.colorBar.width)
        return cr
    
    def resizeEvent(self, event):
        self.layoutScale(False)
    
    def layoutScale(self, update_geometry=True):
        bd0, bd1 = self.getBorderDistHint()
        if self.__data.borderDist[0] > bd0:
            bd0 = self.__data.borderDist[0]
        if self.__data.borderDist[1] > bd1:
            bd1 = self.__data.borderDist[1]
        
        colorBarWidth = 0
        if self.__data.colorBar.isEnabled and\
           self.__data.colorBar.interval.isValid():
            colorBarWidth = self.__data.colorBar.width + self.__data.spacing
        
        r = self.contentsRect()
        if self.__data.scaleDraw.orientation() == Qt.Vertical:
            y = r.top() + bd0
            length = r.height() - (bd0 +bd1)
            if self.__data.scaleDraw.alignment() == QwtScaleDraw.LeftScale:
                x = r.right() - 1. - self.__data.margin - colorBarWidth
            else:
                x = r.left() + self.__data.margin + colorBarWidth
        else:
            x = r.left() + bd0
            length = r.width() - (bd0 + bd1)
            if self.__data.scaleDraw.alignment() == QwtScaleDraw.BottomScale:
                y = r.top() + self.__data.margin + colorBarWidth
            else:
                y = r.bottom() - 1. - self.__data.margin - colorBarWidth
        
        self.__data.scaleDraw.move(x, y)
        self.__data.scaleDraw.setLength(length)
        
        extent = ceil(self.__data.scaleDraw.extent(self.font()))
        self.__data.titleOffset = self.__data.margin + self.__data.spacing +\
                                  colorBarWidth + extent
        
        if update_geometry:
            self.updateGeometry()
            self.update()
    
    def drawColorBar(self, painter, rect):
        if not self.__data.colorBar.interval.isValid():
            return
        sd = self.__data.scaleDraw
        QwtPainter.drawColorBar(painter, self.__data.colorBar.colorMap,
                                  self.__data.colorBar.interval.normalized(),
                                  sd.scaleMap(), sd.orientation(), rect)
    
    def drawTitle(self, painter, align, rect):
        r = rect
        flags = self.__data.title.renderFlags()\
                &(~ int(Qt.AlignTop|Qt.AlignBottom|Qt.AlignVCenter))
        if align == QwtScaleDraw.LeftScale:
            angle = -90.
            flags |= Qt.AlignTop
            r.setRect(r.left(), r.bottom(), r.height(),
                      r.width()-self.__data.titleOffset)
        elif align == QwtScaleDraw.RightScale:
            angle = -90.
            flags |= Qt.AlignTop
            r.setRect(r.left()+self.__data.titleOffset, r.bottom(), r.height(),
                      r.width()-self.__data.titleOffset)
        elif align == QwtScaleDraw.BottomScale:
            angle = 0.
            flags |= Qt.AlignBottom
            r.setTop(r.top()+self.__data.titleOffset)
        else:
            angle = 0.
            flags |= Qt.AlignTop
            r.setBottom(r.bottom()-self.__data.titleOffset)
        
        if self.__data.layoutFlags & self.TitleInverted:
            if align in (QwtScaleDraw.LeftScale, QwtScaleDraw.RightScale):
                angle = -angle
                r.setRect(r.x()+r.height(), r.y()-r.width(),
                          r.width(), r.height())
        
        painter.save()
        painter.setFont(self.font())
        painter.setPen(self.palette().color(QPalette.Text))
        
        painter.translate(r.x(), r.y())
        if angle != 0.:
            painter.rotate(angle)
        
        title = self.__data.title
        title.setRenderFlags(flags)
        title.draw(painter, QRectF(0., 0., r.width(), r.height()))
        
        painter.restore()
    
    def scaleChange(self):
        self.layoutScale()
        
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def minimumSizeHint(self):
        o = self.__data.scaleDraw.orientation()
        length = 0
        mbd1, mbd2 = self.getBorderDistHint()
        length += max([0, self.__data.borderDist[0]-mbd1])
        length += max([0, self.__data.borderDist[1]-mbd2])
        length += self.__data.scaleDraw.minLength(self.font())
        
        dim = self.dimForLength(length, self.font())
        if length < dim:
            length = dim
            dim = self.dimForLength(length, self.font())
        
        size = QSize(length+2, dim)
        if o == Qt.Vertical:
            size.transpose()
        
        left, right, top, bottom = self.getContentsMargins()
        return size + QSize(left + right, top + bottom)
    
    def titleHeightForWidth(self, width):
        return ceil(self.__data.title.heightForWidth(width, self.font()))
    
    def dimForLength(self, length, scaleFont):
        extent = ceil(self.__data.scaleDraw.extent(scaleFont))
        dim = self.__data.margin + extent + 1
        if not self.__data.title.isEmpty():
            dim += self.titleHeightForWidth(length)+self.__data.spacing
        if self.__data.colorBar.isEnabled and self.__data.colorBar.interval.isValid():
            dim += self.__data.colorBar.width+self.__data.spacing
        return dim
    
    def getBorderDistHint(self):
        start, end = self.__data.scaleDraw.getBorderDistHint(self.font())
        if start < self.__data.minBorderDist[0]:
            start = self.__data.minBorderDist[0]
        if end < self.__data.minBorderDist[1]:
            end = self.__data.minBorderDist[1]
        return start, end
    
    def setMinBorderDist(self, start, end):
        self.__data.minBorderDist = [start, end]
    
    def getMinBorderDist(self):
        return self.__data.minBorderDist
    
    def setScaleDiv(self, scaleDiv):
        sd = self.__data.scaleDraw
        if sd.scaleDiv() != scaleDiv:
            sd.setScaleDiv(scaleDiv)
            self.layoutScale()
            self.emit(self.SIG_SCALE_DIV_CHANGED)

    def setTransformation(self, transformation):
        self.__data.scaleDraw.setTransformation(transformation)
        self.layoutScale()
    
    def setColorBarEnabled(self, on):
        if on != self.__data.colorBar.isEnabled:
            self.__data.colorBar.isEnabled = on
            self.layoutScale()
    
    def isColorBarEnabled(self):
        return self.__data.colorBar.isEnabled
    
    def setColorBarWidth(self, width):
        if width != self.__data.colorBar.width:
            self.__data.colorBar.width = width
            if self.isColorBarEnabled():
                self.layoutScale()
    
    def colorBarWidth(self):
        return self.__data.colorBar.width
    
    def colorBarInterval(self):
        return self.__data.colorBar.interval
    
    def setColorMap(self, interval, colorMap):
        self.__data.colorBar.interval = interval
        if colorMap != self.__data.colorBar.colorMap:
            self.__data.colorBar.colorMap = colorMap
        if self.isColorBarEnabled():
            self.layoutScale()
    
    def colorMap(self):
        return self.__data.colorBar.colorMap

