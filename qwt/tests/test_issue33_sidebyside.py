# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2024 Pierre Raybaut
# (see LICENSE file for more details)

"""
Side-by-side plots sharing a single vertical scale (issue #33)
--------------------------------------------------------------

This example answers `issue #33
<https://github.com/PlotPyStack/PythonQwt/issues/33>`_: how to display several
vertical plots side-by-side, perfectly aligned on a *single* shared vertical
scale (here the depth down a drilled core), while each plot keeps its own
horizontal scale (element concentration, density, ...).

Two practical problems are solved here:

1. **Vertical alignment.** When the left-most plot shows the depth axis and the
   others do not, their canvases do not line up: an enabled vertical scale
   reserves a "border distance" at both ends (so the extreme tick labels are not
   clipped), which pushes its canvas down by a few pixels. To keep every canvas
   aligned, the depth axis is *enabled on every plot* but only *drawn* on the
   first one; on the other plots its components (labels, ticks, backbone) are
   hidden while the very same border distance is reserved through
   :py:meth:`qwt.scale_widget.QwtScaleWidget.setMinBorderDist`. This survives
   relayout/zoom because :py:meth:`qwt.plot.QwtPlot.updateLayout` always honors
   the minimum border distance.

2. **Synchronized zoom/scroll.** A single vertical scroll bar and a pair of
   zoom buttons drive the visible depth window of *all* plots at once, by
   calling :py:meth:`qwt.plot.QwtPlot.setAxisScale` on the shared ``yLeft``
   axis of each plot.
"""

SHOW = True  # Show test in GUI-based test launcher

import numpy as np
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from qwt import (
    QwtLinearScaleEngine,
    QwtPlot,
    QwtPlotCurve,
    QwtPlotGrid,
    QwtScaleDraw,
)
from qwt.tests import utils

DEPTH_MIN, DEPTH_MAX = 0.0, 120.0  # meters
SCROLL_RESOLUTION = 100  # scroll bar steps per meter


def make_drillcore_data():
    """Return synthetic drill-core logs as ``(title, [(label, x, depth)], unit)``"""
    depth = np.linspace(DEPTH_MIN, DEPTH_MAX, 800)
    rng = np.random.default_rng(42)

    def log(base, amp, n_bumps, noise):
        signal = base + noise * rng.standard_normal(depth.size)
        for _ in range(n_bumps):
            center = rng.uniform(DEPTH_MIN, DEPTH_MAX)
            width = rng.uniform(3.0, 12.0)
            # Clip the exponent to avoid float64 underflow (numpy may be set to
            # raise on underflow in the test suite).
            signal += amp * np.exp(
                np.clip(-(((depth - center) / width) ** 2), -50.0, 0.0)
            )
        return np.clip(signal, 0, None)

    return [
        (
            "Iron",
            "Fe (%)",
            [("Fe", log(8.0, 18.0, 5, 0.6), depth)],
        ),
        (
            "Copper",
            "Cu (ppm)",
            [
                ("Cu", log(150.0, 600.0, 4, 20.0), depth),
                ("Cu (smoothed)", log(150.0, 580.0, 4, 2.0), depth),
            ],
        ),
        (
            "Density",
            "rho (g/cm3)",
            [("rho", 2.6 + 0.04 * np.sin(depth / 6.0) + log(0.0, 0.2, 3, 0.01), depth)],
        ),
    ]


class DepthPlot(QwtPlot):
    """A single drill-core log plot with depth on the (inverted) left axis"""

    CURVE_COLORS = ("#1f77b4", "#d62728", "#2ca02c", "#9467bd")

    def _curve_color(self, index):
        """Return a :py:class:`QColor` for the curve at ``index``"""
        return QG.QColor(self.CURVE_COLORS[index % len(self.CURVE_COLORS)])

    def __init__(self, title, x_title, curves, show_depth_axis, parent=None):
        super().__init__(parent)
        self.setObjectName(title)
        self.setTitle(title)

        # By default QwtPlot uses a MinimumExpanding horizontal policy, which
        # makes the surrounding layout treat sizeHint() (not minimumSizeHint())
        # as a hard minimum width. With several plots side-by-side this prevents
        # the widget from being shrunk. An "Ignored" horizontal policy lets every
        # column shrink freely and share the available width equally.
        self.setSizePolicy(QW.QSizePolicy.Ignored, QW.QSizePolicy.Preferred)

        # Horizontal (data) axis on top, like column headers in a core log
        self.enableAxis(self.xBottom, False)
        self.enableAxis(self.xTop, True)
        self.setAxisTitle(self.xTop, x_title)
        # Limit the number of major ticks: the horizontal axis reserves room for
        # all its tick labels (minLabelDist * majorCount), which otherwise sets a
        # very large minimum width and crowds the labels when the plot is narrow.
        self.setAxisMaxMajor(self.xTop, 4)

        # Vertical (depth) axis: inverted so depth increases downwards
        self.enableAxis(self.yLeft, True)
        self.axisScaleEngine(self.yLeft).setAttribute(
            QwtLinearScaleEngine.Inverted, True
        )

        if show_depth_axis:
            self.setAxisTitle(self.yLeft, "Depth (m)")
        else:
            # Keep the axis enabled (so the canvas stays aligned with the
            # reference plot) but hide everything it draws.
            scale_draw = self.axisScaleDraw(self.yLeft)
            scale_draw.enableComponent(QwtScaleDraw.Labels, False)
            scale_draw.enableComponent(QwtScaleDraw.Ticks, False)
            scale_draw.enableComponent(QwtScaleDraw.Backbone, False)
            scale_draw.setMinimumExtent(0)

        QwtPlotGrid.make(self, color=QC.Qt.lightGray, width=0, style=QC.Qt.DotLine)

        for index, (label, x, depth) in enumerate(curves):
            color = self._curve_color(index)
            curve = QwtPlotCurve.make(x, depth, label, self, linecolor=color)
            curve.setAxes(self.xTop, self.yLeft)

        self.setAxisScale(self.yLeft, DEPTH_MIN, DEPTH_MAX)


class DrillCoreViewer(QW.QWidget):
    """Several depth plots side-by-side, aligned on a single shared depth scale"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_span = DEPTH_MAX - DEPTH_MIN
        self.view_span = self.full_span
        self.view_top = DEPTH_MIN

        self.plots = []
        plots_layout = QW.QHBoxLayout()
        plots_layout.setSpacing(0)
        for index, (title, x_title, curves) in enumerate(make_drillcore_data()):
            plot = DepthPlot(title, x_title, curves, show_depth_axis=index == 0)
            self.plots.append(plot)
            plots_layout.addWidget(plot)

        # Vertical scroll bar to move the visible depth window
        self.scrollbar = QW.QScrollBar(QC.Qt.Vertical)
        self.scrollbar.valueChanged.connect(self.scroll_to)
        plots_layout.addWidget(self.scrollbar)

        # Zoom buttons
        zoom_in = QW.QToolButton()
        zoom_in.setText("+")
        zoom_in.setToolTip("Zoom in (depth)")
        zoom_in.clicked.connect(lambda: self.zoom(0.5))
        zoom_out = QW.QToolButton()
        zoom_out.setText("-")
        zoom_out.setToolTip("Zoom out (depth)")
        zoom_out.clicked.connect(lambda: self.zoom(2.0))
        reset = QW.QToolButton()
        reset.setText("Reset")
        reset.clicked.connect(self.reset_view)
        toolbar = QW.QHBoxLayout()
        toolbar.addWidget(QW.QLabel("Depth zoom:"))
        toolbar.addWidget(zoom_in)
        toolbar.addWidget(zoom_out)
        toolbar.addWidget(reset)
        toolbar.addStretch()

        layout = QW.QVBoxLayout()
        layout.addLayout(toolbar)
        layout.addLayout(plots_layout)
        self.setLayout(layout)

        # Align the hidden depth axes with the reference one and apply the view.
        QC.QTimer.singleShot(0, self._align_and_refresh)

    def _align_and_refresh(self):
        """Force identical vertical border distance on every depth axis"""
        for plot in self.plots:
            plot.replot()  # ensure scale divisions are computed
        ref_widget = self.plots[0].axisWidget(self.plots[0].yLeft)
        start, end = ref_widget.getBorderDistHint()
        for plot in self.plots[1:]:
            plot.axisWidget(plot.yLeft).setMinBorderDist(start, end)
        self._apply_view()

    def _apply_view(self):
        """Apply the current depth window to every plot and update the scroll bar"""
        bottom = self.view_top + self.view_span
        for plot in self.plots:
            plot.setAxisScale(plot.yLeft, self.view_top, bottom)
            plot.replot()
        self._update_scrollbar()

    def _update_scrollbar(self):
        """Reflect the current depth window in the scroll bar geometry"""
        hidden = max(self.full_span - self.view_span, 0.0)
        self.scrollbar.blockSignals(True)
        self.scrollbar.setRange(0, int(round(hidden * SCROLL_RESOLUTION)))
        self.scrollbar.setPageStep(int(round(self.view_span * SCROLL_RESOLUTION)))
        self.scrollbar.setSingleStep(
            int(round(self.view_span * SCROLL_RESOLUTION / 10))
        )
        self.scrollbar.setValue(
            int(round((self.view_top - DEPTH_MIN) * SCROLL_RESOLUTION))
        )
        self.scrollbar.setEnabled(hidden > 0)
        self.scrollbar.blockSignals(False)

    def scroll_to(self, value):
        """Scroll bar handler: move the visible depth window"""
        self.view_top = DEPTH_MIN + value / SCROLL_RESOLUTION
        self._apply_view()

    def zoom(self, factor):
        """Zoom the visible depth window around its center by ``factor``"""
        center = self.view_top + self.view_span / 2.0
        self.view_span = min(self.full_span, self.view_span * factor)
        self.view_top = center - self.view_span / 2.0
        self.view_top = max(DEPTH_MIN, min(self.view_top, DEPTH_MAX - self.view_span))
        self._apply_view()

    def reset_view(self):
        """Restore the full depth range"""
        self.view_span = self.full_span
        self.view_top = DEPTH_MIN
        self._apply_view()


def test_issue33_sidebyside():
    """Side-by-side plots sharing a single vertical scale (issue #33)"""
    utils.test_widget(DrillCoreViewer, size=(700, 600))


if __name__ == "__main__":
    test_issue33_sidebyside()
