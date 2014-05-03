# -*- coding: utf-8 -*-

from qwt.qwt_painter import QwtPainter
from qwt.qwt_text_engine import QwtPlainTextEngine, QwtRichTextEngine

from qwt.qt.QtGui import (QPainter, QFrame, QSizePolicy, QPalette, QFont,
                          QFontMetrics, QApplication)
from qwt.qt.QtCore import Qt, QSizeF, QSize, QRectF

import math


class QwtTextEngineDict(object):
    def __init__(self):
        self.d_map = {QwtText.PlainText: QwtPlainTextEngine(),
                      QwtText.RichText:  QwtRichTextEngine()}
    
    def textEngine(self, *args):
        if len(args) == 1:
            format_ = args[0]
            return self.d_map.get(format_)
        elif len(args) == 2:
            text, format_ = args
        
            if format_ == QwtText.AutoText:
                for key, engine in list(self.d_map.iteritems()):
                    if key != QwtText.PlainText:
                        if engine and engine.mightRender(text):
                            return engine
            
            engine = self.d_map.get(format_)
            if engine is not None:
                return engine
            
            engine = self.d_map[QwtText.PlainText]
            return engine
        else:
            raise TypeError("%s().textEngine() takes 1 or 2 argument(s) (%s "\
                            "given)" % (self.__class__.__name__, len(args)))
        
    def setTextEngine(self, format_, engine):
        if format_ == QwtText.AutoText:
            return
        if format_ == QwtText.PlainText and engine is None:
            return
        self.d_map.setdefault(format_, engine)


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
        self.textSize = None
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
        QwtPlainTextEngine()
        self._dict = QwtTextEngineDict()
        if len(args) in (0, 2):
            if len(args) == 2:
                text, textFormat = args
            else:
                text, textFormat = "", self.AutoText
            self.d_data = QwtText_PrivateData()
            self.d_data.text = text
            self.d_data.textEngine = self.textEngine(text, textFormat)
            self.d_layoutCache = QwtText_LayoutCache()
        elif len(args) == 1:
            if isinstance(args[0], QwtText):
                other, = args
                self.d_data = other.d_data
                self.d_layoutCache = other.d_layoutCache
            else:
                text, = args
                textFormat = self.AutoText
                self.d_data = QwtText_PrivateData()
                self.d_data.text = text
                self.d_data.textEngine = self.textEngine(text, textFormat)
                self.d_layoutCache = QwtText_LayoutCache()
        else:
            raise TypeError("%s() takes 0, 1 or 2 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def __eq__(self, other):
        return self.d_data.renderFlags == other.d_data.renderFlags and\
               self.d_data.text == other.d_data.text and\
               self.d_data.font == other.d_data.font and\
               self.d_data.color == other.d_data.color and\
               self.d_data.borderRadius == other.d_data.borderRadius and\
               self.d_data.borderPen == other.d_data.borderPen and\
               self.d_data.backgroundBrush == other.d_data.backgroundBrush and\
               self.d_data.paintAttributes == other.d_data.paintAttributes and\
               self.d_data.textEngine == other.d_data.textEngine

    def __ne__(self, other):
        return not self.__eq__(other)

    def isEmpty(self):
        return len(self.text()) == 0

    def setText(self, text, textFormat=None):
        if textFormat is None:
            textFormat = self.AutoText
        self.d_data.text = text
        self.d_data.textEngine = self.textEngine(text, textFormat)
        self.d_layoutCache.invalidate()
    
    def text(self):
        return self.d_data.text
    
    def setRenderFlags(self, renderFlags):
        if renderFlags != self.d_data.renderFlags:
            self.d_data.renderFlags = renderFlags
            self.d_layoutCache.invalidate()
    
    def renderFlags(self):
        return self.d_data.renderFlags
    
    def setFont(self, font):
        self.d_data.font = font
        self.setPaintAttribute(self.PaintUsingTextFont)
    
    def font(self):
        return self.d_data.font
        
    def usedFont(self, defaultFont):
        if self.d_data.paintAttributes & self.PaintUsingTextFont:
            return self.d_data.font
        return defaultFont
    
    def setColor(self, color):
        self.d_data.color = color
        self.setPaintAttribute(self.PaintUsingTextColor)
    
    def color(self):
        return self.d_data.color
    
    def usedColor(self, defaultColor):
        if self.d_data.paintAttributes & self.PaintUsingTextColor:
            return self.d_data.color
        return defaultColor
    
    def setBorderRadius(self, radius):
        self.d_data.borderRadius = max([0., radius])
    
    def borderRadius(self):
        return self.d_data.borderRadius
    
    def setBorderPen(self, pen):
        self.d_data.borderPen = pen
        self.setPaintAttribute(self.PaintBackground)
    
    def borderPen(self):
        return self.d_data.borderPen
            
    def setBackgroundBrush(self, brush):
        self.d_data.backgroundBrush = brush
        self.setPaintAttribute(self.PaintBackground)
    
    def backgroundBrush(self):
        return self.d_data.backgroundBrush
    
    def setPaintAttribute(self, attribute, on=True):
        if on:
            self.d_data.paintAttributes |= attribute
        else:
            self.d_data.paintAttributes &= ~attribute
    
    def testPaintAttribute(self, attribute):
        return self.d_data.paintAttributes & attribute
        
    
    def setLayoutAttribute(self, attribute, on=True):
        if on:
            self.d_data.layoutAttributes |= attribute
        else:
            self.d_data.layoutAttributes &= ~attribute
    
    def testLayoutAttribute(self, attribute):
        return self.d_data.layoutAttributes & attribute
    
    def heightForWidth(self, width, defaultFont=None):
        if defaultFont is None:
            defaultFont = QFont()
        font = QFont(self.usedFont(defaultFont), QApplication.desktop())
        h = 0
        if self.d_data.layoutAttributes & self.MinimumLayout:
            (left, right, top, bottom
             ) = self.d_data.textEngine.textMargins(font)
            h = self.d_data.textEngine.heightForWidth(font,
                            self.d_data.renderFlags, self.d_data.text,
                            width + left + right)
            h -= top + bottom
        else:
            h = self.d_data.textEngine.heightForWidth(font,
                            self.d_data.renderFlags, self.d_data.text, width)
        return h
    
    def textSize(self, defaultFont):
        font = QFont(self.usedFont(defaultFont), QApplication.desktop())
        if not self.d_layoutCache.textSize.isValid() or\
           self.d_layoutCache.font is not font:
            self.d_layoutCache.textSize =\
                self.d_data.textEngine.textSize(font, self.d_data.renderFlags,
                                                self.d_data.text)
            self.d_layoutCache.font = font
        sz = self.d_layoutCache.textSize
        if self.d_data.layoutAttributes & self.MinimumLayout:
            (left, right, top, bottom
             ) = self.d_data.textEngine.textMargins(font)
            sz -= QSizeF(left + right, top + bottom)
        return sz
    
    def draw(self, painter, rect):
        if self.d_data.paintAttributes & self.PaintBackground:
            if self.d_data.borderPen != Qt.NoPen or\
               self.d_data.backgroundBrush != Qt.NoBrush:
                painter.save()
                painter.setPen(self.d_data.borderPen)
                painter.setBrush(self.d_data.backgroundBrush)
                if self.d_data.borderRadius == 0:
                    QwtPainter.drawRect(painter, rect)
                else:
                    painter.setRenderHint(QPainter.Antialiasing, True)
                    painter.drawRoundedRect(rect, self.d_data.borderRadius,
                                            self.d_data.borderRadius)
                painter.restore()
        painter.save()
        if self.d_data.paintAttributes & self.PaintUsingTextFont:
            painter.setFont(self.d_data.font)
        if self.d_data.paintAttributes & self.PaintUsingTextColor:
            if self.d_data.color.isValid():
                painter.setPen(self.d_data.color)
        expandedRect = rect
        if self.d_data.layoutAttributes & self.MinimumLayout:
            font = QFont(painter.font(), QApplication.desktop())
            (left, right, top, bottom
             ) = self.d_data.textEngine.textMargins(font)
            expandedRect.setTop(rect.top()-top)
            expandedRect.setBottom(rect.bottom()+bottom)
            expandedRect.setLeft(rect.left()-left)
            expandedRect.setRight(rect.right()+right)
        self.d_data.textEngine.draw(painter, expandedRect,
                                    self.d_data.renderFlags, self.d_data.text)
        painter.restore()
    
    def textEngine(self, *args):
        return self._dict.textEngine(*args)
    
    def setTextEngine(self, format_, engine):
        self._dict.setTextEngine(format_, engine)


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
            self.d_data.text = text
    
    def init(self):
        self.d_data = QwtTextLabel_PrivateData()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    
    def setPlainText(self, text):
        self.setText(QwtText(text))
        
    def plainText(self):
        return self.d_data.text.text()
    
    def setText(self, text, textFormat=QwtText.AutoText):
        if isinstance(text, QwtText):
            self.d_data.text = text
        else:
            self.d_data.text.setText(text, textFormat)
        self.update()
        self.updateGeometry()
    
    def text(self):
        return self.d_data.text
        
    def clear(self):
        self.d_data.text = QwtText()
        self.update()
        self.updateGeometry()
    
    def indent(self):
        return self.d_data.indent
    
    def setIdent(self, indent):
        if indent < 0:
            indent = 0
        self.d_data.indent = indent
        self.update()
        self.updateGeometry()
    
    def margin(self, margin):
        return self.d_data.margin
        
    def setMargin(self, margin):
        self.d_data.margin = margin
        self.update()
        self.updateGeometry()
    
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def minimumSizeHint(self):
        sz = self.d_data.text.textSize(self.font())
        mw = 2*(self.frameWidth()+self.d_data.margin)
        mh = mw
        indent = self.d_data.indent
        if indent <= 0:
            indent = self.defaultIndent()
        if indent > 0:
            align = self.d_data.text.renderFlags()
            if align & Qt.AlignLeft or align & Qt.AlignRight:
                mw += self.d_data.indent
            elif align & Qt.AlignTop or align & Qt.AlignBottom:
                mh += self.d_data.indent
        sz += QSizeF(mw, mh)
        return QSize(math.ceil(sz.width()), math.ceil(sz.height()))

    def heightForWidth(self, width):
        renderFlags = self.d_data.text.renderFlags()
        indent = self.d_data.indent
        if indent <= 0:
            indent = self.defaultIndent()
        width -= 2*self.frameWidth()
        if renderFlags & Qt.AlignLeft or renderFlags & Qt.AlignRight:
            width -= indent
        height = math.ceil(self.d_data.text.heightForWidth(width, self.font()))
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
        self.d_data.text.draw(painter, textRect)
    
    def textRect(self):
        r = self.contentsRect()
        if not r.isEmpty() and self.d_data.margin > 0:
            r.setRect(r.x()+self.d_data.margin, r.y()+self.d_data.margin,
                      r.width()-2*self.d_data.margin,
                      r.height()-2*self.d_data.margin)
        if not r.isEmpty():
            indent = self.d_data.indent
            if indent <= 0:
                indent = self.defaultIndent()
            if indent > 0:
                renderFlags = self.d_data.text.renderFlags()
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
        if self.d_data.text.testPaintAttribute(QwtText.PaintUsingTextFont):
            fnt = self.d_data.text.font()
        else:
            fnt = self.font()
        return QFontMetrics(fnt).width('x')/2
