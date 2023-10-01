# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015 Pierre Raybaut
# (see LICENSE file for more details)

"""Qt helpers"""

import os.path as osp
import os

from qtpy import QtGui as QG
from qtpy import QtWidgets as QW
from qtpy import QtCore as QC


QT_API = os.environ["QT_API"]


def qcolor_from_str(color, default):
    """Return QColor object from str

    :param color: Input color
    :type color: QColor or str or None
    :param QColor default: Default color (returned if color is None)

    If color is already a QColor instance, simply return color.
    If color is None, return default color.
    If color is neither an str nor a QColor instance nor None, raise TypeError.
    """
    if color is None:
        return default
    elif isinstance(color, str):
        try:
            return getattr(QC.Qt, color)
        except AttributeError:
            raise ValueError("Unknown Qt color %r" % color)
    else:
        try:
            return QG.QColor(color)
        except TypeError:
            raise TypeError("Invalid color %r" % color)


def take_screenshot(widget, path, size=None, quit=True):
    """Take screenshot of widget"""
    if size is not None:
        widget.resize(*size)
    widget.show()
    QW.QApplication.processEvents()
    if QT_API in ("pyqt4", "pyside2"):
        pixmap = QG.QPixmap.grabWidget(widget)
    else:
        pixmap = widget.grab()
    pixmap.save(path)
    if quit:
        QC.QTimer.singleShot(0, QW.QApplication.instance().quit)
