r"""Profile ``qwt.tests.test_loadtest`` under :mod:`cProfile`.

First-pass tool for performance investigation: identifies which functions
dominate cumulative time and total time. Use :mod:`lineprofile_loadtest` for
the second pass once a hot family of functions has been spotted. See
``scripts/README.md`` and ``doc/issue93_optimization_summary.md``.

What it does
------------
Runs the PythonQwt micro load test once under ``cProfile``, then prints three
reports to stdout (and dumps the raw stats to ``<out_path>``):

1. Top 40 by cumulative time (``--cumulative``).
2. Top 40 by total time (``--tottime``).
3. Top 40 by total time, restricted to ``qwt/`` internals.

Prerequisites
-------------
* A Qt binding selected via ``QT_API`` (``pyqt5`` / ``pyqt6`` / ``pyside6``);
  numbers are most informative when collected for each binding in turn.
* PythonQwt importable.

Usage
-----
::

    $env:QT_API = "pyside6"
    & .\.venvs\pyside6\Scripts\python.exe scripts\profile_loadtest.py pyside6.prof

Open the dumped ``.prof`` file with ``snakeviz`` (``pip install snakeviz``)
or ``gprof2dot`` for a graphical view. Diff the per-binding reports to spot
overhead that scales with binding cost.
"""

from __future__ import annotations

import cProfile
import os
import pstats
import sys
from io import StringIO


def main() -> int:
    os.environ["PYTHONQWT_UNATTENDED_TESTS"] = "1"

    # Import lazily so PYTHONQWT_UNATTENDED_TESTS is honored
    from qwt.tests import test_loadtest

    pr = cProfile.Profile()
    pr.enable()
    test_loadtest.test_loadtest()
    pr.disable()

    out_path = sys.argv[1] if len(sys.argv) > 1 else "profile.out"
    pr.dump_stats(out_path)

    buf = StringIO()
    stats = pstats.Stats(pr, stream=buf).sort_stats("cumulative")
    stats.print_stats(40)
    print(buf.getvalue())

    buf2 = StringIO()
    stats2 = pstats.Stats(pr, stream=buf2).sort_stats("tottime")
    stats2.print_stats(40)
    print("==== TOTTIME TOP 40 ====")
    print(buf2.getvalue())

    buf3 = StringIO()
    stats3 = pstats.Stats(pr, stream=buf3).sort_stats("tottime")
    stats3.print_stats(r"qwt[\\/].*", 40)
    print("==== TOTTIME (qwt only) ====")
    print(buf3.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
