"""Capture screenshots from every PythonQwt visual test into a directory.

Used together with :mod:`diff_screenshots` to detect visual regressions
introduced by performance optimizations. See ``scripts/README.md`` and
``doc/issue93_optimization_summary.md`` for the broader workflow.

What it does
------------
For each entry in the hard-coded ``tests`` list, runs the corresponding test
in a *subprocess* with ``PYTHONQWT_TAKE_SCREENSHOTS=1`` and
``PYTHONQWT_UNATTENDED_TESTS=1`` set, watches the test data directory for
newly-written PNGs and copies them into ``<output_dir>`` with names of the
form ``<test_module>__<original_name>.png`` (so different tests producing the
same PNG basename do not overwrite each other).

Prerequisites
-------------
* A Qt binding selected via ``QT_API`` (``pyqt5`` / ``pyqt6`` / ``pyside6``).
* PythonQwt importable (typically the editable install of the local checkout).
* The Qt platform plug-in able to render to a real display surface
  (offscreen also works but produces slightly different antialiasing).

Usage
-----
::

    $env:QT_API = "pyqt5"
    & .\\.venvs\\pyqt5\\Scripts\\python.exe scripts\\capture_screenshots.py shots\fix\\pyqt5

The output directory is created if missing. After the run, leftover PNGs in
``qwt/tests/data/`` should be cleaned up (only newly-untracked PNGs are
produced by tests; see ``scripts/README.md`` for the cleanup snippet).

Note: the ``tests`` list maps each test *module* (``test_xxx``) to the *test
function* defined inside it. Some modules use a slightly different function
name (``test_relativemargin`` -> ``test_relative_margin``,
``test_symbols`` -> ``test_base``); update this mapping if new visual tests
are added.
"""

from __future__ import annotations

import os
import os.path as osp
import shutil
import subprocess
import sys
import time
import traceback


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    out_dir = osp.abspath(sys.argv[1])
    os.makedirs(out_dir, exist_ok=True)

    os.environ["PYTHONQWT_TAKE_SCREENSHOTS"] = "1"
    os.environ["PYTHONQWT_UNATTENDED_TESTS"] = "1"

    import qwt  # noqa: F401
    from qwt.tests import utils as test_utils

    data_dir = osp.join(test_utils.TEST_PATH, "data")

    tests = [
        ("test_backingstore", "test_backingstore"),
        ("test_bodedemo", "test_bodedemo"),
        ("test_cartesian", "test_cartesian"),
        ("test_cpudemo", "test_cpudemo"),
        ("test_curvebenchmark1", "test_curvebenchmark1"),
        ("test_curvebenchmark2", "test_curvebenchmark2"),
        ("test_curvedemo1", "test_curvedemo1"),
        ("test_curvedemo2", "test_curvedemo2"),
        ("test_data", "test_data"),
        ("test_errorbar", "test_errorbar"),
        ("test_eventfilter", "test_eventfilter"),
        ("test_highdpi", "test_highdpi"),
        ("test_image", "test_image"),
        ("test_loadtest", "test_loadtest"),
        ("test_logcurve", "test_logcurve"),
        ("test_mapdemo", "test_mapdemo"),
        ("test_multidemo", "test_multidemo"),
        ("test_relativemargin", "test_relative_margin"),
        ("test_simple", "test_simple"),
        ("test_stylesheet", "test_stylesheet"),
        ("test_symbols", "test_base"),
        ("test_vertical", "test_vertical"),
    ]

    failed: list[str] = []
    no_screenshot: list[str] = []

    for module_name, func_name in tests:
        before = {
            f: os.path.getmtime(osp.join(data_dir, f))
            for f in os.listdir(data_dir)
            if f.lower().endswith(".png")
        }
        marker = time.time()

        cmd = [
            sys.executable,
            "-c",
            f"import qwt.tests.{module_name} as m; m.{func_name}()",
        ]
        try:
            proc = subprocess.run(
                cmd,
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {module_name}")
            failed.append(module_name)
            continue

        if proc.returncode != 0:
            print(f"[FAIL] {module_name}: rc={proc.returncode}")
            if proc.stderr:
                print(proc.stderr.strip()[-500:])
            failed.append(module_name)
            continue

        produced = []
        for f in os.listdir(data_dir):
            if not f.lower().endswith(".png"):
                continue
            full = osp.join(data_dir, f)
            mt = os.path.getmtime(full)
            if mt >= marker - 0.5 and (f not in before or mt > before[f] + 0.001):
                produced.append(f)

        if not produced:
            print(f"[NO SCREENSHOT] {module_name}")
            no_screenshot.append(module_name)
            continue

        for png in produced:
            src = osp.join(data_dir, png)
            dst = osp.join(out_dir, f"{module_name}__{png}")
            shutil.copy2(src, dst)
            print(f"[OK] {module_name} -> {osp.basename(dst)}")

    print()
    print(f"Captured screenshots into: {out_dir}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
    if no_screenshot:
        print(f"No screenshot ({len(no_screenshot)}): {', '.join(no_screenshot)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
