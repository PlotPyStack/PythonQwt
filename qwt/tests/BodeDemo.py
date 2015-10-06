# -*- coding: utf-8 -*-
#
# Licensed under the terms of the PyQwt License
# Copyright (C) 2003-2009 Gerard Vermeulen, for the original PyQwt example
# Copyright (c) 2015 Pierre Raybaut, for the PyQt5/PySide port and further 
# developments (e.g. ported to PythonQwt API)
# (see LICENSE file for more details)

from __future__ import unicode_literals

SHOW = True # Show test in GUI-based test launcher

import sys
import numpy as np

from qwt.qt.QtGui import (QApplication, QPen, QBrush, QFrame, QFont, QWidget,
                          QMainWindow, QToolButton, QIcon, QPixmap, QToolBar,
                          QHBoxLayout, QLabel, QPrinter, QPrintDialog,
                          QFontDatabase)
from qwt.qt.QtCore import QSize
from qwt.qt.QtCore import Qt
from qwt import (QwtPlot, QwtPlotMarker, QwtSymbol, QwtLegend, QwtPlotGrid,
                 QwtPlotCurve, QwtPlotItem, QwtLogScaleEngine, QwtText,
                 QwtPlotRenderer)


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

    def showData(self, frequency, amplitude, phase):
        self.curve1.setData(frequency, amplitude)
        self.curve2.setData(frequency, phase)

    def showPeak(self, frequency, amplitude):
        self.peakMarker.setValue(frequency, amplitude)
        label = self.peakMarker.label()
        label.setText('Peak: %4g dB' % amplitude)
        self.peakMarker.setLabel(label)

    def show3dB(self, frequency):
        self.dB3Marker.setValue(frequency, 0.0)
        label = self.dB3Marker.label()
        label.setText('-3dB at f = %4g' % frequency)
        self.dB3Marker.setLabel(label)

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


class BodeDemo(QMainWindow):

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)

        self.plot = BodePlot(self)
        self.plot.setContentsMargins(5, 5, 5, 0)

        self.setContextMenuPolicy(Qt.NoContextMenu)
        
        self.setCentralWidget(self.plot)

        toolBar = QToolBar(self)
        self.addToolBar(toolBar)

        btnPrint = QToolButton(toolBar)
        btnPrint.setText("Print")
        btnPrint.setIcon(QIcon(QPixmap(print_xpm)))
        btnPrint.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(btnPrint)
        btnPrint.clicked.connect(self.print_)

        btnExport = QToolButton(toolBar)
        btnExport.setText("Export")
        btnExport.setIcon(QIcon(QPixmap(print_xpm)))
        btnExport.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolBar.addWidget(btnExport)
        btnExport.clicked.connect(self.exportDocument)
            
        toolBar.addSeparator()

        dampBox = QWidget(toolBar)
        dampLayout = QHBoxLayout(dampBox)
        dampLayout.setSpacing(0)
        dampLayout.addWidget(QWidget(dampBox), 10) # spacer
        dampLayout.addWidget(QLabel("Damping Factor", dampBox), 0)
        dampLayout.addSpacing(10)

        toolBar.addWidget(dampBox)

        self.statusBar()
        
        self.showInfo()

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
        renderer = QwtPlotRenderer(self.plot)
        renderer.exportTo(self.plot, "bode")
    
    def showInfo(self, text=""):
        self.statusBar().showMessage(text)
                
    def moved(self, point):
        info = "Freq=%g, Ampl=%g, Phase=%g" % (
            self.plot.invTransform(QwtPlot.xBottom, point.x()),
            self.plot.invTransform(QwtPlot.yLeft, point.y()),
            self.plot.invTransform(QwtPlot.yRight, point.y()))
        self.showInfo(info)

    def selected(self, _):
        self.showInfo()


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
