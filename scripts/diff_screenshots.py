"""Pixel-compare two directories of screenshots produced by
:mod:`capture_screenshots`. See ``scripts/README.md`` and
``doc/issue93_optimization_summary.md`` for the broader workflow.

For each PNG present in both directories, classifies the pair as one of:

* ``IDENTICAL``   - byte-equal files;
* ``EQUAL_PIXELS`` - bytes differ but decoded pixel arrays match;
* ``DIFFER``      - size or pixel mismatch (with ``n/total`` differing pixels,
  pixel percentage, max and mean per-channel magnitude);
* ``ERROR``       - PIL failed to decode one of the files.

Files present in only one side are listed at the end. The exit code is ``0``
if and only if no ``DIFFER`` row is produced (useful as a CI gate).

A ``DIFFER`` baseline does not necessarily mean a regression: some PythonQwt
visual tests use random data, timestamps or live system stats and are
intrinsically non-reproducible. Always pair the run with a self-compare
baseline (e.g. ``shots/master/<binding>`` vs ``shots/master2/<binding>``) to
identify *flaky* tests; see the optimization summary for the classification
rule ("✅ / ⚠️ / ❌").

Prerequisites
-------------
``numpy`` and ``Pillow`` available in the Python that runs the comparison
(any binding-specific venv works - PIL/numpy do not depend on Qt).

Usage
-----
::

    python scripts/diff_screenshots.py shots\\master\\pyqt5 shots\fix\\pyqt5

Output is a Markdown table; pipe through ``Select-String DIFFER|Summary`` to
focus on regressions only.
"""

from __future__ import annotations

import os
import os.path as osp
import sys

import numpy as np
from PIL import Image


def load_array(path):
    img = Image.open(path).convert("RGBA")
    return np.asarray(img)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    a, b = osp.abspath(sys.argv[1]), osp.abspath(sys.argv[2])
    files_a = {f for f in os.listdir(a) if f.lower().endswith(".png")}
    files_b = {f for f in os.listdir(b) if f.lower().endswith(".png")}
    common = sorted(files_a & files_b)
    only_a = sorted(files_a - files_b)
    only_b = sorted(files_b - files_a)

    rows = []
    for name in common:
        pa, pb = osp.join(a, name), osp.join(b, name)
        with open(pa, "rb") as f:
            ba = f.read()
        with open(pb, "rb") as f:
            bb = f.read()
        if ba == bb:
            rows.append((name, "IDENTICAL", "", ""))
            continue
        try:
            arr_a = load_array(pa)
            arr_b = load_array(pb)
        except Exception as exc:
            rows.append((name, "ERROR", str(exc), ""))
            continue
        if arr_a.shape != arr_b.shape:
            rows.append((name, "DIFFER", f"shape {arr_a.shape} vs {arr_b.shape}", ""))
            continue
        diff = np.abs(arr_a.astype(np.int16) - arr_b.astype(np.int16))
        n_diff = int(np.any(diff > 0, axis=-1).sum())
        total = arr_a.shape[0] * arr_a.shape[1]
        pct = 100.0 * n_diff / total
        max_diff = int(diff.max())
        mean_diff = float(diff.mean())
        if n_diff == 0:
            rows.append((name, "EQUAL_PIXELS", "", ""))
        else:
            rows.append(
                (
                    name,
                    "DIFFER",
                    f"{n_diff}/{total} px ({pct:.2f}%)",
                    f"max={max_diff} mean={mean_diff:.2f}",
                )
            )

    # Print a markdown-style table
    print(f"# Screenshot diff: {a} vs {b}")
    print()
    print("| Test (PNG) | Status | Pixels differ | Magnitude |")
    print("|---|---|---|---|")
    for name, status, info1, info2 in rows:
        print(f"| `{name}` | {status} | {info1} | {info2} |")

    if only_a:
        print(f"\nOnly in A: {', '.join(only_a)}")
    if only_b:
        print(f"\nOnly in B: {', '.join(only_b)}")

    n_diff = sum(1 for r in rows if r[1] == "DIFFER")
    n_same = sum(1 for r in rows if r[1] in ("IDENTICAL", "EQUAL_PIXELS"))
    print(f"\nSummary: {n_same} match, {n_diff} differ, {len(common)} total")
    return 0 if n_diff == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
