# History of changes

## Version 0.5.2

Added CHM documentation to wheel package
Fixed QwtPlotRenderer.setDiscardFlag/setLayoutFlag args
Fixed QwtPlotItem.setItemInterest args
Fixed QwtPlot.setAxisAutoScale/setAutoReplot args

## Version 0.5.1

Fixed Issue #22: fixed scale issues in CurveDemo2.py and ImagePlotDemo.py
QwtPlotCurve: sticks were not drawn correctly depending on orientation
QwtInterval: avoid overflows with NumPy scalars
Fixed Issue #28: curve shading was broken since v0.5.0
setup.py: using setuptools "entry_points" instead of distutils "scripts"
Showing curves/plots number in benchmarks to avoid any misinterpretation (see Issue #26)
Added Python2/Python3 scripts for running tests

## Version 0.5.0

Various optimizations
Major API simplification, taking into account the feature that won't be implemented (fitting, rounding, weeding out points, clipping, etc.)
Added QwtScaleDraw.setLabelAutoSize/labelAutoSize methods to set the new auto size option (see documentation)

## Version 0.4.0

Color bar: fixed axis ticks shaking when color bar is enabled
Fixed QwtPainter.drawColorBar for horizontal color bars (typo)
Restored compatibility with original Qwt signals (QwtPlot, ...)

## Version 0.3.0

Renamed the project (python-qwt --> PythonQwt), for various reasons.

## Version 0.2.1

Fixed Issue #23: "argument numPoints is not implemented" error was showing up 
when calling QwtSymbol.drawSymbol(symbol, QPoint(x, y)).

## Version 0.2.0

Added docstrings in all Python modules and a complete documentation based on 
Sphinx. See the Overview section for API limitations when comparing to Qwt.

## Version 0.1.1

Fixed Issue #21 (blocking issue *only* on non-Windows platforms when building 
the package): typo in "PythonQwt-tests" script name (setup.py)

## Version 0.1.0

First alpha public release.
