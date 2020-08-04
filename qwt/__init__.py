# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)
"""
PythonQwt
=========

The ``PythonQwt`` package is a 2D-data plotting library using Qt graphical 
user interfaces for the Python programming language. It is compatible with 
both ``PyQt4`` and ``PyQt5`` (``PySide`` is currently not supported but it
could be in the near future as it would "only" requires testing to support 
it as a stable alternative to PyQt).

It consists of a single Python package named `qwt` which is a pure Python 
implementation of Qwt C++ library with some limitations.

.. image:: images/panorama.png

External resources:
    * Python Package Index: `PyPI`_
    * Project page on GitHub: `GitHubPage`_
    * Bug reports and feature requests: `GitHub`_

.. _PyPI: https://pypi.python.org/pypi/PythonQwt
.. _GitHubPage: http://pierreraybaut.github.io/PythonQwt
.. _GitHub: https://github.com/PierreRaybaut/PythonQwt
"""
__version__ = '0.6.0'
QWT_VERSION_STR = '6.1.5'

import warnings

from .plot import QwtPlot
from .symbol import QwtSymbol as QSbl  # see deprecated section
from .scale_engine import QwtLinearScaleEngine, QwtLogScaleEngine
from .text import QwtText
from .plot_canvas import QwtPlotCanvas
from .plot_curve import QwtPlotCurve as QPC  # see deprecated section
from .plot_curve import QwtPlotItem
from .scale_map import QwtScaleMap
from .interval import QwtInterval
from .legend import QwtLegend, QwtLegendData, QwtLegendLabel
from .plot_marker import QwtPlotMarker
from .plot_grid import QwtPlotGrid as QPG  # see deprecated section
from .color_map import QwtLinearColorMap

from .toqimage import array_to_qimage as toQImage

from .scale_div import QwtScaleDiv
from .scale_draw import QwtScaleDraw
from .scale_draw import QwtAbstractScaleDraw
from .painter import QwtPainter

from .plot_series import (QwtSeriesData, QwtPointArrayData, QwtSeriesStore,
                             QwtPlotSeriesItem)

from .plot_renderer import QwtPlotRenderer

from .plot_directpainter import QwtPlotDirectPainter


## ============================================================================
## Deprecated classes and attributes (to be removed in next major release)
## ============================================================================
#  Remove deprecated QwtPlotItem.setAxis (replaced by setAxes)
#  Remove deprecated QwtPlotCanvas.invalidatePaintCache (replaced by replot)
## ============================================================================
class QwtDoubleInterval(QwtInterval):
    def __init__(self, minValue=0., maxValue=-1., borderFlags=None):
        warnings.warn("`QwtDoubleInterval` has been removed in Qwt6: "\
                      "please use `QwtInterval` instead", RuntimeWarning)
        super(QwtDoubleInterval, self).__init__(minValue, maxValue, borderFlags)
## ============================================================================
class QwtLog10ScaleEngine(QwtLogScaleEngine):
    def __init__(self):
        warnings.warn("`QwtLog10ScaleEngine` has been removed in Qwt6: "\
                      "please use `QwtLogScaleEngine` instead",
                      RuntimeWarning)
        super(QwtLog10ScaleEngine, self).__init__(10)
## ============================================================================
class QwtPlotPrintFilter(object):
    def __init__(self):
        raise NotImplementedError("`QwtPlotPrintFilter` has been removed in Qwt6: "\
                                  "please rely on `QwtPlotRenderer` instead")
## ============================================================================
class QwtPlotCurve(QPC):
    @property
    def Yfx(self):
        raise NotImplementedError("`Yfx` attribute has been removed "\
                            "(curve types are no longer implemented in Qwt6)")
    @property
    def Xfy(self):
        raise NotImplementedError("`Yfx` attribute has been removed "\
                            "(curve types are no longer implemented in Qwt6)")
## ============================================================================
class QwtSymbol(QSbl):
    def draw(self, painter, *args):
        warnings.warn("`draw` has been removed in Qwt6: "\
                      "please rely on `drawSymbol` and `drawSymbols` instead",
                      RuntimeWarning)
        from .qt.QtCore import QPointF
        if len(args) == 2:
            self.drawSymbols(painter, [QPointF(*args)])
        else:
            self.drawSymbol(painter, *args)
## ============================================================================
class QwtPlotGrid(QPG):
    def majPen(self):
        warnings.warn("`majPen` has been removed in Qwt6: "\
                      "please use `majorPen` instead",
                      RuntimeWarning)
        return self.majorPen()
    def minPen(self):
        warnings.warn("`minPen` has been removed in Qwt6: "\
                      "please use `minorPen` instead",
                      RuntimeWarning)
        return self.minorPen()
    def setMajPen(self, *args):
        warnings.warn("`setMajPen` has been removed in Qwt6: "\
                      "please use `setMajorPen` instead",
                      RuntimeWarning)
        return self.setMajorPen(*args)
    def setMinPen(self, *args):
        warnings.warn("`setMinPen` has been removed in Qwt6: "\
                      "please use `setMinorPen` instead",
                      RuntimeWarning)
        return self.setMinorPen(*args)
## ============================================================================
