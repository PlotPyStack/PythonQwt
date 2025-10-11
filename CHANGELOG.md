# PythonQwt Releases

## Version 0.15.0

- Added support for `QwtDateTimeScaleDraw` and `QwtDateTimeScaleEngine` for datetime axis support (see `QwtDateTimeScaleDraw` and `QwtDateTimeScaleEngine` classes in the `qwt` module)
- Improved font rendering for rotated text in `QwtPlainTextEngine.draw` method: disabled font hinting to avoid character misalignment in rotated text

## Version 0.14.6

- Fixed [Issue #100](https://github.com/PlotPyStack/PythonQwt/issues/100) - TypeError in `QwtSymbol.drawSymbol` method due to outdated `renderSymbols` call
- Fixed [Issue #101](https://github.com/PlotPyStack/PythonQwt/issues/101) - `RuntimeWarning: overflow encountered in cast` when plotting `numpy.float32` curve data
- Merged [PR #103](https://github.com/PlotPyStack/PythonQwt/pull/103): [FIX] wrong handling of `border.rectList` with PySide6 backend - thanks to @martinschwinzerl

## Version 0.14.5

- Merged [PR #98](https://github.com/PlotPyStack/PythonQwt/pull/98): Fix legend still being visible after removed
- Merged [PR #99](https://github.com/PlotPyStack/PythonQwt/pull/99): Fix `QRectF` to `QRect` cast in `QwtPainterClass.drawBackground`

## Version 0.14.4

- Fixed canvas rectangle type in `drawItems` method call in `QwtPlot.drawCanvas` (was causing a hard crash when printing to PDF a canvas with upstream `PlotPy` project)

## Version 0.14.3

- Fixed [Issue #94](https://github.com/PlotPyStack/PythonQwt/issues/94) - Different logarithmic scale behavior when compared to Qwt
- Merged [PR #91](https://github.com/PlotPyStack/PythonQwt/pull/91): Fix: legend now showing up when enabled later - thanks to @nicoddemus
- Removed `QwtPlotItem.setIcon` and `QwtPlotItem.icon` methods (introduced in 0.9.0 but not used in PythonQwt)

## Version 0.14.2

- Merged [PR #89](https://github.com/PlotPyStack/PythonQwt/pull/89): fixed call to `ScaleEngine.autoScale` in `QwtPlot.updateAxes` (returned values were not used) - thanks to @nicoddemus
- Merged [PR #90](https://github.com/PlotPyStack/PythonQwt/pull/90): updated `QwtLinearScaleEngine.autoScale` method implementation to the latest Qwt version - thanks to @nicoddemus

## Version 0.14.1

- Handled `RuntimeError` when running `test_eventfilter.py` on Ubuntu 22.04 (Python 3.12, PyQt5)
- Fixed `ResourceWarning: unclosed file` in `test_cpudemo.py` (purely test issue)
- Fixed segmentation fault in `test_multidemo.py` (purely test issue, related to test utility module `qwt.tests.utils`)
- Update GitHub actions to use the latest versions of actions/checkout, actions/setup-python, ...

## Version 0.14.0

- Dropped support for Python 3.8

## Version 0.12.7

- Fixed random crashes (segfaults) on Linux related to conflicts between Qt and Python reference counting mechanisms:
  - This issue was only happening on Linux, and only with Python 3.12, probably due to changes in Python garbage collector behavior introduced in Python 3.12. Moreover, it was only triggered with an extensive test suite, such as the one provided by the `PlotPy` project.
  - The solution was to derive all private classes containing Qt objects from `QObject` instead of `object`, in order to let Qt manage the reference counting of its objects.
  - This change was applied to the following classes:
    - `QwtLinearColorMap_PrivateData`
    - `QwtColumnSymbol_PrivateData`
    - `QwtDynGridLayout_PrivateData`
    - `QwtGraphic_PrivateData`
    - `QwtLegendLabel_PrivateData`
    - `QwtNullPaintDevice_PrivateData`
    - `QwtPlotCanvas_PrivateData`
    - `QwtPlotDirectPainter_PrivateData`
    - `QwtPlotGrid_PrivateData`
    - `QwtPlotLayout_PrivateData`
    - `QwtPlotMarker_PrivateData`
    - `QwtPlotRenderer_PrivateData`
    - `QwtPlot_PrivateData`
    - `QwtAbstractScaleDraw_PrivateData`
    - `QwtScaleDraw_PrivateData`
    - `QwtScaleWidget_PrivateData`
    - `QwtSymbol_PrivateData`
    - `QwtText_PrivateData`
- Removed deprecated code regarding PyQt4 compatibility

## Version 0.12.6

- Fixed random crashes (segfaults) on Linux related to Qt objects stored in cache data structures (`QwtText` and `QwtSymbol`)

- Test suite can simply be run with `pytest` and specific configuration (`conftest.py`) will be taken into account (previously, the test suite has to be run with `pytest qwt` in order to be successfully configured)

## Version 0.12.5

- Add support for NumPy 2.0:
  - Use `numpy.asarray` instead of `numpy.array(..., copy=False)`
  - Update requirements to remove the NumPy version upper bound constraint

## Version 0.12.4

- Fixed segmentation fault issue reported in the `PlotPy` project:
  - See [PlotPy's Issue #13](https://github.com/PlotPyStack/PlotPy/issues/13) for the original issue.
  - The issue was caused by the `QwtSymbol` class constructor, and more specifically by its private data object, which instanciated an empty `QtPainterPath` object, causing a segmentation fault on Linux, Python 3.12 and PyQt5.

## Version 0.12.3

- Fixed `Fatal Python error` issue reported in the `PlotPy` project:
  - See [PlotPy's Issue #11](https://github.com/PlotPyStack/PlotPy/issues/11) for the original issue, even if the problem is not directly pointed out in the issue comments.
  - The issue was caused by the `QwtAbstractScaleDraw` cache mechanism, which was keeping references to `QSizeF` objects that were deleted by the garbage collector at some point. This was causing a segmentation fault, but only on Linux, and only when executing the `PlotPy` test suite in a specific order.
  - Thanks to @yuzibo for helping to reproduce the issue and providing a test case, that is the `PlotPy` Debian package build process.

## Version 0.12.2

For this release, test coverage is 72%.

- Preparing for NumPy V2 compatibility: this is a work in progress, as NumPy V2 is not yet released. In the meantime, requirements have been updated to exclude NumPy V2.
- Fix `QwtPlot.axisInterval` (was raising `AttributeError`)
- Removed unnecessary dependencies (pytest-qt, pytest-cov)
- Moved `conftest.py` to project root
- Project code formatting: using `ruff` instead of `black` and `isort`

## Version 0.12.1

- Fixed `ColorStops.stops` method (was returning a copy of the list of stops instead of the list itself)

## Version 0.12.0

- 30% performance improvement (measured by `qwt.tests.test_loadtest`) by optimizing the `QwtAbstractScaleDraw.tickLabel` method:
  - Suppressed an unnecessary call to `QFont.textSize` (which can be quite slow)
  - Cached the text size with the label `QwtText` object
- Added support for margins in `QwtPlot` (see Issue #82):
  - Default margins are set to 0.05 (5% of the plot area) at each side of the plot
  - Margins are adjustable for each plot axis using `QwtPlot.setAxisMargin` (and `QwtPlot.axisMargin` to get the current value)
- Added an additional margin to the left of ticks labels: this margin is set to one character width, to avoid the labels to be truncated while keeping a tight layout
- Slighly improved the new flat style (see V0.7.0) by selecting default fonts
- API breaking change: `QwtLinearColorMap.colorStops` now returns a list of `ColorStop` objects instead of the list of stop values

## Version 0.11.2

- Fixed `TypeError` on `QwtPlotLayout.minimumSizeHint`

## Version 0.11.1

- Fixed remaining `QwtPainter.drawPixmap` call

## Version 0.11.0

- Dropped support for Python 3.7 and earlier
- Dropped support for PyQt4 and PySide2
- Removed unnecessary argument `numPoints` in `QwtSymbol.drawSymbols` and `QwtSymbol.renderSymbols` methods
- `QwtPlotCanvas`: fixed `BackingStore` feature (`paintAttribute`)

## Version 0.10.6

- Qt6 support:
  - Handled all occurences of deprecated ``QWidget.getContentsMargins`` method.
  - Removed references to NonCosmeticDefaultPen
  - Fixed `QApplication.desktop` `AttributeError`
  - Fixed `QPrinter.HighResolution` `AttributeError` on Linux
  - Fixed `QPrinter.setColorMode` `AttributeError` on PyQt6/Linux
  - Fixed `QPrinter.setOrientation` deprecation issue
  - Fixed `QPrinter.setPaperSize` deprecation issue
- Improved unit tests:
  - Ensure that tests are entirely executed before quitting (in unattended mode)
  - Added more tests on `qwt.symbols`
  - Added tests on `qwt.plot_renderer`
- `qwt.plot_renderer`: fixed resolution type
- `qwt.symbols`: fixed `QPointF` type mismatch
- Removed CHM help file generation (obsolete)

## Version 0.10.5

- [Issue #81](https://github.com/PlotPyStack/PythonQwt/issues/81) - Signal disconnection issue with PySide 6.5.3

## Version 0.10.4

- [Issue #80](https://github.com/PlotPyStack/PythonQwt/issues/80) - Print to PDF: AttributeError: 'NoneType' object has no attribute 'getContentsMargins'

## Version 0.10.3

- [Issue #79](https://github.com/PlotPyStack/PythonQwt/issues/79) - TypeError: unexpected type 'QSize' (thanks to @luc-j-bourhis)

- Moved project to the [PlotPyStack](https://github.com/PlotPyStack) organization.

- Unit tests: added support for ``pytest`` and ``coverage`` (60% coverage as of today)

- [Issue #74](https://github.com/PlotPyStack/PythonQwt/issues/74) - TypeError: QwtPlotDict.__init__() [...] with PySide 6.5.0

- [Issue #77](https://github.com/PlotPyStack/PythonQwt/issues/77) - AttributeError: 'XXX' object has no attribute '_QwtPlot__data'

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
- Fixed event management in `QwtPlot` and removed unnecessary `QEvent.LayoutRequest` emission in `QwtScaleWidget` (caused high CPU usage with `guiqwt.ImageWidget`).
- `QwtScaleDiv`: fixed ticks initialization when passing all arguments to constructor.
- tests/image.py: fixed overriden `updateLegend` signature.

## Version 0.9.0

- `QwtPlot`: set the `autoReplot` option at False by default, to avoid time consuming implicit plot updates.
- Added `QwtPlotItem.setIcon` and `QwtPlotItem.icon` method for setting and getting the icon associated to the plot item (as of today, this feature is not strictly needed in PythonQwt: this has been implemented for several use cases in higher level libraries (see PR #61).
- Removed unused `QwtPlotItem.defaultIcon` method.
- Added various minor optimizations for axes/ticks drawing features.
- Fixed `QwtPlot.canvasMap` when `axisScaleDiv` returns None.
- Fixed alias `np.float` which is deprecated in NumPy 1.20.

## Version 0.8.3

- Fixed simple plot examples (setup.py & plot.py's doc page) following the introduction of the new QtPy dependency (Qt compatibility layer) since V0.8.0.

## Version 0.8.2

- Added new GUI-based test script `PythonQwt-py3` to run the test launcher.
- Added command-line options to the `PythonQwt-tests-py3` script to run all the tests simultenously in unattended mode (`--mode unattended`) or to update all the screenshots (`--mode screenshots`).
- Added internal scripts for automated test in virtual environments with both PyQt5 and PySide2.

## Version 0.8.1

- PySide2 support was significatively improved betwen PythonQwt V0.8.0 and V0.8.1 thanks to the new `qwt.qwt_curve.array2d_to_qpolygonf` function.

## Version 0.8.0

- Added PySide2 support: PythonQwt is now compatible with Python 2.7, Python 3.4+, PyQt4, PyQt5 and PySide2!

## Version 0.7.1

- Changed QwtPlotItem.detachItems signature: removed unnecessary "autoDelete" argument, initialiazing "rtti" argument to None (remove all items)
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
- QwtPlot: added "flatStyle" option, a PythonQwt-exclusive feature improving default plot style (without margin, more compact and flat look) -- option is enabled by default
- QwtAbstractScaleDraw: added option to set the tick color lighter factor for each tick type (minor, medium, major) -- this feature is used with the new flatStyle option
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

- Fixed rounding issue with PythonQwt scale engine (0...1000 is now divided in 200-size steps, as in both Qwt and PyQwt)
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

Fixed an annoying bug which caused scale widget (axis ticks in particular) to be misaligned with canvas grid: the user was forced to resize the plot widget as a workaround

## Version 0.5.3

- Better handling of infinity and `NaN` values in scales (removed `NumPy` warnings)
- Now handling infinity and `NaN` values in series data: removing points that can't be drawn
- Fixed logarithmic scale engine: presence of values <= 0 was slowing down series data plotting

## Version 0.5.2

- Added CHM documentation to wheel package
- Fixed `QwtPlotRenderer.setDiscardFlag`/`setLayoutFlag` args
- Fixed `QwtPlotItem.setItemInterest` args
- Fixed `QwtPlot.setAxisAutoScale`/`setAutoReplot` args

## Version 0.5.1

- Fixed Issue #22: fixed scale issues in [CurveDemo2.py](qwt/tests/CurveDemo2.py) and [ImagePlotDemo.py](qwt/tests/ImagePlotDemo.py)
- `QwtPlotCurve`: sticks were not drawn correctly depending on orientation
- `QwtInterval`: avoid overflows with `NumPy` scalars
- Fixed Issue #28: curve shading was broken since v0.5.0
- setup.py: using setuptools "entry_points" instead of distutils "scripts"
- Showing curves/plots number in benchmarks to avoid any misinterpretation (see Issue #26)
- Added Python2/Python3 scripts for running tests

## Version 0.5.0

- Various optimizations
- Major API simplification, taking into account the feature that won't be implemented (fitting, rounding, weeding out points, clipping, etc.)
- Added `QwtScaleDraw.setLabelAutoSize`/`labelAutoSize` methods to set the new auto size option (see [documentation](http://pythonhosted.org/PythonQwt/))
- `QwtPainter`: removed unused methods `drawRoundFrame`, `drawImage` and `drawPixmap`

## Version 0.4.0

- Color bar: fixed axis ticks shaking when color bar is enabled
- Fixed `QwtPainter.drawColorBar` for horizontal color bars (typo)
- Restored compatibility with original Qwt signals (`QwtPlot`, ...)

## Version 0.3.0

Renamed the project (python-qwt --> PythonQwt), for various reasons.

## Version 0.2.1

Fixed Issue #23: "argument numPoints is not implemented" error was showing up when calling `QwtSymbol.drawSymbol(symbol, QPoint(x, y))`.

## Version 0.2.0

Added docstrings in all Python modules and a complete documentation based on Sphinx. See the Overview section for API limitations when comparing to Qwt.

## Version 0.1.1

Fixed Issue #21 (blocking issue *only* on non-Windows platforms when building the package): typo in "PythonQwt-tests" script name (in [setup script](setup.py))

## Version 0.1.0

First alpha public release.
