# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see LICENSE file for more details)

"""
Test for issue 113: axis ticks misaligned with the canvas after replacing the
scale draw.

``QwtScaleWidget.setScaleDraw`` passed the alignment, the scale division and
the transformation of the previous scale draw to the new one, but not its
position and length. The border distance hint was then computed from a scale
of zero length, so the axis was laid out with border distances differing from
the stored ones used by ``QwtPlot.canvasMap``: grid lines and plot items no
longer matched the ticks, even after a replot, until the next scale division
change.
"""

import numpy as np
import pytest
from qtpy import QtWidgets as QW

from qwt import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtScaleDraw

# Scale bounds that are not major ticks: end labels do not overflow the scale
# ends, so that the stored border distances are zero
X_BOUNDS = (3.06e-7, 4.1e-7)
Y_BOUNDS = (-1.05, 1.05)
AXES = (QwtPlot.xBottom, QwtPlot.yLeft)
AXIS_IDS = ("xBottom", "yLeft")


def _ensure_app():
    # A live QApplication must exist before constructing any QWidget, otherwise
    # Qt aborts the process. Tests run in a shared interpreter, but no test
    # keeps a persistent Python reference to the application, so the singleton
    # may be garbage-collected between tests (observed on Linux/PyQt5 in CI).
    return QW.QApplication.instance() or QW.QApplication([])


def _make_plot(app):
    plot = QwtPlot()
    x = np.linspace(*X_BOUNDS, 1000)
    QwtPlotCurve.make(x, np.tanh((x - 3.1e-7) * 1e8), plot=plot)
    QwtPlotGrid().attach(plot)
    plot.setAxisScale(QwtPlot.xBottom, *X_BOUNDS)
    plot.setAxisScale(QwtPlot.yLeft, *Y_BOUNDS)
    plot.resize(600, 400)
    plot.show()
    plot.replot()
    app.processEvents()
    return plot


def _scale_ends(plot, axis_id):
    """Return the ends of the axis scale and of the canvas map, in canvas
    coordinates"""
    widget = plot.axisWidget(axis_id)
    if axis_id in (QwtPlot.yLeft, QwtPlot.yRight):
        offset = widget.y() - plot.canvas().y()
    else:
        offset = widget.x() - plot.canvas().x()
    smap = widget.scaleDraw().scaleMap()
    cmap = plot.canvasMap(axis_id)
    scale_ends = sorted((smap.p1() + offset, smap.p2() + offset))
    canvas_ends = sorted((cmap.p1(), cmap.p2()))
    return scale_ends, canvas_ends


@pytest.mark.parametrize("axis_id", AXES, ids=AXIS_IDS)
def test_replaced_scale_draw_keeps_geometry(axis_id):
    """The new scale draw takes the position and length of the previous one."""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    plot = _make_plot(app)

    old_draw = plot.axisScaleDraw(axis_id)
    pos, length = old_draw.pos(), old_draw.length()
    new_draw = QwtScaleDraw()
    plot.setAxisScaleDraw(axis_id, new_draw)

    assert plot.axisScaleDraw(axis_id) is new_draw
    assert new_draw.pos() == pos
    assert new_draw.length() == length

    plot.close()
    del app


@pytest.mark.parametrize("axis_id", AXES, ids=AXIS_IDS)
def test_axis_aligned_with_canvas_after_scale_draw_change(axis_id):
    """Axis ticks stay aligned with the canvas after replacing the scale draw."""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    plot = _make_plot(app)

    scale_ends, canvas_ends = _scale_ends(plot, axis_id)
    assert scale_ends == pytest.approx(canvas_ends, abs=0.5)

    plot.setAxisScaleDraw(axis_id, QwtScaleDraw())
    plot.replot()
    app.processEvents()

    scale_ends, canvas_ends = _scale_ends(plot, axis_id)
    assert scale_ends == pytest.approx(canvas_ends, abs=0.5)

    plot.close()
    del app


if __name__ == "__main__":
    for axis in AXES:
        test_replaced_scale_draw_keeps_geometry(axis)
        test_axis_aligned_with_canvas_after_scale_draw_change(axis)
    print("OK")
