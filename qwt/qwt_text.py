# -*- coding: utf-8 -*-

from qwt.qwt_painter import QwtPainter
from qwt.qwt_text_engine import QwtPlainTextEngine, QwtRichTextEngine

from qwt.qt.QtGui import (QPainter, QFrame, QSizePolicy, QPalette, QFont,
                          QFontMetrics, QApplication, QColor)
from qwt.qt.QtCore import Qt, QSizeF, QSize, QRectF

import math


class QwtText_PrivateData(object):
    def __init__(self):
        self.renderFlags = Qt.AlignCenter
        self.borderRadius = 0
        self.borderPen = Qt.NoPen
        self.backgroundBrush = Qt.NoBrush
        self.paintAttributes = 0
        self.layoutAttributes = 0
        self.textEngine = None
        
        self.text = None
        self.font = None
        self.color = None

class QwtText_LayoutCache(object):
    def __init__(self):
        self.textSize = QSizeF()
        self.font = None
    
    def invalidate(self):
        self.textSize = QSizeF()

class QwtText(object):

    # enum TextFormat
    AutoText, PlainText, RichText, MathMLText, TeXText = range(5)
    OtherFormat = 100
    
    # enum PaintAttribute
    PaintUsingTextFont = 0x01
    PaintUsingTextColor = 0x02
    PaintBackground = 0x04
    
    # enum LayoutAttribute
    MinimumLayout = 0x01

    def __init__(self, *args):
        self._desktopwidget = None
        self._dict = QwtTextEngineDict()
        if len(args) in (0, 2):
            if len(args) == 2:
                text, textFormat = args
            else:
                text, textFormat = "", self.AutoText
            self.__data = QwtText_PrivateData()
            self.__data.text = text
            self.__data.textEngine = self.textEngine(text, textFormat)
            self.__layoutCache = QwtText_LayoutCache()
        elif len(args) == 1:
            if isinstance(args[0], QwtText):
                other, = args
                self.__data = other.__data
                self.__layoutCache = other.__layoutCache
            else:
                text, = args
                textFormat = self.AutoText
                self.__data = QwtText_PrivateData()
                self.__data.text = text
                self.__data.textEngine = self.textEngine(text, textFormat)
                self.__layoutCache = QwtText_LayoutCache()
        else:
            raise TypeError("%s() takes 0, 1 or 2 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))

    @property
    def desktopwidget(self):
        if self._desktopwidget is None:
            self._desktopwidget = QApplication.desktop()
        return self._desktopwidget
    
    def __eq__(self, other):
        return self.__data.renderFlags == other.__data.renderFlags and\
               self.__data.text == other.__data.text and\
               self.__data.font == other.__data.font and\
               self.__data.color == other.__data.color and\
               self.__data.borderRadius == other.__data.borderRadius and\
               self.__data.borderPen == other.__data.borderPen and\
               self.__data.backgroundBrush == other.__data.backgroundBrush and\
               self.__data.paintAttributes == other.__data.paintAttributes and\
               self.__data.textEngine == other.__data.textEngine

    def __ne__(self, other):
        return not self.__eq__(other)

    def isEmpty(self):
        return len(self.text()) == 0

    def setText(self, text, textFormat=None):
        if textFormat is None:
            textFormat = self.AutoText
        self.__data.text = text
        self.__data.textEngine = self.textEngine(text, textFormat)
        self.__layoutCache.invalidate()
    
    def text(self):
        return self.__data.text
    
    def setRenderFlags(self, renderFlags):
        renderFlags = Qt.AlignmentFlag(renderFlags)
        if renderFlags != self.__data.renderFlags:
            self.__data.renderFlags = renderFlags
            self.__layoutCache.invalidate()
    
    def renderFlags(self):
        return self.__data.renderFlags
    
    def setFont(self, font):
        self.__data.font = font
        self.setPaintAttribute(self.PaintUsingTextFont)
    
    def font(self):
        return self.__data.font
        
    def usedFont(self, defaultFont):
        if self.__data.paintAttributes & self.PaintUsingTextFont:
            return self.__data.font
        return defaultFont
    
    def setColor(self, color):
        self.__data.color = QColor(color)
        self.setPaintAttribute(self.PaintUsingTextColor)
    
    def color(self):
        return self.__data.color
    
    def usedColor(self, defaultColor):
        if self.__data.paintAttributes & self.PaintUsingTextColor:
            return self.__data.color
        return defaultColor
    
    def setBorderRadius(self, radius):
        self.__data.borderRadius = max([0., radius])
    
    def borderRadius(self):
        return self.__data.borderRadius
    
    def setBorderPen(self, pen):
        self.__data.borderPen = pen
        self.setPaintAttribute(self.PaintBackground)
    
    def borderPen(self):
        return self.__data.borderPen
            
    def setBackgroundBrush(self, brush):
        self.__data.backgroundBrush = brush
        self.setPaintAttribute(self.PaintBackground)
    
    def backgroundBrush(self):
        return self.__data.backgroundBrush
    
    def setPaintAttribute(self, attribute, on=True):
        if on:
            self.__data.paintAttributes |= attribute
        else:
            self.__data.paintAttributes &= ~attribute
    
    def testPaintAttribute(self, attribute):
        return self.__data.paintAttributes & attribute
        
    
    def setLayoutAttribute(self, attribute, on=True):
        if on:
            self.__data.layoutAttributes |= attribute
        else:
            self.__data.layoutAttributes &= ~attribute
    
    def testLayoutAttribute(self, attribute):
        return self.__data.layoutAttributes & attribute
    
    def heightForWidth(self, width, defaultFont=None):
        if defaultFont is None:
            defaultFont = QFont()
        font = QFont(self.usedFont(defaultFont), self.desktopwidget)
        h = 0
        if self.__data.layoutAttributes & self.MinimumLayout:
            (left, right, top, bottom
             ) = self.__data.textEngine.textMargins(font)
            h = self.__data.textEngine.heightForWidth(font,
                            self.__data.renderFlags, self.__data.text,
                            width + left + right)
            h -= top + bottom
        else:
            h = self.__data.textEngine.heightForWidth(font,
                            self.__data.renderFlags, self.__data.text, width)
        return h
    
    def textSize(self, defaultFont):
        font = QFont(self.usedFont(defaultFont), self.desktopwidget)
        if not self.__layoutCache.textSize.isValid() or\
           self.__layoutCache.font is not font:
            self.__layoutCache.textSize =\
                self.__data.textEngine.textSize(font, self.__data.renderFlags,
                                                self.__data.text)
            self.__layoutCache.font = font
        sz = self.__layoutCache.textSize
        if self.__data.layoutAttributes & self.MinimumLayout:
            (left, right, top, bottom
             ) = self.__data.textEngine.textMargins(font)
            sz -= QSizeF(left + right, top + bottom)
        return sz
    
    def draw(self, painter, rect):
        if self.__data.paintAttributes & self.PaintBackground:
            if self.__data.borderPen != Qt.NoPen or\
               self.__data.backgroundBrush != Qt.NoBrush:
                painter.save()
                painter.setPen(self.__data.borderPen)
                painter.setBrush(self.__data.backgroundBrush)
                if self.__data.borderRadius == 0:
                    QwtPainter.drawRect(painter, rect)
                else:
                    painter.setRenderHint(QPainter.Antialiasing, True)
                    painter.drawRoundedRect(rect, self.__data.borderRadius,
                                            self.__data.borderRadius)
                painter.restore()
        painter.save()
        if self.__data.paintAttributes & self.PaintUsingTextFont:
            painter.setFont(self.__data.font)
        if self.__data.paintAttributes & self.PaintUsingTextColor:
            if self.__data.color.isValid():
                painter.setPen(self.__data.color)
        expandedRect = rect
        if self.__data.layoutAttributes & self.MinimumLayout:
            font = QFont(painter.font(), self.desktopwidget)
            (left, right, top, bottom
             ) = self.__data.textEngine.textMargins(font)
            expandedRect.setTop(rect.top()-top)
            expandedRect.setBottom(rect.bottom()+bottom)
            expandedRect.setLeft(rect.left()-left)
            expandedRect.setRight(rect.right()+right)
        self.__data.textEngine.draw(painter, expandedRect,
                                    self.__data.renderFlags, self.__data.text)
        painter.restore()
    
    def textEngine(self, *args):
        return self._dict.textEngine(*args)
    
    def setTextEngine(self, format_, engine):
        self._dict.setTextEngine(format_, engine)


class QwtTextEngineDict(object):
    # Optimization: a single text engine for all QwtText objects
    # (this is not how it's implemented in Qwt6 C++ library)
    __map = {QwtText.PlainText: QwtPlainTextEngine(),
             QwtText.RichText:  QwtRichTextEngine()}
    
    def textEngine(self, *args):
        if len(args) == 1:
            format_ = args[0]
            return self.__map.get(format_)
        elif len(args) == 2:
            text, format_ = args
        
            if format_ == QwtText.AutoText:
                for key, engine in list(self.__map.iteritems()):
                    if key != QwtText.PlainText:
                        if engine and engine.mightRender(text):
                            return engine
            
            engine = self.__map.get(format_)
            if engine is not None:
                return engine
            
            engine = self.__map[QwtText.PlainText]
            return engine
        else:
            raise TypeError("%s().textEngine() takes 1 or 2 argument(s) (%s "\
                            "given)" % (self.__class__.__name__, len(args)))
        
    def setTextEngine(self, format_, engine):
        if format_ == QwtText.AutoText:
            return
        if format_ == QwtText.PlainText and engine is None:
            return
        self.__map.setdefault(format_, engine)


class QwtTextLabel_PrivateData(object):
    def __init__(self):
        self.indent = 4
        self.margin = 0
        self.text = QwtText()


class QwtTextLabel(QFrame):
    def __init__(self, *args):
        if len(args) == 0:
            text, parent = None, None
        elif len(args) == 1:
            text = None
            parent, = args
        elif len(args) == 2:
            text, parent = args
        else:
            raise TypeError("%s() takes 0, 1 or 2 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
        super(QwtTextLabel, self).__init__(parent)
        self.init()
        if text is not None:
            self.__data.text = text
    
    def init(self):
        self.__data = QwtTextLabel_PrivateData()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    
    def setPlainText(self, text):
        self.setText(QwtText(text))
        
    def plainText(self):
        return self.__data.text.text()
    
    def setText(self, text, textFormat=QwtText.AutoText):
        if isinstance(text, QwtText):
            self.__data.text = text
        else:
            self.__data.text.setText(text, textFormat)
        self.update()
        self.updateGeometry()
    
    def text(self):
        return self.__data.text
        
    def clear(self):
        self.__data.text = QwtText()
        self.update()
        self.updateGeometry()
    
    def indent(self):
        return self.__data.indent
    
    def setIndent(self, indent):
        if indent < 0:
            indent = 0
        self.__data.indent = indent
        self.update()
        self.updateGeometry()
    
    def margin(self):
        return self.__data.margin
        
    def setMargin(self, margin):
        self.__data.margin = margin
        self.update()
        self.updateGeometry()
    
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def minimumSizeHint(self):
        sz = self.__data.text.textSize(self.font())
        mw = 2*(self.frameWidth()+self.__data.margin)
        mh = mw
        indent = self.__data.indent
        if indent <= 0:
            indent = self.defaultIndent()
        if indent > 0:
            align = self.__data.text.renderFlags()
            if align & Qt.AlignLeft or align & Qt.AlignRight:
                mw += self.__data.indent
            elif align & Qt.AlignTop or align & Qt.AlignBottom:
                mh += self.__data.indent
        sz += QSizeF(mw, mh)
        return QSize(math.ceil(sz.width()), math.ceil(sz.height()))

    def heightForWidth(self, width):
        renderFlags = self.__data.text.renderFlags()
        indent = self.__data.indent
        if indent <= 0:
            indent = self.defaultIndent()
        width -= 2*self.frameWidth()
        if renderFlags & Qt.AlignLeft or renderFlags & Qt.AlignRight:
            width -= indent
        height = math.ceil(self.__data.text.heightForWidth(width, self.font()))
        if renderFlags & Qt.AlignTop or renderFlags & Qt.AlignBottom:
            height += indent
        height += 2*self.frameWidth()
        return height
    
    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.contentsRect().contains(event.rect()):
            painter.save()
            painter.setClipRegion(event.region() & self.frameRect())
            self.drawFrame(painter)
            painter.restore()
        painter.setClipRegion(event.region() & self.contentsRect())
        self.drawContents(painter)
    
    def drawContents(self, painter):
        r = self.textRect()
        if r.isEmpty():
            return
        painter.setFont(self.font())
        painter.setPen(self.palette().color(QPalette.Active, QPalette.Text))
        self.drawText(painter, QRectF(r))
        if self.hasFocus():
            m = 2
            focusRect = self.contentsRect().adjusted(m, m, -m+1, -m+1)
            QwtPainter.drawFocusRect(painter, self, focusRect)
    
    def drawText(self, painter, textRect):
        self.__data.text.draw(painter, textRect)
    
    def textRect(self):
        r = self.contentsRect()
        if not r.isEmpty() and self.__data.margin > 0:
            r.setRect(r.x()+self.__data.margin, r.y()+self.__data.margin,
                      r.width()-2*self.__data.margin,
                      r.height()-2*self.__data.margin)
        if not r.isEmpty():
            indent = self.__data.indent
            if indent <= 0:
                indent = self.defaultIndent()
            if indent > 0:
                renderFlags = self.__data.text.renderFlags()
                if renderFlags & Qt.AlignLeft:
                    r.setX(r.x()+indent)
                elif renderFlags & Qt.AlignRight:
                    r.setWidth(r.width()-indent)
                elif renderFlags & Qt.AlignTop:
                    r.setY(r.y()+indent)
                elif renderFlags & Qt.AlignBottom:
                    r.setHeight(r.height()-indent)
        return r
    
    def defaultIndent(self):
        if self.frameWidth() <= 0:
            return 0
        if self.__data.text.testPaintAttribute(QwtText.PaintUsingTextFont):
            fnt = self.__data.text.font()
        else:
            fnt = self.font()
        return QFontMetrics(fnt).width('x')/2
