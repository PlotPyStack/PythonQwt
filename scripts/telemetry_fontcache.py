"""Telemetry probe for the QwtText font-key cache (PythonQwt).

Measures, over repeated build/destroy cycles of a :class:`qwt.QwtPlot`:

* live Qt / Qwt objects (``QFont``, ``QPixmap``, ``QFontMetrics``,
  ``QwtText``, ``QwtScaleDraw``);
* internal cache sizes (the single-slot font memo plus the metrics caches in
  :mod:`qwt.text`);
* per-cycle render time.

It is the tool used to verify that the font-key cache no longer retains
``QFont`` objects (the memory / GDI-handle leak fixed alongside this script):
the ``QFont`` column and the cache sizes must stay flat across cycles instead
of growing towards the old 1024-entry limit.

Prerequisites
-------------
* A Qt binding selected via ``QT_API`` (``pyqt5`` / ``pyqt6`` / ``pyside6``);
  run it once per binding to cover them all.
* ``PythonQwt`` importable (current working directory or on ``PYTHONPATH``).

Usage
-----
::

    $env:PYTHONPATH = "<...>\\PythonQwt.git"
    $env:QT_API = "pyqt5"      # or pyqt6 / pyside6
    python scripts\\telemetry_fontcache.py --cycles 800 --report-every 100

Pass ``--show`` to exercise the real native window backend (native paint
pipeline, real GDI handles) instead of the default offscreen ``grab()``.
"""

from __future__ import annotations

import argparse
import gc
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYTHONQWT_UNATTENDED_TESTS", "1")

import numpy as np
from qtpy import API_NAME, QT_VERSION
from qtpy.QtWidgets import QApplication

import qwt
import qwt.text as qtext


def count(typename: str) -> int:
    """Return the number of live Python objects whose type name matches.

    :param str typename: Unqualified type name to count (e.g. ``"QFont"``)
    :return: Number of live instances
    """
    return sum(1 for obj in gc.get_objects() if type(obj).__name__ == typename)


def cache_sizes() -> dict:
    """Return a snapshot of the relevant cache sizes in :mod:`qwt.text`.

    Works against both the fixed code (single-slot ``_LAST_FONT`` memo) and any
    older revision that still exposes the retaining ``_FONT_KEY_CACHE`` dict, so
    the script can be used to compare before/after.

    :return: Mapping of cache name to current size
    """
    sizes = {}
    if hasattr(qtext, "_LAST_FONT"):
        sizes["memo_font"] = 0 if qtext._LAST_FONT is None else 1
    if hasattr(qtext, "_FONT_KEY_CACHE"):
        sizes["FONT_KEY_CACHE"] = len(qtext._FONT_KEY_CACHE)
    sizes["ASCENTCACHE"] = len(qtext.ASCENTCACHE)
    return sizes


def make_cycle(app: QApplication, show: bool):
    """Build a closure that creates, renders and destroys one plot per call.

    :param QApplication app: Running application instance
    :param bool show: If True, show a real native window each cycle instead of
     rendering offscreen with ``grab()``
    :return: A zero-argument callable running a single cycle
    """
    x = np.linspace(0, 100, 500)

    def cycle() -> None:
        plot = qwt.QwtPlot("T")
        for k in range(4):
            qwt.QwtPlotCurve.make(x, np.sin(x * 0.1 + k) * 1000 + k, f"c{k}", plot)
        plot.setAxisScale(qwt.QwtPlot.xBottom, 0, 100)
        plot.setAxisScale(qwt.QwtPlot.yLeft, -2000, 2000)
        plot.resize(600, 400)
        if show:
            plot.show()
            app.processEvents()
            plot.replot()
            app.processEvents()
            plot.close()
        else:
            plot.replot()
            plot.grab()
        plot.deleteLater()
        del plot
        app.processEvents()
        gc.collect()
        app.processEvents()

    return cycle


def main() -> int:
    """Run the telemetry loop and print a report every ``--report-every`` cycles.

    :return: Process exit code
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycles", type=int, default=800)
    parser.add_argument("--report-every", type=int, default=100)
    parser.add_argument(
        "--show",
        action="store_true",
        help="show a real native window each cycle (native paint backend)",
    )
    args = parser.parse_args()

    app = QApplication.instance() or QApplication([])
    cycle = make_cycle(app, args.show)

    cycle()  # warm-up (one-time allocations)
    gc.collect()

    print(f"{API_NAME} Qt {QT_VERSION} | {args.cycles} cycles | show={args.show}")
    print(
        f"{'cycle':>6} {'ms/cyc':>7} {'QFont':>6} {'QPixmap':>8} "
        f"{'QFontMetrics':>12} {'QwtText':>8} {'QwtScaleDraw':>13}  caches"
    )

    t_block = time.perf_counter()
    for i in range(1, args.cycles + 1):
        cycle()
        if i % args.report_every == 0:
            ms = (time.perf_counter() - t_block) / args.report_every * 1000
            gc.collect()
            print(
                f"{i:6d} {ms:7.2f} {count('QFont'):6d} {count('QPixmap'):8d} "
                f"{count('QFontMetrics'):12d} {count('QwtText'):8d} "
                f"{count('QwtScaleDraw'):13d}  {cache_sizes()}"
            )
            t_block = time.perf_counter()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
