# -*- coding: utf-8 -*-

from qwt.qwt_plot import QwtPlotItem
from qwt.qwt_text import QwtText
from qwt.qwt_painter import QwtPainter
from qwt.qwt_graphic import QwtGraphic

from qwt.qt.QtGui import QPen, QPainter
from qwt.qt.QtCore import Qt, QPointF, QRectF, QSizeF, QRect


class QwtPlotMarker_PrivateData(object):
    def __init__(self):
        self.labelAlignment = Qt.AlignCenter
        self.labelOrientation = Qt.Horizontal
        self.spacing = 2
        self.symbol = None
        self.style = QwtPlotMarker.NoLine
        self.xValue = 0.
        self.yValue = 0.
        self.label = QwtText()
        self.pen = QPen()


class QwtPlotMarker(QwtPlotItem):
    
    # enum LineStyle
    NoLine, HLine, VLine, Cross = range(4)
    
    
    def __init__(self, title=None):
        if title is None:
            title = ""
        if not isinstance(title, QwtText):
            title = QwtText(title)
        QwtPlotItem.__init__(self, title)
        self.__data = QwtPlotMarker_PrivateData()
        self.setZ(30.)
        
    def rtti(self):
        return QwtPlotItem.Rtti_PlotMarker
    
    def value(self):
        return QPointF(self.__data.xValue, self.__data.yValue)
    
    def xValue(self):
        return self.__data.xValue
    
    def yValue(self):
        return self.__data.yValue
    
    def setValue(self, *args):
        if len(args) == 1:
            pos, = args
            self.setValue(pos.x(), pos.y())
        elif len(args) == 2:
            x, y = args
            if x != self.__data.xValue or y != self.__data.yValue:
                self.__data.xValue = x
                self.__data.yValue = y
                self.itemChanged()
        else:
            raise TypeError("%s() takes 1 or 2 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))

    def setXValue(self, x):
        self.setValue(x, self.__data.yValue)
    
    def setYValue(self, y):
        self.setValue(self.__data.xValue, y)
    
    def draw(self, painter, xMap, yMap, canvasRect):
        pos = QPointF(xMap.transform(self.__data.xValue),
                      yMap.transform(self.__data.yValue))
        self.drawLines(painter, canvasRect, pos)
        if self.__data.symbol and\
           self.__data.symbol.style() != QwtSymbol.NoSymbol:
            sz = self.__data.symbol.size()
            clipRect = QRectF(canvasRect.adjusted(-sz.width(), -sz.height(),
                                                  sz.width(), sz.height()))
            if clipRect.contains(pos):
                self.__data.symbol.drawSymbol(painter, pos)
        self.drawLabel(painter, canvasRect, pos)
    
    def drawLines(self, painter, canvasRect, pos):
        if self.__data.style == self.NoLine:
            return
        doAlign = QwtPainter().roundingAlignment(painter)
        painter.setPen(self.__data.pen)
        if self.__data.style in (QwtPlotMarker.HLine, QwtPlotMarker.Cross):
            y = pos.y()
            if doAlign:
                y = round(y)
            QwtPainter().drawLine(painter, canvasRect.left(),
                                  y, canvasRect.right()-1., y)
        if self.__data.style in (QwtPlotMarker.VLine, QwtPlotMarker.Cross):
            x = pos.x()
            if doAlign:
                x = round(x)
            QwtPainter().drawLine(painter, x,
                                  canvasRect.top(), x, canvasRect.bottom()-1.)
    
    def drawLabel(self, painter, canvasRect, pos):
        if self.__data.label.isEmpty():
            return
        align = Qt.Alignment(self.__data.labelAlignment)
        alignPos = QPointF(pos)
        symbolOff = QSizeF(0, 0)
        if self.__data.style == QwtPlotMarker.VLine:
            if bool(self.__data.labelAlignment & Qt.AlignTop):
                alignPos.setY(canvasRect.top())
                align &= ~Qt.AlignTop
                align |= Qt.AlignBottom
            elif bool(self.__data.labelAlignment & Qt.AlignBottom):
                alignPos.setY(canvasRect.bottom()-1)
                align &= ~Qt.AlignBottom
                align |= Qt.AlignTop
            else:
                alignPos.setY(canvasRect.center().y())
        elif self.__data.style == QwtPlotMarker.HLine:
            if bool(self.__data.labelAlignment & Qt.AlignLeft):
                alignPos.setX(canvasRect.left())
                align &= ~Qt.AlignLeft
                align |= Qt.AlignRight
            elif bool(self.__data.labelAlignment & Qt.AlignRight):
                alignPos.setX(canvasRect.right()-1)
                align &= ~Qt.AlignRight
                align |= Qt.AlignLeft
            else:
                alignPos.setX(canvasRect.center().x())
        else:
            if self.__data.symbol and\
               self.__data.symbol.style() != QwtSymbol.NoSymbol:
                symbolOff = self.__data.symbol.size()+QSizeF(1, 1)
                symbolOff /= 2
        pw2 = self.__data.pen.widthF()/2.
        if pw2 == 0.:
            pw2 = .5
        spacing = self.__data.spacing
        xOff = max([pw2, symbolOff.width()])
        yOff = max([pw2, symbolOff.height()])
        textSize = self.__data.label.textSize(painter.font())
        if align & Qt.AlignLeft:
            alignPos.setX(alignPos.x()-(xOff+spacing))
            if self.__data.labelOrientation == Qt.Vertical:
                alignPos.setX(alignPos.x()-textSize.height())
            else:
                alignPos.setX(alignPos.x()-textSize.width())
        elif align & Qt.AlignRight:
            alignPos.setX(alignPos.x()+xOff+spacing)
        else:
            if self.__data.labelOrientation == Qt.Vertical:
                alignPos.setX(alignPos.x()-textSize.height()/2)
            else:
                alignPos.setX(alignPos.x()-textSize.width()/2)
        if align & Qt.AlignTop:
            alignPos.setY(alignPos.y()-(yOff+spacing))
            if self.__data.labelOrientation != Qt.Vertical:
                alignPos.setY(alignPos.y()-textSize.height())
        elif align & Qt.AlignBottom:
            alignPos.setY(alignPos.y()+yOff+spacing)
            if self.__data.labelOrientation == Qt.Vertical:
                alignPos.setY(alignPos.y()+textSize.width())
        else:
            if self.__data.labelOrientation == Qt.Vertical:
                alignPos.setY(alignPos.y()+textSize.width()/2)
            else:
                alignPos.setY(alignPos.y()-textSize.height()/2)
        painter.translate(alignPos.x(), alignPos.y())
        if self.__data.labelOrientation == Qt.Vertical:
            painter.rotate(-90.)
        textRect = QRectF(0, 0, textSize.width(), textSize.height())
        self.__data.label.draw(painter, textRect)
    
    def setLineStyle(self, style):
        if style != self.__data.style:
            self.__data.style = style
            self.legendChanged()
            self.itemChanged()
    
    def lineStyle(self):
        return self.__data.style
            
    def setSymbol(self, symbol):
        if symbol != self.__data.symbol:
            self.__data.symbol = symbol
            if symbol is not None:
                self.setLegendIconSize(symbol.boundingRect().size())
            self.legendChanged()
            self.itemChanged()
    
    def symbol(self):
        return self.__data.symbol
    
    def setLabel(self, label):
        if label != self.__data.label:
            self.__data.label = label
            self.itemChanged()
    
    def label(self):
        return self.__data.label
    
    def setLabelAlignment(self, align):
        if align != self.__data.labelAlignment:
            self.__data.labelAlignment = align
            self.itemChanged()
    
    def labelAlignment(self):
        return self.__data.labelAlignment
    
    def setLabelOrientation(self, orientation):
        if orientation != self.__data.labelOrientation:
            self.__data.labelOrientation = orientation
            self.itemChanged()
    
    def labelOrientation(self):
        return self.__data.labelOrientation
    
    def setSpacing(self, spacing):
        if spacing < 0:
            spacing = 0
        if spacing != self.__data.spacing:
            self.__data.spacing = spacing
            self.itemChanged()
    
    def spacing(self):
        return self.__data.spacing

    
    def setLinePen(self, *args):
        if len(args) == 1 and isinstance(args[0], QPen):
            pen, = args
        elif len(args) in (1, 2, 3):
            color = args[0]
            width = 0.
            style = Qt.SolidLine
            if len(args) > 1:
                width = args[1]
                if len(args) > 2:
                    style = args[2]
            self.setLinePen(QPen(color, width, style))
        else:
            raise TypeError("%s().setLinePen() takes 1, 2 or 3 argument(s) "\
                            "(%s given)" % (self.__class__.__name__, len(args)))
        if pen != self.__data.pen:
            self.__data.pen = pen
            self.legendChanged()
            self.itemChanged()
    
    def linePen(self):
        return self.__data.pen

    def boundingRect(self):
        return QRectF(self.__data.xValue, self.__data.yValue, 0., 0.)
    
    def legendIcon(self, index, size):
        if size.isEmpty():
            return QwtGraphic()
        icon = QwtGraphic()
        icon.setDefaultSize(size)
        icon.setRenderHint(QwtGraphic.RenderPensUnscaled, True)
        painter = QPainter(icon)
        painter.setRenderHint(QPainter.Antialiasing,
                          self.testRenderHint(QwtPlotItem.RenderAntialiased))
        if self.__data.style != QwtPlotMarker.NoLine:
            painter.setPen(self.__data.pen)
            if self.__data.style in (QwtPlotMarker.HLine, QwtPlotMarker.Cross):
                y = .5*size.height()
                QwtPainter().drawLine(painter, 0., y, size.width(), y)
            if self.__data.style in (QwtPlotMarker.VLine, QwtPlotMarker.Cross):
                x = .5*size.width()
                QwtPainter().drawLine(painter, x, 0., x, size.height())
        if self.__data.symbol:
            r = QRect(0, 0, size.width(), size.height())
            self.__data.symbol.drawSymbol(painter, r)
        return icon
