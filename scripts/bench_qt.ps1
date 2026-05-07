# Run the PythonQwt micro load test (qwt/tests/test_loadtest.py) across one
# or several Qt bindings, using per-binding venvs under .venvs/<binding>/.
#
# Primary use case: detect performance regressions in PythonQwt itself,
# isolated from PlotPy. For the PlotPy load test (the one cited in
# https://github.com/PlotPyStack/PythonQwt/issues/93) use
# scripts/bench_plotpy_loadtest.py instead.
#
# See scripts/README.md and doc/issue93_optimization_summary.md for the
# full performance-investigation workflow and reference numbers.
#
# Prerequisites:
#   .venvs/<binding>/Scripts/python.exe must exist for each binding listed in
#   $Bindings, with the corresponding Qt binding + numpy + qtpy + pytest
#   installed, and PythonQwt installed in editable mode (pip install -e .).
#   See scripts/README.md for a one-shot bootstrap snippet.
#
# Usage:
#   .\scripts\bench_qt.ps1                # run all three bindings, 1 run each
#   .\scripts\bench_qt.ps1 pyqt5          # run a single binding
#   .\scripts\bench_qt.ps1 pyqt5,pyside6  # run a subset
#   .\scripts\bench_qt.ps1 -Repeat 5      # repeat each run N times (recommended)
#
# The script sets PYTHONQWT_UNATTENDED_TESTS=1 and QT_API=<binding>, then
# invokes qwt/tests/test_loadtest.py via the binding-specific venv. It
# captures the "Average elapsed time" line printed by the benchmark.

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string[]] $Bindings = @("pyqt5", "pyqt6", "pyside6"),
    [int] $Repeat = 1
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    foreach ($binding in $Bindings) {
        $py = Join-Path $repoRoot ".venvs\$binding\Scripts\python.exe"
        if (-not (Test-Path $py)) {
            Write-Warning "Skipping $binding (venv not found at $py)"
            continue
        }
        $env:PYTHONQWT_UNATTENDED_TESTS = "1"
        $env:QT_API = $binding
        for ($i = 1; $i -le $Repeat; $i++) {
            $output = & $py "qwt\tests\test_loadtest.py" 2>&1
            $avg = $output | Select-String -Pattern "Average elapsed time" | Select-Object -Last 1
            $tag = "[{0}]" -f $binding
            if ($Repeat -gt 1) { $tag = "{0} run {1}/{2}" -f $tag, $i, $Repeat }
            if ($avg) {
                Write-Host ("{0} {1}" -f $tag, $avg.Line.Trim())
            }
            else {
                Write-Host ("{0} (no result)" -f $tag)
                Write-Host ($output -join [Environment]::NewLine)
            }
        }
        Remove-Item Env:PYTHONQWT_UNATTENDED_TESTS -ErrorAction SilentlyContinue
        Remove-Item Env:QT_API -ErrorAction SilentlyContinue
    }
}
finally {
    Pop-Location
}
