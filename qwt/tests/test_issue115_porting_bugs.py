# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see LICENSE file for more details)

"""
Tests for issue 115: porting bugs making several rarely used APIs fail.

Each test covers a difference between the Python port and the Qwt C++ code,
which made the API raise an exception or ignore some of its arguments.
"""

import pytest
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from qwt import (
    QwtLegend,
    QwtPlot,
    QwtPlotGrid,
    QwtPlotItem,
    QwtPlotMarker,
    QwtSymbol,
)
from qwt.graphic import QwtGraphic

RED = QG.QColor(QC.Qt.red)


def _ensure_app():
    # A live QApplication must exist before constructing any QWidget or
    # QPixmap, otherwise Qt aborts the process. Tests run in a shared
    # interpreter, but no test keeps a persistent Python reference to the
    # application, so the singleton may be garbage-collected between tests.
    return QW.QApplication.instance() or QW.QApplication([])


# ---------------------------------------------------------------------------
# QwtGraphic.toPixmap / QwtGraphic.toImage
# ---------------------------------------------------------------------------


def _make_graphic():
    """Return a graphic made of a red rectangle of 20 x 10 points"""
    graphic = QwtGraphic()
    path = QG.QPainterPath()
    path.addRect(QC.QRectF(0.0, 0.0, 20.0, 10.0))
    painter = QG.QPainter(graphic)
    painter.setPen(QC.Qt.NoPen)
    painter.setBrush(RED)
    painter.drawPath(path)
    painter.end()
    return graphic


def _to_qimage(result):
    """Return result as a QImage (result: QPixmap or QImage)"""
    if isinstance(result, QG.QPixmap):
        return result.toImage()
    return result


def _is_red(image, x, y):
    color = image.pixelColor(x, y)
    return color.alpha() == 255 and color.rgb() == RED.rgb()


@pytest.mark.parametrize("method", ("toPixmap", "toImage"))
def test_graphic_conversion_default_size(method):
    """toPixmap() and toImage() render the graphic in its default size"""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    result = getattr(_make_graphic(), method)()
    assert not result.isNull()
    assert result.size() == QC.QSize(20, 10)
    assert _is_red(_to_qimage(result), 10, 5)
    del app


@pytest.mark.parametrize("method", ("toPixmap", "toImage"))
def test_graphic_conversion_given_size(method):
    """toPixmap(size) and toImage(size) scale the graphic to the given size"""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    result = getattr(_make_graphic(), method)(QC.QSize(40, 20))
    assert not result.isNull()
    assert result.size() == QC.QSize(40, 20)
    image = _to_qimage(result)
    assert _is_red(image, 20, 10)
    assert _is_red(image, 2, 2)
    assert _is_red(image, 37, 17)
    del app


@pytest.mark.parametrize("method", ("toPixmap", "toImage"))
def test_graphic_conversion_keep_aspect_ratio(method):
    """toPixmap(size, mode) and toImage(size, mode) honor the aspect ratio"""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    result = getattr(_make_graphic(), method)(QC.QSize(40, 40), QC.Qt.KeepAspectRatio)
    assert result.size() == QC.QSize(40, 40)
    image = _to_qimage(result)
    # The 2:1 graphic is scaled to 40 x 20 and centered vertically
    assert _is_red(image, 20, 20)
    assert image.pixelColor(20, 2).alpha() == 0
    assert image.pixelColor(20, 37).alpha() == 0
    del app


# ---------------------------------------------------------------------------
# QwtPlotMarker.legendIcon
# ---------------------------------------------------------------------------


def _make_symbol():
    return QwtSymbol(
        QwtSymbol.Rect, QG.QBrush(RED), QG.QPen(QC.Qt.NoPen), QC.QSize(8, 8)
    )


@pytest.mark.parametrize(
    "size", (QC.QSize(8, 8), QC.QSizeF(8.0, 8.0)), ids=("QSize", "QSizeF")
)
def test_marker_legend_icon_with_symbol(size):
    """The legend icon of a marker with a symbol shows the symbol"""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    marker = QwtPlotMarker.make(xvalue=0.0, yvalue=0.0, symbol=_make_symbol())
    icon = marker.legendIcon(0, size)
    assert not icon.isNull()
    assert _is_red(icon.toImage(), 4, 4)
    del app


def test_marker_with_symbol_in_legend():
    """A marker with a symbol can be shown in a legend"""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    plot = QwtPlot()
    legend = QwtLegend()
    plot.insertLegend(legend)
    marker = QwtPlotMarker.make(
        xvalue=1.0, yvalue=1.0, title="Marker", symbol=_make_symbol(), plot=plot
    )
    marker.setItemAttribute(QwtPlotItem.Legend, True)
    plot.updateLegend(marker)
    label = legend.legendWidget(marker)
    assert label is not None
    assert not label.icon().isNull()
    plot.close()
    del app


# ---------------------------------------------------------------------------
# QwtPlotGrid.make
# ---------------------------------------------------------------------------


def _pen_attrs(pen):
    return pen.color().name(), pen.widthF(), pen.style()


@pytest.mark.parametrize(
    "kwargs, expected",
    (
        ({"mincolor": "red"}, ("#ff0000", 1.0, QC.Qt.DotLine)),
        ({"minwidth": 2}, ("#a0a0a4", 2.0, QC.Qt.DotLine)),
        ({"minstyle": QC.Qt.DashLine}, ("#a0a0a4", 1.0, QC.Qt.DashLine)),
        ({"mincolor": "red", "minwidth": 2}, ("#ff0000", 2.0, QC.Qt.DotLine)),
        (
            {"mincolor": "red", "minstyle": QC.Qt.DashLine},
            ("#ff0000", 1.0, QC.Qt.DashLine),
        ),
        (
            {"minwidth": 3.0, "minstyle": QC.Qt.SolidLine},
            ("#a0a0a4", 3.0, QC.Qt.SolidLine),
        ),
        (
            {"mincolor": "blue", "minwidth": 0, "minstyle": QC.Qt.DashDotLine},
            ("#0000ff", 0.0, QC.Qt.DashDotLine),
        ),
    ),
)
def test_grid_make_minor_pen(kwargs, expected):
    """QwtPlotGrid.make honors each minor pen argument, with documented defaults"""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    grid = QwtPlotGrid.make(color="green", width=4, style=QC.Qt.DashLine, **kwargs)
    assert _pen_attrs(grid.minorPen()) == expected
    assert _pen_attrs(grid.majorPen()) == ("#00ff00", 4.0, QC.Qt.DashLine)
    del app


def test_grid_make_without_minor_pen():
    """Without minor pen arguments, both pens are built from the major ones"""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    grid = QwtPlotGrid.make(color="green", width=0, style=QC.Qt.SolidLine)
    expected = ("#00ff00", 0.0, QC.Qt.SolidLine)
    assert _pen_attrs(grid.majorPen()) == expected
    assert _pen_attrs(grid.minorPen()) == expected
    del app


if __name__ == "__main__":
    for name in ("toPixmap", "toImage"):
        test_graphic_conversion_default_size(name)
        test_graphic_conversion_given_size(name)
        test_graphic_conversion_keep_aspect_ratio(name)
    for size in (QC.QSize(8, 8), QC.QSizeF(8.0, 8.0)):
        test_marker_legend_icon_with_symbol(size)
    test_marker_with_symbol_in_legend()
    test_grid_make_without_minor_pen()
    print("OK")
