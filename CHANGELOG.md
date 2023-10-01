# PythonQwt Releases

## Version 0.10.3

- Moved project to the [PlotPyStack](https://github.com/PlotPyStack) organization.

- Unit tests: added support for ``pytest`` and ``coverage`` (60% coverage as of today)

- [Issue #72](https://github.com/PlotPyStack/PythonQwt/issues/72) - AttributeError: 'QwtScaleWidget' object has no attribute 'maxMajor' / 'maxMinor' / 'stepSize'

- [Issue #76](https://github.com/PlotPyStack/PythonQwt/issues/76) - [PySide] AttributeError: 'QwtPlotCanvas' object has no attribute 'Sunken'

- [Issue #63](https://github.com/PlotPyStack/PythonQwt/issues/71) - TypeError: 'PySide2.QtCore.QRect' object is not subscriptable

## Version 0.10.2

- Fixed type mismatch issues on Linux

## Version 0.10.1

- Added support for PyQt6.

## Version 0.10.0

- Added support for QtPy 2 and PySide6.
- Dropped support for Python 2.

## Version 0.9.2

- Curve plotting: added support for `numpy.float32` data type.

## Version 0.9.1

- Added load test showing a large number of plots (eventually highlights performance issues).
- Fixed event management in `QwtPlot` and removed unnecessary `QEvent.LayoutRequest`
  emission in `QwtScaleWidget` (caused high CPU usage with `guiqwt.ImageWidget`).
- `QwtScaleDiv`: fixed ticks initialization when passing all arguments to constructor.
- tests/image.py: fixed overriden `updateLegend` signature.

## Version 0.9.0

- `QwtPlot`: set the `autoReplot` option at False by default, to avoid time consuming
  implicit plot updates.
- Added `QwtPlotItem.setIcon` and `QwtPlotItem.icon` method for setting and getting the
  icon associated to the plot item (as of today, this feature is not strictly needed in
  PythonQwt: this has been implemented for several use cases in higher level libraries
  (see PR #61).
- Removed unused `QwtPlotItem.defaultIcon` method.
- Added various minor optimizations for axes/ticks drawing features.
- Fixed `QwtPlot.canvasMap` when `axisScaleDiv` returns None.
- Fixed alias `np.float` which is deprecated in NumPy 1.20.

## Version 0.8.3

- Fixed simple plot examples (setup.py & plot.py's doc page) following the introduction
  of the new QtPy dependency (Qt compatibility layer) since V0.8.0.

## Version 0.8.2

- Added new GUI-based test script `PythonQwt-py3` to run the test launcher.
- Added command-line options to the `PythonQwt-tests-py3` script to run all the tests
  simultenously in unattended mode (`--mode unattended`) or to update all the
  screenshots (`--mode screenshots`).
- Added internal scripts for automated test in virtual environments with both PyQt5 and
  PySide2.

## Version 0.8.1

- PySide2 support was significatively improved betwen PythonQwt V0.8.0 and
  V0.8.1 thanks to the new `qwt.qwt_curve.array2d_to_qpolygonf` function.

## Version 0.8.0

- Added PySide2 support: PythonQwt is now compatible with Python 2.7, Python 3.4+,
  PyQt4, PyQt5 and PySide2!

## Version 0.7.1

- Changed QwtPlotItem.detachItems signature: removed unnecessary "autoDelete" argument,
  initialiazing "rtti" argument to None (remove all items)
- Improved Qt universal support (PyQt5, ...)

## Version 0.7.0

- Added convenience functions for creating usual objects (curve, grid, marker, ...):

  - `QwtPlotCurve.make`
  - `QwtPlotMarker.make`
  - `QwtPlotGrid.make`
  - `QwtSymbol.make`
  - `QwtText.make`

- Added new test launcher with screenshots (automatically generated)
- Removed `guidata` dependency thanks to the new specific GUI-based test launcher
- Updated documentation (added more examples, using automatically generated screenshots)
- QwtPlot: added "flatStyle" option, a PythonQwt-exclusive feature improving
  default plot style (without margin, more compact and flat look) -- option is
  enabled by default
- QwtAbstractScaleDraw: added option to set the tick color lighter factor for
  each tick type (minor, medium, major) -- this feature is used with the new
  flatStyle option
- Fixed obvious errors (+ poor implementations) in untested code parts
- Major code cleaning and formatting

## Version 0.6.2

- Fixed Python crash occuring at exit when deleting objects (Python 3 only)
- Moved documentation to <https://docs.readthedocs.io/>
- Added unattended tests with multiple versions of WinPython:

  - WinPython-32bit-2.7.6.4
  - WinPython-64bit-2.7.6.4
  - WinPython-64bit-3.4.4.3
  - WinPython-64bit-3.4.4.3Qt5
  - WPy64-3680
  - WPy64-3771
  - WPy64-3830

- Added PyQt4/PyQt5/PySide automatic switch depending on installed libraries

## Version 0.6.1

- Fixed rounding issue with PythonQwt scale engine (0...1000 is now divided
  in 200-size steps, as in both Qwt and PyQwt)
- Removed unnecessary mask on scaleWidget (this closes #35)
- CurveBenchmark.py: fixed TypeError with numpy.linspace (NumPy=1.18)

## Version 0.6.0

- Ported changes from Qwt 6.1.2 to Qwt 6.1.5
- `QwtPlotCanvas.setPaintAttribute`: fixed PyQt4 compatibility issue for BackingStore paint attribute
- Fixed DataDemo.py test script (was crashing ; this closes #41)
- `QwtPainterClass.drawBackground`: fixed obvious bug in untested code (this closes #51)
- `qwtFillBackground`: fixed obvious bug in untested code (this closes #50)
- `QwtPainterClass.fillPixmap`: fixed obvious bug in untested code (this closes #49)
- `QwtStyleSheetRecorder`: fixed obvious bug in untested code (this closes #47, closes #48 and closes #52)
- Added "plot without margins" test for Issue #35

## Version 0.5.5

- `QwtScaleMap.invTransform_scalar`: avoid divide by 0
- Avoid error when computing ticks: when the axis was so small that no tick could be drawn, an exception used to be raised

## Version 0.5.4

Fixed an annoying bug which caused scale widget (axis ticks in particular)
to be misaligned with canvas grid: the user was forced to resize the plot
widget as a workaround

## Version 0.5.3

- Better handling of infinity and `NaN` values in scales (removed `NumPy`
warnings)
- Now handling infinity and `NaN` values in series data: removing points that
can't be drawn
- Fixed logarithmic scale engine: presence of values <= 0 was slowing down
series data plotting

## Version 0.5.2

- Added CHM documentation to wheel package
- Fixed `QwtPlotRenderer.setDiscardFlag`/`setLayoutFlag` args
- Fixed `QwtPlotItem.setItemInterest` args
- Fixed `QwtPlot.setAxisAutoScale`/`setAutoReplot` args

## Version 0.5.1

- Fixed Issue #22: fixed scale issues in [CurveDemo2.py](qwt/tests/CurveDemo2.py)
and [ImagePlotDemo.py](qwt/tests/ImagePlotDemo.py)
- `QwtPlotCurve`: sticks were not drawn correctly depending on orientation
- `QwtInterval`: avoid overflows with `NumPy` scalars
- Fixed Issue #28: curve shading was broken since v0.5.0
- setup.py: using setuptools "entry_points" instead of distutils "scripts"
- Showing curves/plots number in benchmarks to avoid any misinterpretation
(see Issue #26)
- Added Python2/Python3 scripts for running tests

## Version 0.5.0

- Various optimizations
- Major API simplification, taking into account the feature that won't be
implemented (fitting, rounding, weeding out points, clipping, etc.)
- Added `QwtScaleDraw.setLabelAutoSize`/`labelAutoSize` methods to set the new
auto size option (see [documentation](http://pythonhosted.org/PythonQwt/))

## Version 0.4.0

- Color bar: fixed axis ticks shaking when color bar is enabled
- Fixed `QwtPainter.drawColorBar` for horizontal color bars (typo)
- Restored compatibility with original Qwt signals (`QwtPlot`, ...)

## Version 0.3.0

Renamed the project (python-qwt --> PythonQwt), for various reasons.

## Version 0.2.1

Fixed Issue #23: "argument numPoints is not implemented" error was showing
up when calling `QwtSymbol.drawSymbol(symbol, QPoint(x, y))`.

## Version 0.2.0

Added docstrings in all Python modules and a complete documentation based on
Sphinx. See the Overview section for API limitations when comparing to Qwt.

## Version 0.1.1

Fixed Issue #21 (blocking issue *only* on non-Windows platforms when
building the package): typo in "PythonQwt-tests" script name
(in [setup script](setup.py))

## Version 0.1.0

First alpha public release.
