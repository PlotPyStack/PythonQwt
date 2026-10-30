# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see LICENSE file for more details)

"""
Test that the backbone of a scale is drawn at fractional device pixel ratios.

With the default hairline pen, the backbone of bottom and right scales lies on
the edge of the scale widget. At fractional device pixel ratios (e.g. 125%
screen scaling), depending on the position of the widget in the window, the
backbone was drawn in the device pixel just outside of the widget, where it was
clipped: the axis line was missing (e.g. the X axis of a plot).
"""

import math

import pytest
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from qwt.scale_draw import QwtAbstractScaleDraw, QwtScaleDraw
from qwt.scale_widget import QwtScaleWidget

ALIGNMENTS = (
    QwtScaleDraw.BottomScale,
    QwtScaleDraw.TopScale,
    QwtScaleDraw.LeftScale,
    QwtScaleDraw.RightScale,
)
ALIGNMENT_IDS = ("bottom", "top", "left", "right")
DEVICE_PIXEL_RATIOS = (1.0, 1.25, 1.5, 1.75, 2.0)
LENGTH, THICKNESS = 200, 40  # Scale widget size, along and across the scale
OFFSETS = range(4)  # Positions of the widget in the rendered image


def _ensure_app():
    # A live QApplication must exist before constructing any QWidget, otherwise
    # Qt aborts the process. Tests run in a shared interpreter, but no test
    # keeps a persistent Python reference to the application, so the singleton
    # may be garbage-collected between tests.
    return QW.QApplication.instance() or QW.QApplication([])


def _count_backbone_lines(widget, horizontal, dpr, offset):
    """Render the scale widget at the given offset (in logical pixels) into an
    image with the given device pixel ratio, and return the number of device
    pixel rows (horizontal scale) or columns (vertical scale) entirely drawn
    along the middle of the scale"""
    size = math.ceil((max(LENGTH, THICKNESS) + len(OFFSETS)) * dpr)
    image = QG.QImage(size, size, QG.QImage.Format_RGB32)
    image.setDevicePixelRatio(dpr)
    image.fill(QC.Qt.white)
    widget.render(image, QC.QPoint(offset, offset))
    start = math.ceil((offset + 0.2 * LENGTH) * dpr)
    stop = math.floor((offset + 0.8 * LENGTH) * dpr)
    count = 0
    for across in range(size):
        if horizontal:
            pixels = (image.pixelColor(along, across) for along in range(start, stop))
        else:
            pixels = (image.pixelColor(across, along) for along in range(start, stop))
        if all(color.lightness() < 128 for color in pixels):
            count += 1
    return count


@pytest.mark.parametrize("dpr", DEVICE_PIXEL_RATIOS)
@pytest.mark.parametrize("alignment", ALIGNMENTS, ids=ALIGNMENT_IDS)
def test_backbone_drawn_at_fractional_dpr(alignment, dpr):
    """The backbone is drawn whatever the device pixel ratio and the position
    of the scale widget."""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    widget = QwtScaleWidget(alignment, None)
    widget.setMargin(0)  # As with the flat style of QwtPlot (default style)
    # Labels are not needed, and may be drawn as solid boxes (e.g. with the
    # "offscreen" platform of Qt 6, which has no fonts)
    widget.scaleDraw().enableComponent(QwtAbstractScaleDraw.Labels, False)
    horizontal = alignment in (QwtScaleDraw.BottomScale, QwtScaleDraw.TopScale)
    if horizontal:
        widget.resize(LENGTH, THICKNESS)
    else:
        widget.resize(THICKNESS, LENGTH)
    widget.layoutScale()
    counts = [
        _count_backbone_lines(widget, horizontal, dpr, offset) for offset in OFFSETS
    ]
    assert counts == [1] * len(OFFSETS)
    widget.deleteLater()
    del app


if __name__ == "__main__":
    for align in ALIGNMENTS:
        for ratio in DEVICE_PIXEL_RATIOS:
            test_backbone_drawn_at_fractional_dpr(align, ratio)
    print("OK")
