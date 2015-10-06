# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
Text engine
-----------

QwtTextEngine
~~~~~~~~~~~~~

.. autoclass:: QwtTextEngine
   :members:
   
QwtPlainTextEngine
~~~~~~~~~~~~~~~~~~

.. autoclass:: QwtPlainTextEngine
   :members:
   
QwtRichTextEngine
~~~~~~~~~~~~~~~~~

.. autoclass:: QwtRichTextEngine
   :members:
"""

from qwt.painter import QwtPainter

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


class QwtTextEngine(object):
    """
    Abstract base class for rendering text strings

    A text engine is responsible for rendering texts for a
    specific text format. They are used by `QwtText` to render a text.

    `QwtPlainTextEngine` and `QwtRichTextEngine` are part of the 
    `PythonQwt` library.
    The implementation of `QwtMathMLTextEngine` uses code from the 
    `Qt` solution package. Because of license implications it is built into
    a separate library.
 
    .. seealso::
    
        :py:meth:`qwt.text.QwtText.setTextEngine()`
    """
    def __init__(self):
        pass
    
    def heightForWidth(self, font, flags, text, width):
        """
        Find the height for a given width

        :param QFont font: Font of the text
        :param int flags: Bitwise OR of the flags used like in QPainter::drawText
        :param str text: Text to be rendered
        :param float width: Width
        :return: Calculated height
        """
        pass
    
    def textSize(self, font, flags, text):
        """
        Returns the size, that is needed to render text

        :param QFont font: Font of the text
        :param int flags: Bitwise OR of the flags like in for QPainter::drawText
        :param str text: Text to be rendered
        :return: Calculated size
        """
        pass

    def mightRender(self, text):
        """
        Test if a string can be rendered by this text engine

        :param str text: Text to be tested
        :return: True, if it can be rendered
        """
        pass

    def textMargins(self, font):
        """
        Return margins around the texts

        The textSize might include margins around the
        text, like QFontMetrics::descent(). In situations
        where texts need to be aligned in detail, knowing
        these margins might improve the layout calculations.

        :param QFont font: Font of the text
        :return: tuple (left, right, top, bottom) representing margins
        """
        pass

    def draw(self, painter, rect, flags, text):
        """
        Draw the text in a clipping rectangle

        :param QPainter painter: Painter
        :param QRectF rect: Clipping rectangle
        :param int flags: Bitwise OR of the flags like in for QPainter::drawText()
        :param str text: Text to be rendered
        """
        pass


ASCENTCACHE = {}

class QwtPlainTextEngine(QwtTextEngine):
    """
    A text engine for plain texts

    `QwtPlainTextEngine` renders texts using the basic `Qt` classes
    `QPainter` and `QFontMetrics`.
    """
    def __init__(self):
        self.qrectf_max = QRectF(0, 0, QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
        self._fm_cache = {}
        self._fm_cache_f = {}
    
    def fontmetrics(self, font):
        fid = font.toString()
        fm = self._fm_cache.get(fid)
        if fm is None:
            return self._fm_cache.setdefault(fid, QFontMetrics(font))
        else:
            return fm
    
    def fontmetrics_f(self, font):
        fid = font.toString()
        fm = self._fm_cache_f.get(fid)
        if fm is None:
            return self._fm_cache_f.setdefault(fid, QFontMetricsF(font))
        else:
            return fm
    
    def heightForWidth(self, font, flags, text, width):
        """
        Find the height for a given width

        :param QFont font: Font of the text
        :param int flags: Bitwise OR of the flags used like in QPainter::drawText
        :param str text: Text to be rendered
        :param float width: Width
        :return: Calculated height
        """
        fm = self.fontmetrics_f(font)
        rect = fm.boundingRect(QRectF(0, 0, width, QWIDGETSIZE_MAX),
                               flags, text)
        return rect.height()
    
    def textSize(self, font, flags, text):
        """
        Returns the size, that is needed to render text

        :param QFont font: Font of the text
        :param int flags: Bitwise OR of the flags like in for QPainter::drawText
        :param str text: Text to be rendered
        :return: Calculated size
        """
        fm = self.fontmetrics_f(font)
        rect = fm.boundingRect(self.qrectf_max, flags, text)
        return rect.size()
    
    def effectiveAscent(self, font):
        global ASCENTCACHE
        fontKey = font.key()
        ascent = ASCENTCACHE.get(fontKey)
        if ascent is not None:
            return ascent
        return ASCENTCACHE.setdefault(fontKey, self.findAscent(font))
    
    def findAscent(self, font):
        dummy = "E"
        white = QColor(Qt.white)

        fm = self.fontmetrics(font)
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

    def textMargins(self, font):
        """
        Return margins around the texts

        The textSize might include margins around the
        text, like QFontMetrics::descent(). In situations
        where texts need to be aligned in detail, knowing
        these margins might improve the layout calculations.

        :param QFont font: Font of the text
        :return: tuple (left, right, top, bottom) representing margins
        """
        left = right = top = 0
        fm = self.fontmetrics_f(font)
        top = fm.ascent() - self.effectiveAscent(font)
        bottom = fm.descent()
        return left, right, top, bottom

    def draw(self, painter, rect, flags, text):
        """
        Draw the text in a clipping rectangle

        :param QPainter painter: Painter
        :param QRectF rect: Clipping rectangle
        :param int flags: Bitwise OR of the flags like in for QPainter::drawText()
        :param str text: Text to be rendered
        """
        QwtPainter.drawText(painter, rect, flags, text)
    
    def mightRender(self, text):
        """
        Test if a string can be rendered by this text engine

        :param str text: Text to be tested
        :return: True, if it can be rendered
        """
        return True


class QwtRichTextEngine(QwtTextEngine):
    """
    A text engine for `Qt` rich texts

    `QwtRichTextEngine` renders `Qt` rich texts using the classes
    of the Scribe framework of `Qt`.
    """
    def __init__(self):
        pass
    
    def heightForWidth(self, font, flags, text, width):
        """
        Find the height for a given width

        :param QFont font: Font of the text
        :param int flags: Bitwise OR of the flags used like in QPainter::drawText
        :param str text: Text to be rendered
        :param float width: Width
        :return: Calculated height
        """
        doc = QwtRichTextDocument(text, flags, font)
        doc.setPageSize(QSizeF(width, QWIDGETSIZE_MAX))
        return doc.documentLayout().documentSize().height()
    
    def textSize(self, font, flags, text):
        """
        Returns the size, that is needed to render text

        :param QFont font: Font of the text
        :param int flags: Bitwise OR of the flags like in for QPainter::drawText
        :param str text: Text to be rendered
        :return: Calculated size
        """
        doc = QwtRichTextDocument(text, flags, font)
        option = doc.defaultTextOption()
        if option.wrapMode() != QTextOption.NoWrap:
            option.setWrapMode(QTextOption.NoWrap)
            doc.setDefaultTextOption(option)
            doc.adjustSize()
        return doc.size()
    
    def draw(self, painter, rect, flags, text):
        """
        Draw the text in a clipping rectangle

        :param QPainter painter: Painter
        :param QRectF rect: Clipping rectangle
        :param int flags: Bitwise OR of the flags like in for QPainter::drawText()
        :param str text: Text to be rendered
        """
        doc = QwtRichTextDocument(text, flags, painter.font())
        QwtPainter.drawSimpleRichText(painter, rect, flags, doc)
    
    def taggedText(self, text, flags):
        return self.taggedRichText(text,flags)

    def mightRender(self, text):
        """
        Test if a string can be rendered by this text engine

        :param str text: Text to be tested
        :return: True, if it can be rendered
        """
        return Qt.mightBeRichText(text)
    
    def textMargins(self, font):
        """
        Return margins around the texts

        The textSize might include margins around the
        text, like QFontMetrics::descent(). In situations
        where texts need to be aligned in detail, knowing
        these margins might improve the layout calculations.

        :param QFont font: Font of the text
        :return: tuple (left, right, top, bottom) representing margins
        """
        return 0, 0, 0, 0
