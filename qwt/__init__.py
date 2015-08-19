
QWT_VERSION_STR = '6.1.2'

import warnings

from qwt.qwt_plot import QwtPlot
from qwt.qwt_symbol import QwtSymbol as QSbl  # see deprecated section
from qwt.qwt_scale_engine import QwtLinearScaleEngine, QwtLogScaleEngine
from qwt.qwt_text import QwtText
from qwt.qwt_plot_canvas import QwtPlotCanvas
from qwt.qwt_plot_curve import QwtPlotCurve as QPC  # see deprecated section
from qwt.qwt_plot_curve import QwtPlotItem
from qwt.qwt_scale_map import QwtScaleMap
from qwt.qwt_interval import QwtInterval
from qwt.qwt_legend import QwtLegend
from qwt.qwt_plot_marker import QwtPlotMarker
from qwt.qwt_plot_grid import QwtPlotGrid as QPG  # see deprecated section
from qwt.qwt_color_map import QwtLinearColorMap

from qwt.toqimage import toQImage

from qwt.qwt_scale_div import QwtScaleDiv
from qwt.qwt_scale_draw import QwtScaleDraw
from qwt.qwt_scale_draw import QwtAbstractScaleDraw
from qwt.qwt_series_data import QwtIntervalSeriesData
from qwt.qwt_sample import QwtIntervalSample
from qwt.qwt_painter import QwtPainter
from qwt.qwt_legend_data import QwtLegendData

from qwt.qwt_plot_renderer import QwtPlotRenderer


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
        from qwt.qt.QtCore import QPointF
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


#TODO: implement QwtClipper: needed for SVG export for example
