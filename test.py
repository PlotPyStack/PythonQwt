# -*- coding: utf-8 -*-
"""
Created on Fri May 09 19:59:20 2014

@author: pierre
"""

from qwt.qt.QtGui import QBrush, QPen
from qwt.qt.QtCore import Qt, QSize

from qwt.qwt_symbol import QwtSymbol
brush = QBrush(Qt.black)
pen = QPen(Qt.black)
QwtSymbol(QwtSymbol.Ellipse, brush, pen, QSize(3, 3))
