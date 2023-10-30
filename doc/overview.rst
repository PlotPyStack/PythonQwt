Purpose and Motivation
======================

The ``PythonQwt`` project was initiated to solve -at least temporarily-
the obsolescence issue of `PyQwt` (the Python-Qwt C++ bindings library)
which is no longer maintained. The idea was to translate the original
Qwt C++ code to Python and then to optimize some parts of the code by
writing new modules based on NumPy and other libraries.

Overview
========

The ``PythonQwt`` package consists of a single Python package named
`qwt` and of a few other files (examples, doc, ...):

    - The subpackage `qwt.tests` contains the PythonQwt unit tests:

        - 75% were directly adapted from Qwt/C++ demos (Bode demo, cartesian demo, etc.).

        - 25% were written specifically for PythonQwt.

        - The test launcher is an exclusive PythonQwt feature.

The `qwt` package is a pure Python implementation of `Qwt` C++ library
with the following limitations.

The following `Qwt` classes won't be reimplemented in `qwt` because more
powerful features already exist in `guiqwt` (and in the forthcoming `plotpy` library,
resulting of the merge of `guidata` and `guiqwt`): `QwtPlotZoomer`,
`QwtCounter`, `QwtEventPattern`, `QwtPicker`, `QwtPlotPicker`.

Only the following plot items are currently implemented in `qwt` (the
only plot items needed by `guiqwt` and `plotpy`): `QwtPlotItem` (base class),
`QwtPlotItem`, `QwtPlotMarker`, `QwtPlotSeriesItem` and `QwtPlotCurve`.

The `HistogramItem` object implemented in PyQwt's HistogramDemo.py is not
available here (a similar item is already implemented in `guiqwt`/`plotpy`). As a
consequence, the following classes are not implemented: `QwtPlotHistogram`,
`QwtIntervalSeriesData`, `QwtIntervalSample`.

The following data structure objects are not implemented as they seemed
irrelevant with Python and NumPy: `QwtCPointerData` (as a consequence, method
`QwtPlot.setRawSamples` is not implemented), `QwtSyntheticPointData`.

The following sample data type objects are not implemented as they seemed
quite specific: `QwtSetSample`, `QwtOHLCSample`. For similar reasons, the
`QwtPointPolar` class and the following sample iterator objects are not
implemented: `QwtSetSeriesData`, `QwtTradingChartData` and `QwtPoint3DSeriesData`.

The following classes are not implemented because they seem inappropriate in
the Python/NumPy context: `QwtArraySeriesData`, `QwtPointSeriesData`,
`QwtAbstractSeriesStore`.

Threads:

    - Multiple threads for graphic rendering is implemented in Qwt C++ code
      thanks to the `QtConcurrent` and `QFuture` Qt features which are
      currently not supported by PyQt.

    - As a consequence the following API is not supported in `PythonQwt`:
        - `QwtPlotItem.renderThreadCount`
        - `QwtPlotItem.setRenderThreadCount`
        - option `numThreads` in `QwtPointMapper.toImage`

The `QwtClipper` class is not implemented yet (and it will probably be
very difficult or even impossible to implement it in pure Python without
performance issues). As a consequence, when zooming in a plot curve, the
entire curve is still painted (in other words, when working with large
amount of data, there is no performance gain when zooming in).

The curve fitter feature is not implemented because powerful curve fitting
features are already implemented in `guiqwt`/`plotpy`.

Other API compatibility issues with `Qwt`:

    - `QwtPlotCurve.MinimizeMemory` option was removed as this option has no
      sense in PythonQwt (the polyline plotting is not taking more memory
      than the array data that is already there).

    - `QwtPlotCurve.Fitted` option was removed as this option is not supported
      at the moment.
