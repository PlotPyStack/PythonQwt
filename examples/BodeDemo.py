#!/usr/bin/env python

# The Python version of Qwt-5.1.1/examples/bode

# To get an impression of the expressive power of NumPy,
# compare the Python and C++ versions of setDamp()

# BodeDemo.py requires at least Python v2.6.
from __future__ import unicode_literals

import sys
from PyQt4.Qt import *
#from PyQt4.Qwt5 import *
from qwt import *
import PyQt4.Qwt5.anynumpy as np


print_xpm = ['32 32 12 1',
             'a c #ffffff',
             'h c #ffff00',
             'c c #ffffff',
             'f c #dcdcdc',
             'b c #c0c0c0',
             'j c #a0a0a4',
             'e c #808080',
             'g c #808000',
             'd c #585858',
             'i c #00ff00',
             '# c #000000',
             '. c None',
             '................................',
             '................................',
             '...........###..................',
             '..........#abb###...............',
             '.........#aabbbbb###............',
             '.........#ddaaabbbbb###.........',
             '........#ddddddaaabbbbb###......',
             '.......#deffddddddaaabbbbb###...',
             '......#deaaabbbddddddaaabbbbb###',
             '.....#deaaaaaaabbbddddddaaabbbb#',
             '....#deaaabbbaaaa#ddedddfggaaad#',
             '...#deaaaaaaaaaa#ddeeeeafgggfdd#',
             '..#deaaabbbaaaa#ddeeeeabbbbgfdd#',
             '.#deeefaaaaaaa#ddeeeeabbhhbbadd#',
             '#aabbbeeefaaa#ddeeeeabbbbbbaddd#',
             '#bbaaabbbeee#ddeeeeabbiibbadddd#',
             '#bbbbbaaabbbeeeeeeabbbbbbaddddd#',
             '#bjbbbbbbaaabbbbeabbbbbbadddddd#',
             '#bjjjjbbbbbbaaaeabbbbbbaddddddd#',
             '#bjaaajjjbbbbbbaaabbbbadddddddd#',
             '#bbbbbaaajjjbbbbbbaaaaddddddddd#',
             '#bjbbbbbbaaajjjbbbbbbddddddddd#.',
             '#bjjjjbbbbbbaaajjjbbbdddddddd#..',
             '#bjaaajjjbbbbbbjaajjbddddddd#...',
             '#bbbbbaaajjjbbbjbbaabdddddd#....',
             '###bbbbbbaaajjjjbbbbbddddd#.....',
             '...###bbbbbbaaajbbbbbdddd#......',
             '......###bbbbbbjbbbbbddd#.......',
             '.........###bbbbbbbbbdd#........',
             '............###bbbbbbd#.........',
             '...............###bbb#..........',
             '..................###...........']

zoom_xpm = ['32 32 8 1',
            '# c #000000',
            'b c #c0c0c0',
            'a c #ffffff',
            'e c #585858',
            'd c #a0a0a4',
            'c c #0000ff',
            'f c #00ffff',
            '. c None',
            '..######################........',
            '.#a#baaaaaaaaaaaaaaaaaa#........',
            '#aa#baaaaaaaaaaaaaccaca#........',
            '####baaaaaaaaaaaaaaaaca####.....',
            '#bbbbaaaaaaaaaaaacccaaa#da#.....',
            '#aaaaaaaaaaaaaaaacccaca#da#.....',
            '#aaaaaaaaaaaaaaaaaccaca#da#.....',
            '#aaaaaaaaaabe###ebaaaaa#da#.....',
            '#aaaaaaaaa#########aaaa#da#.....',
            '#aaaaaaaa###dbbbb###aaa#da#.....',
            '#aaaaaaa###aaaaffb###aa#da#.....',
            '#aaaaaab##aaccaaafb##ba#da#.....',
            '#aaaaaae#daaccaccaad#ea#da#.....',
            '#aaaaaa##aaaaaaccaab##a#da#.....',
            '#aaaaaa##aacccaaaaab##a#da#.....',
            '#aaaaaa##aaccccaccab##a#da#.....',
            '#aaaaaae#daccccaccad#ea#da#.....',
            '#aaaaaab##aacccaaaa##da#da#.....',
            '#aaccacd###aaaaaaa###da#da#.....',
            '#aaaaacad###daaad#####a#da#.....',
            '#acccaaaad##########da##da#.....',
            '#acccacaaadde###edd#eda#da#.....',
            '#aaccacaaaabdddddbdd#eda#a#.....',
            '#aaaaaaaaaaaaaaaaaadd#eda##.....',
            '#aaaaaaaaaaaaaaaaaaadd#eda#.....',
            '#aaaaaaaccacaaaaaaaaadd#eda#....',
            '#aaaaaaaaaacaaaaaaaaaad##eda#...',
            '#aaaaaacccaaaaaaaaaaaaa#d#eda#..',
            '########################dd#eda#.',
            '...#dddddddddddddddddddddd##eda#',
            '...#aaaaaaaaaaaaaaaaaaaaaa#.####',
            '...########################..##.']


class BodePlot(QwtPlot):

    def __init__(self, *args):
        QwtPlot.__init__(self, *args)

        self.setTitle('Frequency Response of a 2<sup>nd</sup>-order System')
        self.setCanvasBackground(Qt.darkBlue)

        # legend
        legend = QwtLegend()
        legend.setFrameStyle(QFrame.Box | QFrame.Sunken)
        self.insertLegend(legend, QwtPlot.BottomLegend)

        # grid
        self.grid = QwtPlotGrid()
        self.grid.enableXMin(True)
        self.grid.attach(self)

        # axes
        self.enableAxis(QwtPlot.yRight)
        self.setAxisTitle(QwtPlot.xBottom, '\u03c9/\u03c9<sub>0</sub>')
        self.setAxisTitle(QwtPlot.yLeft, 'Amplitude [dB]')
        self.setAxisTitle(QwtPlot.yRight, 'Phase [\u00b0]')

        self.setAxisMaxMajor(QwtPlot.xBottom, 6)
        self.setAxisMaxMinor(QwtPlot.xBottom, 10)
        self.setAxisScaleEngine(QwtPlot.xBottom, QwtLogScaleEngine())

        # curves
        self.curve1 = QwtPlotCurve('Amplitude')
        self.curve1.setRenderHint(QwtPlotItem.RenderAntialiased);
        self.curve1.setPen(QPen(Qt.yellow))
        self.curve1.setYAxis(QwtPlot.yLeft)
        self.curve1.attach(self)
        
        self.curve2 = QwtPlotCurve('Phase')
        self.curve2.setRenderHint(QwtPlotItem.RenderAntialiased);
        self.curve2.setPen(QPen(Qt.cyan))
        self.curve2.setYAxis(QwtPlot.yRight)
        self.curve2.attach(self)

        # alias
        fn = self.fontInfo().family()

        # marker
        self.dB3Marker = m = QwtPlotMarker()
        m.setValue(0.0, 0.0)
        m.setLineStyle(QwtPlotMarker.VLine)
        m.setLabelAlignment(Qt.AlignRight | Qt.AlignBottom)
        m.setLinePen(QPen(Qt.green, 2, Qt.DashDotLine))
        text = QwtText('')
        text.setColor(Qt.green)
        text.setBackgroundBrush(Qt.red)
        text.setFont(QFont(fn, 12, QFont.Bold))
        m.setLabel(text)
        m.attach(self)

        self.peakMarker = m = QwtPlotMarker()
        m.setLineStyle(QwtPlotMarker.HLine)
        m.setLabelAlignment(Qt.AlignRight | Qt.AlignBottom)
        m.setLinePen(QPen(Qt.red, 2, Qt.DashDotLine))
        text = QwtText('')
        text.setColor(Qt.red)
        text.setBackgroundBrush(QBrush(self.canvasBackground()))
        text.setFont(QFont(fn, 12, QFont.Bold))
        
        m.setLabel(text)
        m.setSymbol(QwtSymbol(QwtSymbol.Diamond,
                              QBrush(Qt.yellow),
                              QPen(Qt.green),
                              QSize(7,7)))
        m.attach(self)

        # text marker
        m = QwtPlotMarker()
        m.setValue(0.1, -20.0)
        m.setLabelAlignment(Qt.AlignRight | Qt.AlignBottom)
        text = QwtText(
            '[1-(\u03c9/\u03c9<sub>0</sub>)<sup>2</sup>+2j\u03c9/Q]'
            '<sup>-1</sup>'
            )
        text.setFont(QFont(fn, 12, QFont.Bold))
        text.setColor(Qt.blue)
        text.setBackgroundBrush(QBrush(Qt.yellow))
        text.setBorderPen(QPen(Qt.red, 2))
        m.setLabel(text)
        m.attach(self)

        self.setDamp(0.01)

    # __init__()

    def showData(self, frequency, amplitude, phase):
        self.curve1.setData(frequency, amplitude)
        self.curve2.setData(frequency, phase)

    # showData()

    def showPeak(self, frequency, amplitude):
        self.peakMarker.setValue(frequency, amplitude)
        label = self.peakMarker.label()
        label.setText('Peak: %4g dB' % amplitude)
        self.peakMarker.setLabel(label)

    # showPeak()

    def show3dB(self, frequency):
        self.dB3Marker.setValue(frequency, 0.0)
        label = self.dB3Marker.label()
        label.setText('-3dB at f = %4g' % frequency)
        self.dB3Marker.setLabel(label)

    # show3dB()

    def setDamp(self, d):
        self.damping = d
        # Numerical Python: f, g, a and p are NumPy arrays!
        f = np.exp(np.log(10.0)*np.arange(-2, 2.02, 0.04))
        g = 1.0/(1.0-f*f+2j*self.damping*f)
        a = 20.0*np.log10(abs(g))
        p = 180*np.arctan2(g.imag, g.real)/np.pi
        # for show3dB
        i3 = np.argmax(np.where(np.less(a, -3.0), a, -100.0))
        f3 = f[i3] - (a[i3]+3.0)*(f[i3]-f[i3-1])/(a[i3]-a[i3-1])
        # for showPeak
        imax = np.argmax(a)

        self.showPeak(f[imax], a[imax])
        self.show3dB(f3)
        self.showData(f, a, p)

        self.replot()

    # setDamp()

# class BodePlot


class BodeDemo(QMainWindow):

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)

        self.plot = BodePlot(self)
        self.plot.setContentsMargins(5, 5, 5, 0)

        self.setContextMenuPolicy(Qt.NoContextMenu)
        
#        self.zoomers = []
#        zoomer = QwtPlotZoomer(
#            QwtPlot.xBottom,
#            QwtPlot.yLeft,
#            QwtPicker.DragSelection,
#            QwtPicker.AlwaysOff,
#            self.plot.canvas())
#        zoomer.setRubberBandPen(QPen(Qt.green))
#        self.zoomers.append(zoomer)
#
#        zoomer = QwtPlotZoomer(
#            QwtPlot.xTop,
#            QwtPlot.yRight,
#            QwtPicker.PointSelection | QwtPicker.DragSelection,
#            QwtPicker.AlwaysOff,
#            self.plot.canvas())
#        zoomer.setRubberBand(QwtPicker.NoRubberBand)
#        self.zoomers.append(zoomer)

#        self.picker = QwtPlotPicker(
#            QwtPlot.xBottom,
#            QwtPlot.yLeft,
#            QwtPicker.PointSelection | QwtPicker.DragSelection,
#            QwtPlotPicker.CrossRubberBand,
#            QwtPicker.AlwaysOn,
#            self.plot.canvas())
#        self.picker.setRubberBandPen(QPen(Qt.green))
#        self.picker.setTrackerPen(QPen(Qt.cyan))
 
        self.setCentralWidget(self.plot)

        toolBar = QToolBar(self)
        self.addToolBar(toolBar)
        
        btnZoom = QToolButton(toolBar)
        btnZoom.setText("Zoom")
        btnZoom.setIcon(QIcon(QPixmap(zoom_xpm)))
        btnZoom.setCheckable(True)
        btnZoom.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(btnZoom)

        btnPrint = QToolButton(toolBar)
        btnPrint.setText("Print")
        btnPrint.setIcon(QIcon(QPixmap(print_xpm)))
        btnPrint.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(btnPrint)
        self.connect(btnPrint, SIGNAL('clicked()'), self.print_)

        btnExport = QToolButton(toolBar)
        btnExport.setText("Export")
        btnExport.setIcon(QIcon(QPixmap(print_xpm)))
        btnExport.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(btnExport)
        self.connect(btnExport, SIGNAL('clicked()'), self.exportDocument)
            
        toolBar.addSeparator()

        dampBox = QWidget(toolBar)
        dampLayout = QHBoxLayout(dampBox)
        dampLayout.setSpacing(0)
        dampLayout.addWidget(QWidget(dampBox), 10) # spacer
        dampLayout.addWidget(QLabel("Damping Factor", dampBox), 0)
        dampLayout.addSpacing(10)

#        self.cntDamp = QwtCounter(dampBox)
#        self.cntDamp.setRange(0.01, 5.0, 0.01)
#        self.cntDamp.setValue(0.01)
#        dampLayout.addWidget(self.cntDamp, 10)

        toolBar.addWidget(dampBox)

        self.statusBar()
        
        self.zoom(False)
        self.showInfo()
        
#        self.connect(self.cntDamp,
#                     SIGNAL('valueChanged(double)'),
#                     self.plot.setDamp)
        self.connect(btnZoom,
                     SIGNAL('toggled(bool)'),
                     self.zoom)
#        self.connect(self.picker,
#                     SIGNAL('moved(const QPoint &)'),
#                     self.moved)
#        self.connect(self.picker,
#                     SIGNAL('selected(const QPolygon &)'),
#                     self.selected)

    # __init__()

    def print_(self):
        printer = QPrinter(QPrinter.HighResolution)

        printer.setCreator('Bode example')
        printer.setOrientation(QPrinter.Landscape)
        printer.setColorMode(QPrinter.Color)

        docName = str(self.plot.title().text())
        if not docName:
            docName.replace('\n', ' -- ')
            printer.setDocName(docName)

        dialog = QPrintDialog(printer)
        if dialog.exec_():
            renderer = QwtPlotRenderer()
            if (QPrinter.GrayScale == printer.colorMode()):
                renderer.setDiscardFlag(QwtPlotRenderer.DiscardBackground)
                renderer.setDiscardFlag(QwtPlotRenderer.DiscardCanvasBackground)
                renderer.setDiscardFlag(QwtPlotRenderer.DiscardCanvasFrame)
                renderer.setLayoutFlag(QwtPlotRenderer.FrameWithScales)
            renderer.renderTo(self.plot, printer)

    def exportDocument(self):
        self.plot.exportTo("bode.pdf")

    def zoom(self, on):
#        self.zoomers[0].setEnabled(on)
#        self.zoomers[0].zoom(0)
#        
#        self.zoomers[1].setEnabled(on)
#        self.zoomers[1].zoom(0)

#        if on:
#            self.picker.setRubberBand(Qwt.QwtPicker.NoRubberBand)
#        else:
#            self.picker.setRubberBand(Qwt.QwtPicker.CrossRubberBand)

        self.showInfo()

    # zoom()
    
    def showInfo(self, text=""):
#        if not text:
#            if self.picker.rubberBand():
#                text = 'Cursor Pos: Press left mouse button in plot region'
#            else:
#                text = 'Zoom: Press mouse button and drag'
                
        self.statusBar().showMessage(text)
                
    # showInfo()
    
    def moved(self, point):
        info = "Freq=%g, Ampl=%g, Phase=%g" % (
            self.plot.invTransform(Qwt.QwtPlot.xBottom, point.x()),
            self.plot.invTransform(Qwt.QwtPlot.yLeft, point.y()),
            self.plot.invTransform(Qwt.QwtPlot.yRight, point.y()))
        self.showInfo(info)

    # moved()

    def selected(self, _):
        self.showInfo()

    # selected()

def make():
    demo = BodeDemo()
    demo.resize(540, 400)
    demo.show()
    return demo


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fonts = QFontDatabase()
    for name in ('Verdana', 'STIXGeneral'):
        if name in fonts.families():
            app.setFont(QFont(name))
            break
    demo = make()
    sys.exit(app.exec_())
