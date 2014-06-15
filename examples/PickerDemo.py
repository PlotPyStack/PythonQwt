#!/usr/bin/env python
#
# Contributed by Darren Dale.

import sys
from PyQt4.Qt import *
from PyQt4.Qwt5 import *

try:
    import numpy as np
except ImportError:
    if not QCoreApplication.instance():
        a = QApplication([])
    QMessageBox.critical(
        None,
        'NumPy required',
        'This example requires NumPy, but failed to import NumPy.\n'
        'NumPy is available at http://sourceforge.net/projects/numpy'
        )
    raise SystemExit(
        'Failed to import NumPy.\n'
        'NumPy is available at http://sourceforge.net/projects/numpy'
        )


class PickerMachine(QwtPickerMachine):
   
    def __init__(self, *args):
        QwtPickerMachine.__init__(self, *args)

    # __init__()
   
    def transition(self, eventPattern,  e):
        commands = []
        # handle the mouse events
        if e.type() == QEvent.MouseButtonPress:
            if eventPattern.mouseMatch(QwtEventPattern.MouseSelect1, e):
                if self.state() == 0:
                    commands.append(QwtPickerMachine.Begin)
                    commands.append(QwtPickerMachine.Append)
                    self.setState(1)
        elif e.type() == QEvent.MouseMove:
            if self.state != 0:
                commands.append(Qwt.QwtPickerMachine.Append)
        elif e.type() == QEvent.MouseButtonRelease:
            commands.append(QwtPickerMachine.End)
            self.setState(0)
        # handling of the kayboard events is left as an excercise
        return commands

    # transition()
       
# class PickerMachine()         
   

class PlotPicker(QwtPlotPicker):
   
    def __init__(self,  *args):
        Qwt.QwtPlotPicker.__init__(self, *args)
        self.setSelectionFlags(QwtPicker.PolygonSelection)   
        # handle only mouse events coming from the left  mouse button
        self.setMousePattern(
            [QwtEventPattern.MousePattern(Qt.LeftButton, Qt.NoModifier)])


    # __init__()

    def drawRubberBand(self, painter):
       
        if (not self.isActive()
            or self.rubberBand() == QwtPicker.NoRubberBand
            or self.rubberBandPen().style() == Qt.NoPen
            ):
            return

        selection = self.selection()

        if (self.selectionFlags() & QwtPicker.PolygonSelection
            and self.rubberBand() == QwtPicker.PolygonRubberBand
            ):
            painter.drawPolygon(selection)

    # drawRubberBand()
    
    def stateMachine(self, flags):
        return PickerMachine()

    # stateMachine()
   
# class PlotPicker


def make():
    demo = QMainWindow()

    toolBar = QToolBar(demo)
    toolBar.addAction(QWhatsThis.createAction(toolBar))
    demo.addToolBar(toolBar)
    
    plot = QwtPlot(demo)
    demo.setCentralWidget(plot)
    plot.setTitle('Subclassing QwtPlotPicker Demo')
    plot.setCanvasBackground(Qt.white)
    plot.setWhatsThis(
        'Shows how to subclass QwtPlotPicker so that\n'
        'a PolygonRubberBand selection responds to\n'
        'left mouse button events.'
        )

    demo.resize(400, 400)
    demo.show()

    x = np.linspace(-2*np.pi, 2*np.pi, num=501)
    y = np.sin(x)*5
    curve = QwtPlotCurve()
    curve.setData(x,y)
    curve.setPen(QPen(Qt.red))
    curve.attach(plot)

    picker = PlotPicker(QwtPlot.xBottom,
                        QwtPlot.yLeft,
                        QwtPicker.PolygonSelection,
                        QwtPlotPicker.PolygonRubberBand,
                        QwtPicker.AlwaysOff,
                        plot.canvas())
    picker.setRubberBandPen(QPen(Qt.black, 1))
    slot = lambda polygon: QMessageBox.information(
        None, 'PlotPicker signaled', str(polygon))
    if PYQT_VERSION == 0x040500:
        # works around a bug in PyQt-4.5/sip-4.8
        picker.connect(picker, SIGNAL('selected(const QPolygon&)'), slot)
    else:
        picker.connect(picker, SIGNAL('selected(const QwtPolygon&)'), slot)
   
    QWhatsThis.enterWhatsThisMode()
    QWhatsThis.showText(
        demo.mapToGlobal(QPoint(200, 200)), plot.whatsThis(), demo)
    return demo

# make()


def main(args):
    app = QApplication(args)
    demo = make()
    sys.exit(app.exec_())

# main()


# Admire
if __name__ == '__main__':
    if 'settracemask' in sys.argv:
        # for debugging, requires: python configure.py --trace ...
        import sip
        sip.settracemask(0x3f)

    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
