# PythonQwt performance & visual-regression scripts

This folder collects the tooling that supports performance investigations and visual-regression checks on PythonQwt. It was assembled while working on [issue #93](https://github.com/PlotPyStack/PythonQwt/issues/93) ("Performance degradation with Qt6") and is meant to be reused whenever someone needs to either:

- **Optimize a hot path** — without flying blind on which binding pays the cost.
- **Validate that a refactor did not regress performance** — for any of the supported Qt bindings.
- **Validate that a refactor did not regress rendered output** — pixel-comparison across the 22 visual tests.

The full case study that produced these scripts is documented in [`doc/issue93_optimization_summary.md`](../doc/issue93_optimization_summary.md). Read it first if you want to see the scripts in action and understand the kinds of findings they enable.

## Prerequisites: per-binding virtualenvs

PythonQwt supports PyQt5, PyQt6 and PySide6, and the *whole point* of this tooling is to compare them. The scripts assume three sibling virtual environments under `.venvs/`:

```
PythonQwt/
├── .venvs/
│   ├── pyqt5/     # contains PyQt5
│   ├── pyqt6/     # contains PyQt6
│   └── pyside6/   # contains PySide6
```

`.venvs/` is git-ignored (see [`.gitignore`](../.gitignore)). One-shot bootstrap (PowerShell):

```powershell
foreach ($b in "pyqt5","pyqt6","pyside6") {
    & py -3.11 -m venv ".venvs/$b"
    & ".\.venvs\$b\Scripts\python.exe" -m pip install --upgrade pip
    # Core: Qt binding + qtpy + numpy + test runner + tools used by the scripts
    & ".\.venvs\$b\Scripts\python.exe" -m pip install $b qtpy numpy pytest pillow line_profiler
    # PythonQwt itself (editable, current checkout)
    & ".\.venvs\$b\Scripts\python.exe" -m pip install -e .
    # Optional: needed only by bench_plotpy_loadtest.py
    & ".\.venvs\$b\Scripts\python.exe" -m pip install h5py scipy scikit-image opencv-python-headless tqdm
}
```

If you keep `PlotPy` and `guidata` as sibling editable checkouts, point `PYTHONPATH` at them when running the PlotPy bench (see workflow 3 below) instead of `pip install`-ing them.

## Scripts at a glance

| Script | Use case | Output |
|---|---|---|
| [`bench_qt.ps1`](bench_qt.ps1) | Quick **PythonQwt-only** load test across one or several bindings | `Average elapsed time: <ms> ms` per run |
| [`bench_plotpy_loadtest.py`](bench_plotpy_loadtest.py) | The **PlotPy** load test cited in issue #93 | Same format as `bench_qt.ps1` (parser-compatible) |
| [`profile_loadtest.py`](profile_loadtest.py) | First-pass profiling: who eats CPU? (`cProfile`) | Top-40 by cumulative & total time, plus `qwt/`-only view |
| [`lineprofile_loadtest.py`](lineprofile_loadtest.py) | Second-pass profiling: line-by-line on a curated `HOTSPOTS` set (`line_profiler`) | Annotated source listing |
| [`capture_screenshots.py`](capture_screenshots.py) | Run all 22 visual tests, copy PNGs into `shots/<branch>/<binding>/` | One PNG per test |
| [`diff_screenshots.py`](diff_screenshots.py) | Pixel-compare two screenshot folders | Markdown table; non-zero exit on `DIFFER` |

`run_with_env.py` is unrelated to performance work; it is a generic local-development helper used elsewhere in the project.

## Workflow 1 — "Did I regress performance?"

Run before *and* after the change you want to validate, on the *same* machine, with no other heavy process competing for the CPU:

```powershell
.\scripts\bench_qt.ps1 -Repeat 5            # PythonQwt-only micro load test
# Optional, slower, more representative of real-world usage:
$env:PYTHONPATH = "c:\Dev\PlotPy;c:\Dev\guidata"
foreach ($b in "pyqt5","pyqt6","pyside6") {
    & ".\.venvs\$b\Scripts\python.exe" scripts\bench_plotpy_loadtest.py --repeat 3 --nplots 60
}
```

Use the median across the 5 runs (the first run is usually slower due to warm-up) and **compare across all three bindings**: an optimization that helps PyQt5 only, or that helps PyQt6 only, is rarely a good trade.

## Workflow 2 — "Where is time being spent?"

Two-pass approach. cProfile first (cheap, broad), then line_profiler on the families it surfaces (focused, deep):

```powershell
# First pass: who eats CPU?
$env:QT_API = "pyside6"
& .\.venvs\pyside6\Scripts\python.exe scripts\profile_loadtest.py pyside6.prof

# Second pass: which line of which method? Edit HOTSPOTS in lineprofile_loadtest.py
# to add/remove functions of interest, then:
& .\.venvs\pyside6\Scripts\python.exe scripts\lineprofile_loadtest.py > lineprofile.txt
```

Comparing the cProfile output of two bindings (PyQt5 vs PySide6 typically) is the fastest way to spot Python-side overhead that the Qt6 bindings amplify; that diff is what guided the cleanups in [issue #93](https://github.com/PlotPyStack/PythonQwt/issues/93).

## Workflow 3 — "Did I regress rendered output?"

```powershell
# 1. Capture before (master) and after (your branch) for each binding.
$env:QT_API = "pyqt5"
& .\.venvs\pyqt5\Scripts\python.exe scripts\capture_screenshots.py shots\master\pyqt5
# ... checkout your branch, repeat ...
& .\.venvs\pyqt5\Scripts\python.exe scripts\capture_screenshots.py shots\fix\pyqt5

# 2. (Recommended) capture each side TWICE (master-vs-master2 and fix-vs-fix2)
#    to identify *flaky* tests that have intrinsically random output. Otherwise
#    the diff cannot tell a regression from random data.

# 3. Diff. PIL/numpy do not depend on Qt, so any venv with them works.
& .\.venvs\pyside6\Scripts\python.exe scripts\diff_screenshots.py shots\master\pyqt5 shots\fix\pyqt5
```

After running `capture_screenshots.py`, the test PNGs accumulated under `qwt/tests/data/` should be cleaned up — only the tracked PNGs are kept (one-liner):

```powershell
git checkout -- qwt/tests/data
$tracked = git ls-files qwt/tests/data/*.png | ForEach-Object { Split-Path $_ -Leaf }
Get-ChildItem qwt\tests\data\*.png | Where-Object { $_.Name -notin $tracked } | Remove-Item
```

The classification rule used in the issue #93 summary (✅ / ⚠️ / ❌) crosses two diff runs per test (master self-compare baseline + master-vs-fix). It is described in detail in [`doc/issue93_optimization_summary.md`](../doc/issue93_optimization_summary.md#per-test-screenshot-status-master-vs-phase-2-fix-all-bindings).

## Reference numbers (from issue #93)

So future investigations have a yardstick. Windows 11, Python 3.11.9, real desktop session (not `offscreen`).

PythonQwt micro `test_loadtest` (`scripts/bench_qt.ps1 -Repeat 5`):

| Binding | Master at the time | After issue #93 |
|---|---:|---:|
| PyQt5 | ~1 900 ms | ~450–550 ms |
| PyQt6 | ~2 300 ms | ~450–675 ms |
| PySide6 | ~2 900 ms | ~580–795 ms |

PlotPy `test_loadtest`, 60 plots (`scripts/bench_plotpy_loadtest.py --repeat 3 --nplots 60`):

| Binding | Master at the time | After issue #93 |
|---|---:|---:|
| PyQt5 | 25 134 ms | 16 169 ms |
| PyQt6 | 42 202 ms | 21 387 ms |
| PySide6 | 53 160 ms | 24 849 ms |

If your absolute numbers differ by more than ~30% from these on a typical dev machine, suspect environmental drift before assuming a regression / improvement.

## See also

- [`doc/issue93_optimization_summary.md`](../doc/issue93_optimization_summary.md) — the case study these scripts came out of.
- [Issue #93](https://github.com/PlotPyStack/PythonQwt/issues/93) on GitHub.
