# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see LICENSE file for more details)

"""
Test for issue 88: ``QwtPlot.setMouseTracking`` was ignored.

The plot's drawing area is occupied by the canvas widget, so mouse move events
over the plot are delivered to the canvas rather than to the ``QwtPlot`` frame.
Calling ``QwtPlot.setMouseTracking(True)`` therefore had no visible effect: the
canvas kept its default (button-pressed-only) move events. ``QwtPlot`` now
propagates its mouse-tracking state to the canvas so that the setting behaves
as documented by ``QWidget.setMouseTracking``.
"""

from qtpy import QtWidgets as QW

from qwt import QwtPlot, QwtPlotCanvas


def _ensure_app():
    # A live QApplication must exist before constructing any QWidget, otherwise
    # Qt aborts the process. Tests run in a shared interpreter, but no test
    # keeps a persistent Python reference to the application, so the singleton
    # may be garbage-collected between tests (observed on Linux/PyQt5 in CI).
    return QW.QApplication.instance() or QW.QApplication([])


def test_set_mouse_tracking_propagates_to_canvas():
    """Enabling/disabling mouse tracking on the plot updates the canvas."""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    plot = QwtPlot()

    # By default mouse tracking is off on both the plot and its canvas.
    assert not plot.hasMouseTracking()
    assert not plot.canvas().hasMouseTracking()

    plot.setMouseTracking(True)
    assert plot.hasMouseTracking()
    assert plot.canvas().hasMouseTracking()

    plot.setMouseTracking(False)
    assert not plot.hasMouseTracking()
    assert not plot.canvas().hasMouseTracking()

    plot.close()
    del app


def test_set_canvas_inherits_mouse_tracking_state():
    """A canvas set after enabling tracking inherits the plot's state."""
    app = _ensure_app()  # keep a reference alive for the duration of the test
    plot = QwtPlot()
    plot.setMouseTracking(True)

    new_canvas = QwtPlotCanvas(plot)
    assert not new_canvas.hasMouseTracking()

    plot.setCanvas(new_canvas)
    assert plot.canvas() is new_canvas
    assert new_canvas.hasMouseTracking()

    plot.close()
    del app


if __name__ == "__main__":
    test_set_mouse_tracking_propagates_to_canvas()
    test_set_canvas_inherits_mouse_tracking_state()
