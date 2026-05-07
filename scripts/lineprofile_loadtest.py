r"""Line-profile a curated set of PythonQwt hot functions under the load test.

Second-pass tool for performance investigation, used after
:mod:`profile_loadtest` has identified the hot families. Line-by-line
attribution often surfaces costs that are invisible to ``cProfile`` (e.g. a
single ``QFont.key()`` call inside a tight loop, or per-call QObject overhead
on Qt6). See ``scripts/README.md`` and ``doc/issue93_optimization_summary.md``.

What it does
------------
Runs ``qwt.tests.test_loadtest`` once with :mod:`line_profiler` instrumenting
each function listed in :data:`HOTSPOTS`, then prints the line-by-line stats
on stdout (units: microseconds).

The ``HOTSPOTS`` mapping is a *curated* registry. When the surface area of an
optimization changes, **edit the mapping in this file** to add/remove
functions; passing names on the command-line only restricts which of the
registered hotspots are profiled in this run.

Prerequisites
-------------
* A Qt binding selected via ``QT_API`` (``pyqt5`` / ``pyqt6`` / ``pyside6``).
* ``line_profiler`` (``pip install line_profiler``).
* PythonQwt importable.

Usage
-----
::

    # Full hotspot set
    & .\.venvs\pyside6\Scripts\python.exe scripts\lineprofile_loadtest.py

    # Subset (whatever you are currently iterating on)
    & .\.venvs\pyside6\Scripts\python.exe scripts\lineprofile_loadtest.py textSize labelRect

Redirect to a file when iterating: ``> lineprofile.txt`` then diff between
commits to confirm a hot line dropped from N us to N/2.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("PYTHONQWT_UNATTENDED_TESTS", "1")

from line_profiler import LineProfiler  # noqa: E402

import qwt.scale_div  # noqa: E402
import qwt.scale_draw  # noqa: E402
import qwt.scale_engine  # noqa: E402
import qwt.scale_map  # noqa: E402
import qwt.text  # noqa: E402
from qwt.tests import test_loadtest  # noqa: E402

# (module, qualified-name) — only methods listed here are line-profiled.
HOTSPOTS = {
    "textSize": qwt.text.QwtText.textSize,
    "textEngine": qwt.text.QwtText.textEngine,
    "QwtText.__init__": qwt.text.QwtText.__init__,
    "PlainTextEngine.textMargins": qwt.text.QwtPlainTextEngine.textMargins,
    "labelRect": qwt.scale_draw.QwtScaleDraw.labelRect,
    "labelPosition": qwt.scale_draw.QwtScaleDraw.labelPosition,
    "labelTransformation": qwt.scale_draw.QwtScaleDraw.labelTransformation,
    "getBorderDistHint": qwt.scale_draw.QwtScaleDraw.getBorderDistHint,
    "draw": qwt.scale_draw.QwtScaleDraw.draw,
    "drawLabel": qwt.scale_draw.QwtScaleDraw.drawLabel,
    "drawTick": qwt.scale_draw.QwtScaleDraw.drawTick,
    "drawBackbone": qwt.scale_draw.QwtScaleDraw.drawBackbone,
    "scale_map.transform": qwt.scale_map.QwtScaleMap.transform,
    "scale_engine.strip": qwt.scale_engine.QwtScaleEngine.strip,
    "scale_engine.contains": qwt.scale_engine.QwtScaleEngine.contains,
    "scale_div.contains": qwt.scale_div.QwtScaleDiv.contains,
    "orientation": qwt.scale_draw.QwtScaleDraw.orientation,
}


def main() -> None:
    selected = sys.argv[1:] or list(HOTSPOTS)
    profiler = LineProfiler()
    for name in selected:
        if name not in HOTSPOTS:
            print(f"Unknown hotspot: {name!r}", file=sys.stderr)
            continue
        profiler.add_function(HOTSPOTS[name])

    profiler.runcall(test_loadtest.test_loadtest)
    profiler.print_stats(stream=sys.stdout, output_unit=1e-6)


if __name__ == "__main__":
    main()
