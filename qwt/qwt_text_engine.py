# -*- coding: utf-8 -*-

from qwt.qwt_painter import QwtPainter

from qwt.qt.QtGui import (QTextDocument, QTextOption, QColor, QFontMetricsF,
                          QPixmap, QPainter, QFontMetrics)
from qwt.qt.QtCore import Qt, QRectF, QSizeF

import struct

QWIDGETSIZE_MAX = (1<<24)-1


def taggedRichText(text, flags):
    richText = text
    if flags & Qt.AlignJustify:
        richText = "<div align=\"justify\">" + richText + "</div>"
    elif flags & Qt.AlignRight:
        richText = "<div align=\"right\">" + richText + "</div>"
    elif flags & Qt.AlignHCenter:
        richText = "<div align=\"center\">" + richText + "</div>"
    return richText


class QwtRichTextDocument(QTextDocument):
    def __init__(self, text, flags, font):
        super(QwtRichTextDocument, self).__init__(None)
        self.setUndoRedoEnabled(False)
        self.setDefaultFont(font)
        self.setHtml(text)
        
        option = self.defaultTextOption()
        if flags & Qt.TextWordWrap:
            option.setWrapMode(QTextOption.WordWrap)
        else:
            option.setWrapMode(QTextOption.NoWrap)
        
        option.setAlignment(flags)
        self.setDefaultTextOption(option)
        
        root = self.rootFrame()
        fm = root.frameFormat()
        fm.setBorder(0)
        fm.setMargin(0)
        fm.setPadding(0)
        fm.setBottomMargin(0)
        fm.setLeftMargin(0)
        root.setFrameFormat(fm)

        self.adjustSize();


class QwtPlainTextEngine_PrivateData(object):
    def __init__(self):
        self.d_ascentCache = {}
    
    def effectiveAscent(self, font):
        fontKey = font.key()
        return self.d_ascentCache.get(fontKey, self.findAscent(font))
    
    def findAscent(self, font):
        dummy = "E"
        white = QColor(Qt.white)

        fm = QFontMetrics(font)
        pm = QPixmap(fm.width(dummy), fm.height())
        pm.fill(white)
        
        p = QPainter(pm)
        p.setFont(font)
        p.drawText(0, 0, pm.width(), pm.height(), 0, dummy)
        p.end()
        
        img = pm.toImage()
        
        w = pm.width()
        linebytes = w*4
        for row in range(img.height()):
            line = img.scanLine(row).asstring(linebytes)
            for col in range(w):
                color = struct.unpack('I', line[col*4:(col+1)*4])[0]
                if color != white.rgb():
                    return fm.ascent()-row+1
        return fm.ascent()


class QwtTextEngine(object):
    def __init__(self):
        pass


class QwtPlainTextEngine(QwtTextEngine):
    def __init__(self):
        self.d_data = QwtPlainTextEngine_PrivateData()
    
    def heightForWidth(self, font, flags, text, width):
        fm = QFontMetricsF(font)
        rect = fm.boundingRect(QRectF(0, 0, width, QWIDGETSIZE_MAX),
                               flags, text)
        return rect.height()
    
    def textSize(self, font, flags, text):
        fm = QFontMetricsF(font)
        rect = fm.boundingRect(QRectF(0, 0, QWIDGETSIZE_MAX, QWIDGETSIZE_MAX),
                               flags, text)
        return rect.size()
    
    def textMargins(self, font):
        left = right = top = 0
        fm = QFontMetricsF(font)
        top = fm.ascent() - self.d_data.effectiveAscent(font)
        bottom = fm.descent()
        return left, right, top, bottom

    def draw(self, painter, rect, flags, text):
        QwtPainter().drawText(painter, rect, flags, text)
    
    def mightRender(self, text):
        return True


class QwtRichTextEngine(QwtTextEngine):
    def __init__(self):
        pass
    
    def heightForWidth(self, font, flags, text, width):
        doc = QwtRichTextDocument(text, flags, font)
        doc.setPageSize(QSizeF(width, QWIDGETSIZE_MAX))
        return doc.documentLayout().documentSize().height()
    
    def textSize(self, font, flags, text):
        doc = QwtRichTextDocument(text, flags, font)
        option = doc.defaultTextOption()
        if option.wrapMode() != QTextOption.NoWrap:
            option.setWrapMode(QTextOption.NoWrap)
            doc.setDefaultTextOption(option)
            doc.adjustSize()
        return doc.size()
    
    def draw(self, painter, rect, flags, text):
        doc = QwtRichTextDocument(text, flags, painter.font())
        QwtPainter().drawSimpleRichText(painter, rect, flags, doc)
    
    def taggedText(self, text, flags):
        return self.taggedRichText(text,flags)

    def mightRender(self, text):
        return Qt.mightBeRichText(text)
    
    def textMargins(self, font):
        return 0, 0, 0, 0
