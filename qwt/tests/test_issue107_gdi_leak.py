# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# (see LICENSE file for more details)

"""
Test for issue 107: GDI handle exhaustion on Windows.
"""

import numpy as np
import pytest
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from qwt import QwtPlot, QwtPlotCurve
from qwt.tests.utils import TestEnvironment


def run_stress_cycle():
    """Run one cycle of plot creation, rendering and destruction."""
    plot = QwtPlot()
    plot.resize(QC.QSize(800, 600))
    plot.show()

    # Create many curves with different fonts (via titles) to pressure caches
    for i in range(20):
        curve = QwtPlotCurve(f"Curve {i}")
        x = np.linspace(0, 10, 100)
        y = np.sin(x + i / 10.0)
        curve.setData(x, y)
        curve.attach(plot)

    plot.replot()
    QW.QApplication.processEvents()

    plot.close()
    plot.deleteLater()
    QW.QApplication.processEvents()


def test_gdi_leak_stability():
    """
    Repeatedly create/render/destroy plots to check for GDI leak stability.
    On Windows, without the fix, this would crash after a certain number of cycles
    due to GDI handle exhaustion.
    """
    env = TestEnvironment()
    if not env.unattended:
        pytest.skip("This test is for CI/unattended mode only")

    n_cycles = 50
    for i in range(n_cycles):
        run_stress_cycle()


if __name__ == "__main__":
    app = QW.QApplication.instance() or QW.QApplication([])
    test_gdi_leak_stability()
