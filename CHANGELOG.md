# PythonQwt Releases #


### Version 0.5.5 ###

- `QwtScaleMap.invTransform_scalar`: avoid divide by 0
- Avoid error when computing ticks: when the axis was so small that no tick could be drawn, an exception used to be raised


### Version 0.5.4 ###

Fixed an annoying bug which caused scale widget (axis ticks in particular) 
to be misaligned with canvas grid: the user was forced to resize the plot 
widget as a workaround


### Version 0.5.3 ###

- Better handling of infinity and `NaN` values in scales (removed `NumPy` 
warnings)
- Now handling infinity and `NaN` values in series data: removing points that 
can't be drawn
- Fixed logarithmic scale engine: presence of values <= 0 was slowing down 
series data plotting


### Version 0.5.2 ###

- Added CHM documentation to wheel package
- Fixed `QwtPlotRenderer.setDiscardFlag`/`setLayoutFlag` args
- Fixed `QwtPlotItem.setItemInterest` args
- Fixed `QwtPlot.setAxisAutoScale`/`setAutoReplot` args


### Version 0.5.1 ###

- Fixed Issue #22: fixed scale issues in [CurveDemo2.py](qwt/tests/CurveDemo2.py) 
and [ImagePlotDemo.py](qwt/tests/ImagePlotDemo.py)
- `QwtPlotCurve`: sticks were not drawn correctly depending on orientation
- `QwtInterval`: avoid overflows with `NumPy` scalars
- Fixed Issue #28: curve shading was broken since v0.5.0
- setup.py: using setuptools "entry_points" instead of distutils "scripts"
- Showing curves/plots number in benchmarks to avoid any misinterpretation 
(see Issue #26)
- Added Python2/Python3 scripts for running tests


### Version 0.5.0 ###

- Various optimizations
- Major API simplification, taking into account the feature that won't be 
implemented (fitting, rounding, weeding out points, clipping, etc.)
- Added `QwtScaleDraw.setLabelAutoSize`/`labelAutoSize` methods to set the new 
auto size option (see [documentation](http://pythonhosted.org/PythonQwt/))


### Version 0.4.0 ###

- Color bar: fixed axis ticks shaking when color bar is enabled
- Fixed `QwtPainter.drawColorBar` for horizontal color bars (typo)
- Restored compatibility with original Qwt signals (`QwtPlot`, ...)


### Version 0.3.0 ###

Renamed the project (python-qwt --> PythonQwt), for various reasons.


### Version 0.2.1 ###

Fixed Issue #23: "argument numPoints is not implemented" error was showing 
up when calling `QwtSymbol.drawSymbol(symbol, QPoint(x, y))`.


### Version 0.2.0 ###

Added docstrings in all Python modules and a complete documentation based on 
Sphinx. See the Overview section for API limitations when comparing to Qwt.


### Version 0.1.1 ###

Fixed Issue #21 (blocking issue *only* on non-Windows platforms when 
building the package): typo in "PythonQwt-tests" script name 
(in [setup script](setup.py))


### Version 0.1.0 ###

First alpha public release.
