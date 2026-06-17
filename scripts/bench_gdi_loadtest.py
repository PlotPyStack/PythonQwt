# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 CEA, Codra
# Licensed under the terms of the MIT License
# (see LICENSE file for more details)

"""GDI handle load test for PythonQwt (issue #107).

Simulates the workload of a large test suite (e.g. DataLab's) by repeatedly
creating, rendering, and destroying QwtPlot windows with a variety of
PythonQwt objects attached. On Windows, tracks GDI handle count via the
Windows API to detect handle leaks caused by unbounded caches in
QwtPlainTextEngine.

Background
----------
Before the fix for issue #107, ``QwtPlainTextEngine`` kept an unbounded font
metrics cache that grew with every distinct font configuration. Over hundreds
of plot create/destroy cycles (as in a large test suite), this exhausted the
per-process GDI handle limit (~10 000), causing Qt paint failures or crashes.

Usage
-----
::

    # Run with default 100 cycles, threshold 500 GDI handles:
    python scripts/bench_gdi_loadtest.py

    # Run 500 cycles with verbose output:
    python scripts/bench_gdi_loadtest.py --cycles 500 --verbose

    # Custom threshold:
    python scripts/bench_gdi_loadtest.py --cycles 200 --threshold 300
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# ---------------------------------------------------------------------------
# GDI monitoring (Windows only)
# ---------------------------------------------------------------------------

_IS_WINDOWS = sys.platform == "win32"

if _IS_WINDOWS:
    import ctypes
    import ctypes.wintypes

    _user32 = ctypes.windll.user32
    _kernel32 = ctypes.windll.kernel32

    _GR_GDIOBJECTS = 0
    _GR_USEROBJECTS = 1
    _PROCESS_QUERY_INFORMATION = 0x0400

    def get_gdi_count(pid: int | None = None) -> int:
        """Return the number of GDI objects for the given process."""
        if pid is None:
            pid = os.getpid()
        handle = _kernel32.OpenProcess(_PROCESS_QUERY_INFORMATION, False, pid)
        if not handle:
            return -1
        try:
            return _user32.GetGuiResources(handle, _GR_GDIOBJECTS)
        finally:
            _kernel32.CloseHandle(handle)

    def get_user_object_count(pid: int | None = None) -> int:
        """Return the number of USER objects for the given process."""
        if pid is None:
            pid = os.getpid()
        handle = _kernel32.OpenProcess(_PROCESS_QUERY_INFORMATION, False, pid)
        if not handle:
            return -1
        try:
            return _user32.GetGuiResources(handle, _GR_USEROBJECTS)
        finally:
            _kernel32.CloseHandle(handle)

else:

    def get_gdi_count(pid: int | None = None) -> int:  # noqa: ARG001
        return -1

    def get_user_object_count(pid: int | None = None) -> int:  # noqa: ARG001
        return -1


# ---------------------------------------------------------------------------
# Stress cycle
# ---------------------------------------------------------------------------


def run_stress_cycle() -> None:
    """Build a QMainWindow with a heavily populated QwtPlot and tear it down."""
    from qtpy import QtCore as QC
    from qtpy import QtGui as QG
    from qtpy import QtWidgets as QW

    from qwt import (
        QwtLinearColorMap,
        QwtLogScaleEngine,
        QwtPlot,
        QwtPlotCurve,
        QwtPlotGrid,
        QwtPlotMarker,
        QwtPlotRenderer,
        QwtSymbol,
        QwtText,
    )
    from qwt.legend import QwtLegend
    from qwt.plot_directpainter import QwtPlotDirectPainter
    from qwt.scale_draw import QwtScaleDraw
    from qwt.scale_widget import QwtScaleWidget

    win = QW.QMainWindow()
    win.resize(QC.QSize(1024, 768))

    plot = QwtPlot(win)
    win.setCentralWidget(plot)

    # Grid with minor lines
    grid = QwtPlotGrid()
    grid.enableXMin(True)
    grid.enableYMin(True)
    grid.attach(plot)

    # Legend
    legend = QwtLegend()
    plot.insertLegend(legend, QwtPlot.BottomLegend)

    # Log scale on Y
    plot.setAxisScaleEngine(QwtPlot.yLeft, QwtLogScaleEngine())

    # Color map with stops
    cmap = QwtLinearColorMap(QG.QColor("blue"), QG.QColor("red"))
    cmap.addColorStop(0.25, QG.QColor("cyan"))
    cmap.addColorStop(0.5, QG.QColor("green"))
    cmap.addColorStop(0.75, QG.QColor("yellow"))

    # 10 curves, some with symbols
    x = np.linspace(0.001, 20.0, 200)
    for i in range(10):
        curve = QwtPlotCurve(f"Curve {i}")
        offset = i * 0.5
        scale = 1.0 + i * 0.3
        y = np.abs(np.sin(x + offset) / x) * scale
        curve.setData(x, y)
        if i % 3 == 0:
            sym = QwtSymbol(QwtSymbol.Ellipse)
            sym.setSize(QC.QSize(6, 6))
            curve.setSymbol(sym)
        curve.attach(plot)

    # 5 markers (4 VLine + 1 HLine)
    for i in range(4):
        marker = QwtPlotMarker()
        marker.setLineStyle(QwtPlotMarker.VLine)
        marker.setXValue(2.0 + i * 4.0)
        label = QwtText(f"V{i}")
        marker.setLabel(label)
        marker.attach(plot)
    hmarker = QwtPlotMarker()
    hmarker.setLineStyle(QwtPlotMarker.HLine)
    hmarker.setYValue(1.0)
    hmarker.setLabel(QwtText("H0"))
    hmarker.attach(plot)

    # Standalone QwtScaleWidget
    sw = QwtScaleWidget(QwtScaleDraw.LeftScale, win)
    sw.setTitle(QwtText("Intensity"))

    # Renderer
    renderer = QwtPlotRenderer()
    renderer.setDiscardFlag(QwtPlotRenderer.DiscardBackground, True)

    # DirectPainter
    _dp = QwtPlotDirectPainter(plot)

    # QwtText objects with varied fonts to pressure font caches
    for size in (8, 10, 12, 14, 16, 18):
        txt = QwtText(f"Sample text {size}pt")
        font = QG.QFont("Arial", size)
        txt.setFont(font)
        txt.textSize(font)

    # Render cycle
    plot.replot()
    win.show()
    QW.QApplication.processEvents()
    win.close()
    win.deleteLater()
    QW.QApplication.processEvents()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GDI handle load test for PythonQwt (issue #107)."
    )
    parser.add_argument(
        "--cycles", type=int, default=100, help="Number of stress cycles (default 100)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=500,
        help="Max allowed GDI handle growth (default 500)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print GDI count every cycle"
    )
    args = parser.parse_args()

    from qtpy import API_NAME, PYQT_VERSION, QT_VERSION
    from qtpy import QtWidgets as QW

    pyver = ".".join(str(v) for v in sys.version_info[:3])
    print(
        f"GDI load test [Python {pyver}, Qt {QT_VERSION}, "
        f"{API_NAME} v{PYQT_VERSION}, cycles={args.cycles}]"
    )

    app = QW.QApplication.instance() or QW.QApplication([])

    if not _IS_WINDOWS:
        print("WARNING: Not on Windows — GDI tracking unavailable, running cycles only")

    # Warm-up
    print("Warming up (2 cycles)...")
    for _ in range(2):
        run_stress_cycle()

    baseline_gdi = get_gdi_count()
    peak_gdi = baseline_gdi
    print(f"Baseline GDI count: {baseline_gdi}")

    t0 = time.perf_counter()
    for i in range(1, args.cycles + 1):
        run_stress_cycle()
        current_gdi = get_gdi_count()
        if current_gdi > peak_gdi:
            peak_gdi = current_gdi
        if args.verbose or i % 20 == 0:
            print(f"  cycle {i:4d}/{args.cycles}  GDI={current_gdi}")
    elapsed = time.perf_counter() - t0

    final_gdi = get_gdi_count()
    growth = final_gdi - baseline_gdi if baseline_gdi > 0 else 0

    # Summary
    print()
    print("=" * 50)
    print(f"  Cycles:         {args.cycles}")
    print(f"  Elapsed:        {elapsed:.1f} s")
    print(f"  Baseline GDI:   {baseline_gdi}")
    print(f"  Final GDI:      {final_gdi}")
    print(f"  Peak GDI:       {peak_gdi}")
    print(f"  GDI growth:     {growth}")
    print(f"  Threshold:      {args.threshold}")
    print("=" * 50)

    if _IS_WINDOWS and growth > args.threshold:
        print(f"FAIL: GDI growth ({growth}) exceeds threshold ({args.threshold})")
        sys.exit(1)
    else:
        print("PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
