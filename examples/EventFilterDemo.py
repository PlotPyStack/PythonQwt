#!/usr/bin/env python

# The Python version of qwt-*/examples/event_filter


import sys
from PyQt4 import Qt
#import PyQt4.Qwt5 as Qwt
import qwt as Qwt
from PyQt4.Qwt5.anynumpy import *


class ColorBar(Qt.QWidget):

    def __init__(self, orientation, *args):
        Qt.QWidget.__init__(self, *args)
        self.__orientation = orientation
        self.__light = Qt.QColor(Qt.Qt.white)
        self.__dark = Qt.QColor(Qt.Qt.black)
        self.setCursor(Qt.Qt.PointingHandCursor)

    # __init__()
    
    def setOrientation(self, orientation):
        self.__orientation = orientation
        self.update()

    # setOrientation()
    
    def orientation(self):
        return self.__orientation

    # orientation()
    
    def setRange(self, light, dark):
        self.__light = light
        self.__dark = dark
        self.update()

    # setRange()
    
    def setLight(self, color):
        self.__light = color
        self.update()

    # setLight()
    
    def setDark(self, color):
        self.__dark = color
        self.update()

    # setDark()
    
    def light(self):
        return self.__light

    # light()
    
    def dark(self):
        return self.__dark

    # dark()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.Qt.LeftButton:
            pm = Qt.QPixmap.grabWidget(self)
            color = Qt.QColor()
            color.setRgb(pm.toImage().pixel(event.x(), event.y()))
            self.emit(Qt.SIGNAL("colorSelected"), color)
            event.accept()

    # mousePressEvent()

    def paintEvent(self, _):
        painter = Qt.QPainter(self)
        self.drawColorBar(painter, self.rect())

    # paintEvent()

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

    # drawColorBar()

# class ColorBar


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

#        self.__wheel = Qwt.QwtWheel(self.canvas())
#        self.__wheel.setOrientation(Qt.Qt.Vertical)
#        self.__wheel.setRange(-100, 100)
#        self.__wheel.setValue(0.0)
#        self.__wheel.setMass(0.2)
#        self.__wheel.setTotalAngle(4 * 360.0)
#
#        self.connect(self.__wheel,
#                     Qt.SIGNAL('valueChanged(double)'),
#                     self.scrollLeftAxis)

        # we need the resize events, to lay out the wheel
        self.canvas().installEventFilter(self)

        scaleWidget.setWhatsThis(
            'Selecting a value at the scale will insert a new curve.')
        self.__colorBar.setWhatsThis(
            'Selecting a color will change the background of the plot.')
#        self.__wheel.setWhatsThis(
#            'With the wheel you can move the visible area.')
        self.axisWidget(Qwt.QwtPlot.xBottom).setWhatsThis(
            'Selecting a value at the scale will insert a new curve.')

    # __init__()
    
    def setCanvasColor(self, color):
        self.setCanvasBackground(color)
        self.replot()

    # setCanvasColor()

    def scrollLeftAxis(self, value):
        self.setAxisScale(Qwt.QwtPlot.yLeft, value, value + 100)
        self.replot()

    # scrollLeftAxis()

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
            elif object == self.canvas():
                w, h, margin = 16, 50, 2
                r = object.contentsRect();
#                self.__wheel.setGeometry(
#                    r.right() - margin - w, r.center().y() - h / 2, w, h)

        return Qwt.QwtPlot.eventFilter(self, object, event)

    # eventFilter()

    def insertCurve(self, axis, base):
        if axis == Qwt.QwtPlot.yLeft or axis == Qwt.QwtPlot.yRight:
            o = Qt.Qt.Horizontal
        else:
            o = Qt.Qt.Vertical
            
        self.__insertCurve(o, Qt.QColor(Qt.Qt.red), base)
        self.replot()

    # insertCurve()

    def __insertCurve(self, orientation, color, base):
        curve = Qwt.QwtPlotCurve()
        curve.attach(self)

        curve.setPen(Qt.QPen(color))
        curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                      Qt.QBrush(Qt.Qt.gray),
                                      Qt.QPen(color),
                                      Qt.QSize(8, 8)))

        fixed = base*ones(10, Float)
        changing = arange(0, 95.0, 10.0, Float) + 5.0
        if orientation == Qt.Qt.Horizontal:
            curve.setData(changing, fixed)
        else:
            curve.setData(fixed, changing)

    # __insertCurve()

# class Plot


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

    # __init__()

    def event(self, event):
        if event.type() == Qt.QEvent.User:
            self.__showCursor(True)
            return True
        return Qt.QObject.event(event)

    # event()
    
    def eventFilter(self, object, event):
        
        if event.type() == Qt.QEvent.FocusIn:
            self.__showCursor(True)
        if event.type() == Qt.QEvent.FocusOut:
            self.__showCursor(False)
         
        if event.type() == Qt.QEvent.Paint:
            Qt.QApplication.postEvent(
                self, Qt.QEvent(Qt.QEvent.User))
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
        
        return Qwt.QwtPlot.eventFilter(self, object, event)

    # eventFilter()

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

    # __select()

    def __moveBy(self, dx, dy):
        if dx == 0 and dy == 0:
            return

        curve = self.__selectedCurve
        if not curve:
            return

        x = self.__plot.transform(
            curve.xAxis(), curve.x(self.__selectedPoint)) + dx
        y = self.__plot.transform(
            curve.yAxis(), curve.y(self.__selectedPoint)) + dy
        self.__move(Qt.QPoint(x, y))

    # __moveBy()

    def __move(self, pos):
        curve = self.__selectedCurve
        if not curve:
            return

        xData = zeros(curve.dataSize(), Float)
        yData = zeros(curve.dataSize(), Float)

        for i in range(curve.dataSize()):
            if i == self.__selectedPoint:
                xData[i] = self.__plot.invTransform(curve.xAxis(), pos.x())
                yData[i] = self.__plot.invTransform(curve.yAxis(), pos.y())
            else:
                xData[i] = curve.x(i)
                yData[i] = curve.y(i)
            
        curve.setData(xData, yData)
        self.__plot.replot()
        self.__showCursor(True)

    # __move()

    def __showCursor(self, showIt):
        curve = self.__selectedCurve
        if not curve:
            return

        # Use copy constructors to defeat the reference semantics.
        symbol = Qwt.QwtSymbol(curve.symbol())
        newSymbol = Qwt.QwtSymbol(symbol)
        if showIt:
            newSymbol.setBrush(symbol.brush().color().dark(150))

        doReplot = self.__plot.autoReplot()

        self.__plot.setAutoReplot(False)
        curve.setSymbol(newSymbol)

#        curve.draw(self.__selectedPoint, self.__selectedPoint)

        curve.setSymbol(symbol)
        self.__plot.setAutoReplot(doReplot)
        
    # __showCursor()
    
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

    # __shiftCurveCursor()

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

    # __shiftPointCursor()
   
# class CanvasPicker


class ScalePicker(Qt.QObject):

    def __init__(self, plot):
        Qt.QObject.__init__(self, plot)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = plot.axisWidget(i)
            if scaleWidget:
                scaleWidget.installEventFilter(self)

    # __init__()

    def eventFilter(self, object, event):
        if (event.type() == Qt.QEvent.MouseButtonPress):
            self.__mouseClicked(object, event.pos())
            return True
        return Qt.QObject.eventFilter(self, object, event)

    # eventFilter()

    def __mouseClicked(self, scale, pos):
        rect = self.__scaleRect(scale)

        margin = 10
        rect.setRect(rect.x() - margin,
                     rect.y() - margin,
                     rect.width() + 2 * margin,
                     rect.height() +  2 * margin)

        if rect.contains(pos):
            value = 0.0
            axis = -1

        sd = scale.scaleDraw()
        if scale.alignment() == Qwt.QwtScaleDraw.LeftScale:
            value = sd.map().invTransform(pos.y())
            axis = Qwt.QwtPlot.yLeft
        elif scale.alignment() == Qwt.QwtScaleDraw.RightScale:
            value = sd.map().invTransform(pos.y())
            axis = Qwt.QwtPlot.yRight
        elif scale.alignment() == Qwt.QwtScaleDraw.BottomScale:
            value = sd.map().invTransform(pos.x())
            axis = Qwt.QwtPlot.xBottom
        elif scale.alignment() == Qwt.QwtScaleDraw.TopScale:
            value = sd.map().invTransform(pos.x())
            axis = Qwt.QwtPlot.xBottom

        self.emit(Qt.SIGNAL("clicked"), axis, value)

    # __mouseClicked()
 
    def __scaleRect(self, scale):
        bld = scale.margin()
        mjt = scale.scaleDraw().majTickLength()
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

    # __scaleRect

# class ScalePicker


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
    Qt.QObject.connect(scalePicker,
                           Qt.SIGNAL("clicked"),
                           plot.insertCurve)

    demo.resize(540, 400)
    demo.show()
    return demo

# make()

def main(args):
    app = Qt.QApplication(args)
    demo = make()
    sys.exit(app.exec_())

# main()

# Admire!
if __name__ == '__main__':
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
