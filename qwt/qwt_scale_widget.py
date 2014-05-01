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
        self.d_data = None
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
        self.d_data = QwtScaleWidget_PrivateData()
        self.d_data.layoutFlags = 0
        if align == QwtScaleDraw.RightScale:
            self.d_data.layoutFlags |= self.TitleInverted

        self.d_data.borderDist = [0, 0]
        self.d_data.minBorderDist = [0, 0]
        self.d_data.margin = 4
        self.d_data.titleOffset = 0
        self.d_data.spacing = 2

        self.d_data.scaleDraw = QwtScaleDraw()
        self.d_data.scaleDraw.setAlignment(align)
        self.d_data.scaleDraw.setLength(10)
        
        self.d_data.scaleDraw.setScaleDiv(
                    QwtLinearScaleEngine().divideScale(0.0, 100.0, 10, 5))
        
        self.d_data.colorBar.colorMap = QwtLinearColorMap()
        self.d_data.colorBar.isEnabled = False
        self.d_data.colorBar.width = 10
        
        flags = int(Qt.AlignHCenter|Qt.TextExpandTabs|Qt.TextWordWrap)
        self.d_data.title.setRenderFlags(flags)
        self.d_data.title.setFont(self.font())
        
        policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        if self.d_data.scaleDraw.orientation() == Qt.Vertical:
            policy.transpose()
        
        self.setSizePolicy(policy)
        
        self.setAttribute(Qt.WA_WState_OwnSizePolicy, False)
    
    def setLayoutFlag(self, flag, on):
        if (self.d_data.layoutFlags & flag != 0) != on:
            if on:
                self.d_data.layoutFlags |= flag
            else:
                self.d_data.layoutFlags &= ~flag
    
    def testLayoutFlag(self, flag):
        return self.d_data.layoutFlags & flag
    
    def setTitle(self, title):
        if isinstance(title, QwtText):
            flags = title.renderFlags() & (~ int(Qt.AlignTop|Qt.AlignBottom))
            title.setRenderFlags(flags)
            if title != self.d_data.title:
                self.d_data.title = title
                self.layoutScale()
        else:
            if self.d_data.title.text() != title:
                self.d_data.title.setText(title)
                self.layoutScale()
    
    def setAlignment(self, alignment):
        if self.d_data.scaleDraw:
            self.d_data.scaleDraw.setAlignment(alignment)
        if not self.testAttribute(Qt.WA_WState_OwnSizePolicy):
            policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                 QSizePolicy.Fixed)
            if self.d_data.scaleDraw.orientation() == Qt.Vertical:
                policy.transpose()
            self.setSizePolicy(policy)
            self.setAttribute(Qt.WA_WState_OwnSizePolicy, False)
        self.layoutScale()
    
    def alignment(self):
        if not self.scaleDraw():
            return QwtScaleDraw.LeftScale
        return self.scaleDraw().alignment()
    
    def setBorderDist(self, dist1, dist2):
        if dist1 != self.d_data.borderDist[0] or\
           dist2 != self.d_data.borderDist[1]:
            self.d_data.borderDist = [dist1, dist2]
            self.layoutScale()
    
    def setMargin(self, margin):
        margin = max([0, margin])
        if margin != self.d_data.margin:
            self.d_data.margin = margin
            self.layoutScale()
    
    def setSpacing(self, spacing):
        spacing = max([0, spacing])
        if spacing != self.d_data.spacing:
            self.d_data.spacing = spacing
            self.layoutScale()
    
    def setLabelAlignment(self, alignment):
        self.d_data.scaleDraw.setLabelAlignment(alignment)
        self.layoutScale()
    
    def setLabelRotation(self, rotation):
        self.d_data.scaleDraw.setLabelRotation(rotation)
        self.layoutScale()
    
    def setScaleDraw(self, scaleDraw):
        if scaleDraw is None or scaleDraw == self.d_data.scaleDraw:
            return
        sd = self.d_data.scaleDraw
        if sd:
            scaleDraw.setAlignment(sd.alignment())
            scaleDraw.setScaleDiv(sd.scaleDiv())
            transform = None
            if sd.scaleMap().transformation():
                transform = sd.scaleMap().transformation().copy()
            scaleDraw.setTransformation(transform)
        self.d_data.scaleDraw = scaleDraw
        self.layoutScale()
    
    def scaleDraw(self):
        return self.d_data.scaleDraw
    
    def title(self):
        return self.d_data.title
    
    def startBorderDist(self):
        return self.d_data.borderDist[0]
    
    def endBorderDist(self):
        return self.d_data.borderDist[1]

    def margin(self):
        return self.d_data.margin
    
    def spacing(self):
        return self.d_data.spacing
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setClipRegion(event.region())
        opt = QStyleOption()
        opt.init(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        self.draw(painter)
    
    def draw(self, painter):
        self.d_data.scaleDraw.draw(painter, self.palette())
        if self.d_data.colorBar.isEnabled and\
           self.d_data.colorBar.width > 0 and\
           self.d_data.colorBar.interval.isValid():
            self.drawColorBar(painter, self.colorBarRect(self.contentsRect()))
        
        r = self.contentsRect()
        if self.d_data.scaleDraw.orientation() == Qt.Horizontal:
            r.setLeft(r.left() + self.d_data.borderDist[0])
            r.setWidth(r.width() - self.d_data.borderDist[1])
        else:
            r.setTop(r.top() + self.d_data.borderDist[0])
            r.setHeight(r.height() - self.d_data.borderDist[1])
        
        if not self.d_data.title.isEmpty():
            self.drawTitle(painter, self.d_data.scaleDraw.alignment(), r)
    
    def colorBarRect(self, rect):
        cr = rect
        if self.d_data.scaleDraw.orientation() == Qt.Horizontal:
            cr.setLeft(cr.left() + self.d_data.borderDist[0])
            cr.setWidth(cr.width() - self.d_data.borderDist[1] + 1)
        else:
            cr.setTop(cr.top() + self.d_data.borderDist[0])
            cr.setHeight(cr.height() - self.d_data.borderDist[1] + 1)
        sda = self.d_data.scaleDraw.alignment()
        if sda == QwtScaleDraw.LeftScale:
            cr.setLeft(cr.right()-self.d_data.margin-self.d_data.colorBar.width)
            cr.setWidth(self.d_data.colorBar.width)
        elif sda == QwtScaleDraw.RightScale:
            cr.setLeft(cr.left()+self.d_data.margin)
            cr.setWidth(self.d_data.colorBar.width)
        elif sda == QwtScaleDraw.BottomScale:
            cr.setTop(cr.top()+self.d_data.margin)
            cr.setHeight(self.d_data.colorBar.width)
        elif sda == QwtScaleDraw.TopScale:
            cr.setTop(cr.bottom()-self.d_data.margin-self.d_data.colorBar.width)
            cr.setHeight(self.d_data.colorBar.width)
        return cr
    
    def resizeEvent(self, event):
        self.layoutScale(False)
    
    def layoutScale(self, update_geometry=True):
        bd0, bd1 = self.getBorderDistHint()
        if self.d_data.borderDist[0] > bd0:
            bd0 = self.d_data.borderDist[0]
        if self.d_data.borderDist[1] > bd1:
            bd1 = self.d_data.borderDist[1]
        
        colorBarWidth = 0
        if self.d_data.colorBar.isEnabled and\
           self.d_data.colorBar.interval.isValid():
            colorBarWidth = self.d_data.colorBar.width + self.d_data.spacing
        
        r = self.contentsRect()
        if self.d_data.scaleDraw.orientation() == Qt.Vertical:
            y = r.top() + bd0
            length = r.height() - (bd0 +bd1)
            if self.d_data.scaleDraw.alignment() == QwtScaleDraw.LeftScale:
                x = r.right() - 1. - self.d_data.margin - colorBarWidth
            else:
                x = r.left() + self.d_data.margin + colorBarWidth
        else:
            x = r.left() + bd0
            length = r.width() - (bd0 + bd1)
            if self.d_data.scaleDraw.alignment() == QwtScaleDraw.BottomScale:
                y = r.top() + self.d_data.margin + colorBarWidth
            else:
                y = r.bottom() - 1. - self.d_data.margin - colorBarWidth
        
        self.d_data.scaleDraw.move(x, y)
        self.d_data.scaleDraw.setLength(length)
        
        extent = ceil(self.d_data.scaleDraw.extent(self.font()))
        self.d_data.titleOffset = self.d_data.margin + self.d_data.spacing +\
                                  colorBarWidth + extent
        
        if update_geometry:
            self.updateGeometry()
            self.update()
    
    def drawColorBar(self, painter, rect):
        if not self.d_data.colorBar.interval.isValid():
            return
        sd = self.d_data.scaleDraw
        QwtPainter.drawColorBar(painter, self.d_data.colorBar.colorMap,
                                self.d_data.colorBar.interval.normalized(),
                                sd.scaleMap(), sd.orientation(), rect)
    
    def drawTitle(self, painter, align, rect):
        r = rect
        flags = self.d_data.title.renderFlags()\
                &(~ int(Qt.AlignTop|Qt.AlignBottom|Qt.AlignVCenter))
        if align == QwtScaleDraw.LeftScale:
            angle = -90.
            flags |= Qt.AlignTop
            r.setRect(r.left(), r.bottom(), r.height(),
                      r.width()-self.d_data.titleOffset)
        elif align == QwtScaleDraw.RightScale:
            angle = -90.
            flags |= Qt.AlignTop
            r.setRect(r.left()+self.d_data.titleOffset, r.bottom(), r.height(),
                      r.width()-self.d_data.titleOffset)
        elif align == QwtScaleDraw.BottomScale:
            angle = 0.
            flags |= Qt.AlignBottom
            r.setTop(r.top()+self.d_data.titleOffset)
        else:
            angle = 0.
            flags |= Qt.AlignTop
            r.setBottom(r.bottom()-self.d_data.titleOffset)
        
        if self.d_data.layoutFlags & self.TitleInverted:
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
        
        title = self.d_data.title
        title.setRenderFlags(flags)
        title.draw(painter, QRectF(0., 0., r.width(), r.height()))
        
        painter.restore()
    
    def scaleChange(self):
        self.layoutScale()
        
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def minimumSizeHint(self):
        o = self.d_data.scaleDraw.orientation()
        length = 0
        mbd1, mbd2 = self.getBorderDistHint()
        length += max([0, self.d_data.borderDist[0]-mbd1])
        length += max([0, self.d_data.borderDist[1]-mbd2])
        length += self.d_data.scaleDraw.minLength(self.font())
        
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
        return ceil(self.d_data.title.heightForWidth(width, self.font()))
    
    def dimForLength(self, length, scaleFont):
        extent = ceil(self.d_data.scaleDraw.extent(scaleFont))
        dim = self.d_data.margin + extent + 1
        if not self.d_data.title.isEmpty():
            dim += self.titleHeightForWidth(length)+self.d_data.spacing
        if self.d_data.colorBar.isEnabled and self.d_data.colorBar.interval.isValid():
            dim += self.d_data.colorBar.width+self.d_data.spacing
        return dim
    
    def getBorderDistHint(self):
        start, end = self.d_data.scaleDraw.getBorderDistHint(self.font())
        if start < self.d_data.minBorderDist[0]:
            start = self.d_data.minBorderDist[0]
        if end < self.d_data.minBorderDist[1]:
            end = self.d_data.minBorderDist[1]
        return start, end
    
    def setMinBorderDist(self, start, end):
        self.d_data.minBorderDist = [start, end]
    
    def getMinBorderDist(self):
        return self.d_data.minBorderDist
    
    def setScaleDiv(self, scaleDiv):
        sd = self.d_data.scaleDraw
        if sd.scaleDiv() != scaleDiv:
            sd.setScaleDiv(scaleDiv)
            self.layoutScale()
            self.emit(self.SIG_SCALE_DIV_CHANGED)

    def setTransformation(self, transformation):
        self.d_data.scaleDraw.setTransformation(transformation)
        self.layoutScale()
    
    def setColorBarEnabled(self, on):
        if on != self.d_data.colorBar.isEnabled:
            self.d_data.colorBar.isEnabled = on
            self.layoutScale()
    
    def isColorBarEnabled(self):
        return self.d_data.colorBar.isEnabled
    
    def setColorBarWidth(self, width):
        if width != self.d_data.colorBar.width:
            self.d_data.colorBar.width = width
            if self.isColorBarEnabled():
                self.layoutScale()
    
    def colorBarWidth(self):
        return self.d_data.colorBar.width
    
    def colorBarInterval(self):
        return self.d_data.colorBar.interval
    
    def setColorMap(self, interval, colorMap):
        self.d_data.colorBar.interval = interval
        if colorMap != self.d_data.colorBar.colorMap:
            self.d_data.colorBar.colorMap = colorMap
        if self.isColorBarEnabled():
            self.layoutScale()
    
    def colorMap(self):
        return self.d_data.colorBar.colorMap

