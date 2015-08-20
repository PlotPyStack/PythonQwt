#!/usr/bin/env python

import sys
from PyQt4 import Qt
import qwt as Qwt
import numpy as np


class ColorBar(Qt.QWidget):
    def __init__(self, orientation, *args):
        Qt.QWidget.__init__(self, *args)
        self.__orientation = orientation
        self.__light = Qt.QColor(Qt.Qt.white)
        self.__dark = Qt.QColor(Qt.Qt.black)
        self.setCursor(Qt.Qt.PointingHandCursor)
    
    def setOrientation(self, orientation):
        self.__orientation = orientation
        self.update()
    
    def orientation(self):
        return self.__orientation
    
    def setRange(self, light, dark):
        self.__light = light
        self.__dark = dark
        self.update()
    
    def setLight(self, color):
        self.__light = color
        self.update()
    
    def setDark(self, color):
        self.__dark = color
        self.update()
    
    def light(self):
        return self.__light
    
    def dark(self):
        return self.__dark
    
    def mousePressEvent(self, event):
        if event.button() == Qt.Qt.LeftButton:
            pm = Qt.QPixmap.grabWidget(self)
            color = Qt.QColor()
            color.setRgb(pm.toImage().pixel(event.x(), event.y()))
            self.emit(Qt.SIGNAL("colorSelected"), color)
            event.accept()

    def paintEvent(self, _):
        painter = Qt.QPainter(self)
        self.drawColorBar(painter, self.rect())

    def drawColorBar(self, painter, rect):
        h1, s1, v1, _ = self.__light.getHsv()
        h2, s2, v2, _ = self.__dark.getHsv()
        painter.save()
        painter.setClipRect(rect)
        painter.setClipping(True)
        painter.fillRect(rect, Qt.QBrush(self.__dark))
        sectionSize = 2
        if (self.__orientation == Qt.Qt.Horizontal):
            numIntervals = rect.width()/sectionSize
        else:
            numIntervals = rect.height()/sectionSize
        section = Qt.QRect()
        for i in range(int(numIntervals)):
            if self.__orientation == Qt.Qt.Horizontal:
                section.setRect(rect.x() + i*sectionSize, rect.y(),
                                sectionSize, rect.heigh())
            else:
                section.setRect(rect.x(), rect.y() + i*sectionSize,
                                rect.width(), sectionSize)
            ratio = float(i)/float(numIntervals)
            color = Qt.QColor()
            color.setHsv(h1 + int(ratio*(h2-h1) + 0.5),
                         s1 + int(ratio*(s2-s1) + 0.5),
                         v1 + int(ratio*(v2-v1) + 0.5))            
            painter.fillRect(section, color)
        painter.restore()


class Plot(Qwt.QwtPlot):
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)

        self.setTitle("Interactive Plot")
        
        self.setCanvasColor(Qt.Qt.darkCyan)

        grid = Qwt.QwtPlotGrid()
        grid.attach(self)
        grid.setMajorPen(Qt.QPen(Qt.Qt.white, 0, Qt.Qt.DotLine))
        
        self.setAxisScale(Qwt.QwtPlot.xBottom, 0.0, 100.0)
        self.setAxisScale(Qwt.QwtPlot.yLeft, 0.0, 100.0)

        # Avoid jumping when label with 3 digits
        # appear/disappear when scrolling vertically
        scaleDraw = self.axisScaleDraw(Qwt.QwtPlot.yLeft)
        scaleDraw.setMinimumExtent(scaleDraw.extent(
            self.axisWidget(Qwt.QwtPlot.yLeft).font()))

        self.plotLayout().setAlignCanvasToScales(True)

        self.__insertCurve(Qt.Qt.Vertical, Qt.Qt.blue, 30.0)
        self.__insertCurve(Qt.Qt.Vertical, Qt.Qt.magenta, 70.0)
        self.__insertCurve(Qt.Qt.Horizontal, Qt.Qt.yellow, 30.0)
        self.__insertCurve(Qt.Qt.Horizontal, Qt.Qt.white, 70.0)
        
        self.replot()

        scaleWidget = self.axisWidget(Qwt.QwtPlot.yLeft)
        scaleWidget.setMargin(10)

        self.__colorBar = ColorBar(Qt.Qt.Vertical, scaleWidget)
        self.__colorBar.setRange(
            Qt.QColor(Qt.Qt.red), Qt.QColor(Qt.Qt.darkBlue))
        self.__colorBar.setFocusPolicy(Qt.Qt.TabFocus)

        self.connect(self.__colorBar,
                     Qt.SIGNAL('colorSelected'),
                     self.setCanvasColor)
        
        # we need the resize events, to lay out the color bar
        scaleWidget.installEventFilter(self)

        # we need the resize events, to lay out the wheel
        self.canvas().installEventFilter(self)

        scaleWidget.setWhatsThis(
            'Selecting a value at the scale will insert a new curve.')
        self.__colorBar.setWhatsThis(
            'Selecting a color will change the background of the plot.')
        self.axisWidget(Qwt.QwtPlot.xBottom).setWhatsThis(
            'Selecting a value at the scale will insert a new curve.')
    
    def setCanvasColor(self, color):
        self.setCanvasBackground(color)
        self.replot()

    def scrollLeftAxis(self, value):
        self.setAxisScale(Qwt.QwtPlot.yLeft, value, value + 100)
        self.replot()

    def eventFilter(self, object, event):
        if event.type() == Qt.QEvent.Resize:
            size = event.size()
            if object == self.axisWidget(Qwt.QwtPlot.yLeft):
                margin = 2
                x = size.width() - object.margin() + margin
                w = object.margin() - 2 * margin
                y = object.startBorderDist()
                h = (size.height()
                     - object.startBorderDist() - object.endBorderDist())
                self.__colorBar.setGeometry(x, y, w, h)
        return Qwt.QwtPlot.eventFilter(self, object, event)

    def insertCurve(self, axis, base):
        if axis == Qwt.QwtPlot.yLeft or axis == Qwt.QwtPlot.yRight:
            o = Qt.Qt.Horizontal
        else:
            o = Qt.Qt.Vertical
        self.__insertCurve(o, Qt.QColor(Qt.Qt.red), base)
        self.replot()

    def __insertCurve(self, orientation, color, base):
        curve = Qwt.QwtPlotCurve()
        curve.attach(self)
        curve.setPen(Qt.QPen(color))
        curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                      Qt.QBrush(Qt.Qt.gray),
                                      Qt.QPen(color),
                                      Qt.QSize(8, 8)))
        fixed = base*np.ones(10, np.float)
        changing = np.arange(0, 95.0, 10.0, np.float) + 5.0
        if orientation == Qt.Qt.Horizontal:
            curve.setData(changing, fixed)
        else:
            curve.setData(fixed, changing)


class CanvasPicker(Qt.QObject):
    def __init__(self, plot):
        Qt.QObject.__init__(self, plot)
        self.__selectedCurve = None
        self.__selectedPoint = -1
        self.__plot = plot
        canvas = plot.canvas()
        canvas.installEventFilter(self)        
        # We want the focus, but no focus rect.
        # The selected point will be highlighted instead.
        canvas.setFocusPolicy(Qt.Qt.StrongFocus)
        canvas.setCursor(Qt.Qt.PointingHandCursor)
        canvas.setFocusIndicator(Qwt.QwtPlotCanvas.ItemFocusIndicator)
        canvas.setFocus()        
        canvas.setWhatsThis(
            'All points can be moved using the left mouse button '
            'or with these keys:\n\n'
            '- Up: Select next curve\n'
            '- Down: Select previous curve\n'
            '- Left, "-": Select next point\n'
            '- Right, "+": Select previous point\n'
            '- 7, 8, 9, 4, 6, 1, 2, 3: Move selected point'
            )
        self.__shiftCurveCursor(True)

    def event(self, event):
        if event.type() == Qt.QEvent.User:
            self.__showCursor(True)
            return True
        return Qt.QObject.event(self, event)
    
    def eventFilter(self, object, event):
        if event.type() == Qt.QEvent.FocusIn:
            self.__showCursor(True)
        if event.type() == Qt.QEvent.FocusOut:
            self.__showCursor(False)
        if event.type() == Qt.QEvent.Paint:
            Qt.QApplication.postEvent(self, Qt.QEvent(Qt.QEvent.User))
        elif event.type() == Qt.QEvent.MouseButtonPress:
            self.__select(event.pos())
            return True
        elif event.type() == Qt.QEvent.MouseMove:
            self.__move(event.pos())
            return True
        if event.type() == Qt.QEvent.KeyPress:
            delta = 5
            key = event.key()
            if key == Qt.Qt.Key_Up:
                self.__shiftCurveCursor(True)
                return True
            elif key == Qt.Qt.Key_Down:
                self.__shiftCurveCursor(False)
                return True
            elif key == Qt.Qt.Key_Right or key == Qt.Qt.Key_Plus:
                if self.__selectedCurve:
                    self.__shiftPointCursor(True)
                else:
                    self.__shiftCurveCursor(True)
                return True
            elif key == Qt.Qt.Key_Left or key == Qt.Qt.Key_Minus:
                if self.__selectedCurve:
                    self.__shiftPointCursor(False)
                else:
                    self.__shiftCurveCursor(True)
                return True
            if key == Qt.Qt.Key_1:
                self.__moveBy(-delta, delta)
            elif key == Qt.Qt.Key_2:
                self.__moveBy(0, delta)
            elif key == Qt.Qt.Key_3:
                self.__moveBy(delta, delta)
            elif key == Qt.Qt.Key_4:
                self.__moveBy(-delta, 0)
            elif key == Qt.Qt.Key_6:
                self.__moveBy(delta, 0)
            elif key == Qt.Qt.Key_7:
                self.__moveBy(-delta, -delta)
            elif key == Qt.Qt.Key_8:
                self.__moveBy(0, -delta)
            elif key == Qt.Qt.Key_9:
                self.__moveBy(delta, -delta)
        return Qwt.QwtPlot.eventFilter(self.__plot, object, event)

    def __select(self, pos):
        found, distance, point = None, 1e100, -1
        for curve in self.__plot.itemList():
            if isinstance(curve, Qwt.QwtPlotCurve):
                i, d = curve.closestPoint(pos)
                if d < distance:
                    found = curve
                    point = i
                    distance = d
        self.__showCursor(False)
        self.__selectedCurve = None
        self.__selectedPoint = -1
        if found and distance < 10:
            self.__selectedCurve = found
            self.__selectedPoint = point
            self.__showCursor(True)

    def __moveBy(self, dx, dy):
        if dx == 0 and dy == 0:
            return
        curve = self.__selectedCurve
        if not curve:
            return
        s = curve.sample(self.__selectedPoint)
        x = self.__plot.transform(curve.xAxis(), s.x()) + dx
        y = self.__plot.transform(curve.yAxis(), s.y()) + dy
        self.__move(Qt.QPoint(x, y))

    def __move(self, pos):
        curve = self.__selectedCurve
        if not curve:
            return
        xData = np.zeros(curve.dataSize(), np.float)
        yData = np.zeros(curve.dataSize(), np.float)
        for i in range(curve.dataSize()):
            if i == self.__selectedPoint:
                xData[i] = self.__plot.invTransform(curve.xAxis(), pos.x())
                yData[i] = self.__plot.invTransform(curve.yAxis(), pos.y())
            else:
                s = curve.sample(i)
                xData[i] = s.x()
                yData[i] = s.y()            
        curve.setData(xData, yData)
        self.__showCursor(True)
        self.__plot.replot()

    def __showCursor(self, showIt):
        curve = self.__selectedCurve
        if not curve:
            return
        symbol = curve.symbol()
        brush = symbol.brush()
        if showIt:
            symbol.setBrush(symbol.brush().color().dark(180))
        curve.directPaint(self.__selectedPoint, self.__selectedPoint)
        if showIt:
            symbol.setBrush(brush)
    
    def __shiftCurveCursor(self, up):
        curves = [curve for curve in self.__plot.itemList()
                  if isinstance(curve, Qwt.QwtPlotCurve)]
        if not curves:
            return
        if self.__selectedCurve in curves:
            index = curves.index(self.__selectedCurve)
            if up:
                index += 1
            else:
                index -= 1
            # keep index within [0, len(curves))
            index += len(curves)
            index %= len(curves)
        else:
            index = 0
        self.__showCursor(False)
        self.__selectedPoint = 0
        self.__selectedCurve = curves[index]
        self.__showCursor(True)

    def __shiftPointCursor(self, up):
        curve = self.__selectedCurve
        if not curve:
            return
        if up:
            index = self.__selectedPoint + 1
        else:
            index = self.__selectedPoint - 1
        # keep index within [0, curve.dataSize())
        index += curve.dataSize()
        index %= curve.dataSize()
        if index != self.__selectedPoint:
            self.__showCursor(False)
            self.__selectedPoint = index
            self.__showCursor(True)


class ScalePicker(Qt.QObject):
    def __init__(self, plot):
        Qt.QObject.__init__(self, plot)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = plot.axisWidget(i)
            if scaleWidget:
                scaleWidget.installEventFilter(self)

    def eventFilter(self, object, event):
        if (event.type() == Qt.QEvent.MouseButtonPress):
            self.__mouseClicked(object, event.pos())
            return True
        return Qt.QObject.eventFilter(self, object, event)

    def __mouseClicked(self, scale, pos):
        rect = self.__scaleRect(scale)
        margin = 10
        rect.setRect(rect.x() - margin, rect.y() - margin,
                     rect.width() + 2 * margin, rect.height() +  2 * margin)
        if rect.contains(pos):
            value = 0.0
            axis = -1
        sd = scale.scaleDraw()
        if scale.alignment() == Qwt.QwtScaleDraw.LeftScale:
            value = sd.scaleMap().invTransform(pos.y())
            axis = Qwt.QwtPlot.yLeft
        elif scale.alignment() == Qwt.QwtScaleDraw.RightScale:
            value = sd.scaleMap().invTransform(pos.y())
            axis = Qwt.QwtPlot.yRight
        elif scale.alignment() == Qwt.QwtScaleDraw.BottomScale:
            value = sd.scaleMap().invTransform(pos.x())
            axis = Qwt.QwtPlot.xBottom
        elif scale.alignment() == Qwt.QwtScaleDraw.TopScale:
            value = sd.scaleMap().invTransform(pos.x())
            axis = Qwt.QwtPlot.xBottom
        self.emit(Qt.SIGNAL("clicked"), axis, value)
 
    def __scaleRect(self, scale):
        bld = scale.margin()
        mjt = scale.scaleDraw().tickLength(Qwt.QwtScaleDiv.MajorTick)
        sbd = scale.startBorderDist()
        ebd = scale.endBorderDist()
        if scale.alignment() == Qwt.QwtScaleDraw.LeftScale:
            return Qt.QRect(scale.width() - bld - mjt, sbd,
                                mjt, scale.height() - sbd - ebd)
        elif scale.alignment() == Qwt.QwtScaleDraw.RightScale: 
            return Qt.QRect(bld, sbd,mjt, scale.height() - sbd - ebd)
        elif scale.alignment() == Qwt.QwtScaleDraw.BottomScale:
            return Qt.QRect(sbd, bld, scale.width() - sbd - ebd, mjt)
        elif scale.alignment() == Qwt.QwtScaleDraw.TopScale:
            return Qt.QRect(sbd, scale.height() - bld - mjt,
                                scale.width() - sbd - ebd, mjt)
        else:
            return Qt.QRect()


def make():
    demo = Qt.QMainWindow()
    toolBar = Qt.QToolBar(demo)
    toolBar.addAction(Qt.QWhatsThis.createAction(toolBar))
    demo.addToolBar(toolBar)
    plot = Plot(demo)
    demo.setCentralWidget(plot)
    plot.setWhatsThis(
        'An useless plot to demonstrate how to use event filtering.\n\n'
        'You can click on the color bar, the scales or move the slider.\n'
        'All points can be moved using the mouse or the keyboard.'
        )
    CanvasPicker(plot)
    scalePicker = ScalePicker(plot)
    Qt.QObject.connect(scalePicker, Qt.SIGNAL("clicked"), plot.insertCurve)
    demo.resize(540, 400)
    demo.show()
    return demo


if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    demo = make()
    sys.exit(app.exec_())
