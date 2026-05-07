"""Benchmark PlotPy's load test (test_loadtest) against the current PythonQwt.

This reproduces the load test cited in the PlotPy/PythonQwt performance issue
(https://github.com/PlotPyStack/PythonQwt/issues/93): instantiating a large
grid of plot widgets and measuring construction time. See also
``scripts/README.md`` and ``doc/issue93_optimization_summary.md``.

Prerequisites
-------------
A Python interpreter with **all** of the following importable:

* a Qt binding (``PyQt5``, ``PyQt6`` or ``PySide6``) selected via ``QT_API``;
* ``qtpy``, ``numpy``, plus the usual PlotPy stack (``h5py``, ``scipy``,
  ``scikit-image``, ``opencv-python-headless``, ``tqdm``);
* ``plotpy`` and ``guidata`` (typically as editable installs from sibling
  checkouts: set ``PYTHONPATH=<...>\\PlotPy;<...>\\guidata``);
* the ``PythonQwt`` checkout under test (current working directory or in the
  same ``PYTHONPATH``).

The script does **not** force ``QT_QPA_PLATFORM=offscreen``: numbers are taken
with the real Qt paint pipeline so they include composite cost.

Usage
-----
::

    # PowerShell, with the PyQt5 venv prepared as described in scripts/README.md
    $env:QT_API = "pyqt5"
    $env:PYTHONPATH = "c:\\Dev\\PlotPy;c:\\Dev\\guidata"
    & .\\.venvs\\pyqt5\\Scripts\\python.exe scripts\bench_plotpy_loadtest.py --repeat 3 --nplots 60

Output contains a line compatible with ``scripts/bench_qt.ps1``'s parser::

    Average elapsed time: <ms> ms
"""

from __future__ import annotations

import argparse
import os
import time

# Avoid PlotPy's "first run" wizard / dialogs in headless mode
os.environ.setdefault("GUIDATA_TEST_MODE", "1")


def run_once(nplots: int, ncols: int, nrows: int) -> float:
    """Run one LoadTest construction and return elapsed seconds."""
    # Imports happen inside the function so the Qt binding is fully selected
    # via QT_API by the time PlotPy / guidata import qtpy.
    from guidata.qthelpers import qt_app_context  # noqa: WPS433
    from plotpy.tests.benchmarks.test_loadtest import LoadTest  # noqa: WPS433
    from qtpy import QtWidgets as QW  # noqa: WPS433

    with qt_app_context(exec_loop=False):
        t0 = time.perf_counter()
        win = LoadTest(nplots=nplots, ncols=ncols, nrows=nrows)
        win.show()
        QW.QApplication.processEvents()
        elapsed = time.perf_counter() - t0
        win.close()
    return elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--nplots", type=int, default=60)
    parser.add_argument("--ncols", type=int, default=6)
    parser.add_argument("--nrows", type=int, default=5)
    args = parser.parse_args()

    # Print binding banner like PythonQwt's own loadtest does
    import sys

    from qtpy import API_NAME, PYQT_VERSION, QT_VERSION  # noqa: WPS433

    pyver = ".".join(str(v) for v in sys.version_info[:3])
    print(
        f"PlotPy load test [Python {pyver}, Qt {QT_VERSION}, "
        f"{API_NAME} v{PYQT_VERSION}, nplots={args.nplots}]"
    )

    times = []
    for i in range(args.repeat):
        t = run_once(args.nplots, args.ncols, args.nrows)
        times.append(t)
        print(f"  run {i + 1}/{args.repeat}: {t * 1000:.0f} ms")
    avg_ms = sum(times) / len(times) * 1000
    print(f"Average elapsed time: {avg_ms:.0f} ms")


if __name__ == "__main__":
    main()
