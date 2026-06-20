# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see LICENSE file for more details)

"""
Test for issue 109: the ``QwtPlotCanvas.BackingStore`` paint attribute was
non-functional.

After ``invalidateBackingStore()`` reset the buffer to an empty ``QPixmap()``,
``paintEvent`` skipped the backing-store branch because of an extra
``isNull()`` guard, so the double-buffering cache was never regenerated. The
regenerated pixmap was also only bound to a local variable and never stored
back. This test ensures the cache is refreshed (and reused) as intended.
"""

import numpy as np
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from qwt import QwtPlot, QwtPlotCurve


def _make_plot_with_backing_store():
    plot = QwtPlot()
    plot.resize(QC.QSize(400, 300))
    canvas = plot.canvas()
    canvas.setPaintAttribute(canvas.BackingStore, True)
    x = np.linspace(0, 10, 100)
    QwtPlotCurve.make(x, np.sin(x), "Sine", plot)
    return plot, canvas


def test_backing_store_is_regenerated_after_replot():
    """The backing store must be repopulated when painting after a replot."""
    plot, canvas = _make_plot_with_backing_store()
    plot.show()
    plot.replot()  # invalidates the backing store
    QW.QApplication.processEvents()

    # Force a paint so the backing store branch runs.
    canvas.repaint()
    QW.QApplication.processEvents()

    bs = canvas.backingStore()
    assert bs is not None
    assert not bs.isNull()
    # The regenerated pixmap must match the canvas size (accounting for the
    # device pixel ratio), proving it was actually rebuilt and stored back.
    assert bs.size() == canvas.size() * bs.devicePixelRatio()

    plot.close()
    plot.deleteLater()
    QW.QApplication.processEvents()


if __name__ == "__main__":
    app = QW.QApplication.instance() or QW.QApplication([])
    test_backing_store_is_regenerated_after_replot()
    print("OK")
