# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""Curve styles"""

SHOW = True # Show test in GUI-based test launcher

import time

from qwt.qt.QtGui import (QApplication, QPen, QBrush, QMainWindow, QTabWidget,
                          QFont, QFontDatabase)
from qwt.qt.QtCore import QSize
from qwt.qt.QtCore import Qt

from qwt.tests import CurveBenchmark as cb
from qwt import QwtSymbol


class CSWidget(cb.BMWidget):
    def params(self, *args):
        symbols, = args
        symb1 = QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.yellow),
                          QPen(Qt.blue), QSize(5, 5))
        symb2 = QwtSymbol(QwtSymbol.XCross, QBrush(),
                          QPen(Qt.darkMagenta), QSize(5, 5))
        if symbols:
            return (
                    ('Sticks', symb1),
                    ('Lines', symb1),
                    ('Steps', symb2),
                    ('Dots', symb2),
                    )
        else:
            return (
                    ('Sticks', None),
                    ('Lines', None),
                    ('Steps', None),
                    ('Dots', None),
                    )


class BMDemo(QMainWindow):
    def __init__(self, max_n, parent=None, **kwargs):
        super(BMDemo, self).__init__(parent=parent)
        self.setWindowTitle('Curve styles')
        tabs = QTabWidget()
        self.resize(1000, 800)
        
        # Force window to show up and refresh (for test purpose only)
        self.show()
        QApplication.processEvents()

        self.setCentralWidget(tabs)
        pts = 1000
        for points, symbols in zip((pts/10, pts/10, pts, pts),
                                   (True, False)*2):
            t0 = time.time()
            widget = CSWidget(points, symbols)
            symtext = "with%s symbols" % ("" if symbols else "out")
            title = '%d points, %s' % (points, symtext)
            tabs.addTab(widget, title)
            tabs.setCurrentWidget(widget)

            # Force widget to refresh (for test purpose only)
            QApplication.processEvents()

            time_str = "Elapsed time: %d ms" % ((time.time()-t0)*1000)
            widget.text.setText(time_str)
        tabs.setCurrentIndex(0)


if __name__ == '__main__':
    app = QApplication([])
    for name in ('Calibri', 'Verdana', 'Arial'):
        if name in QFontDatabase().families():
            app.setFont(QFont(name))
            break
    demo = BMDemo(100000)
    app.exec_()
