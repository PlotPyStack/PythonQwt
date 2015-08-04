
QWT_VERSION_STR = '6.1.0'

from qwt.qwt_plot import QwtPlot
from qwt.qwt_symbol import QwtSymbol
from qwt.qwt_scale_engine import QwtLinearScaleEngine, QwtLogScaleEngine
from qwt.qwt_text import QwtText
from qwt.qwt_plot_canvas import QwtPlotCanvas
from qwt.qwt_plot_curve import QwtPlotCurve, QwtPlotItem
from qwt.qwt_scale_map import QwtScaleMap
from qwt.qwt_interval import QwtInterval
from qwt.qwt_legend import QwtLegend
from qwt.qwt_plot_marker import QwtPlotMarker
from qwt.qwt_plot_grid import QwtPlotGrid
from qwt.qwt_color_map import QwtLinearColorMap

from qwt.toqimage import toQImage

from qwt.qwt_scale_div import QwtScaleDiv
from qwt.qwt_scale_draw import QwtScaleDraw
from qwt.qwt_scale_draw import QwtAbstractScaleDraw
from qwt.qwt_series_data import QwtIntervalSeriesData
from qwt.qwt_sample import QwtIntervalSample
from qwt.qwt_painter import QwtPainter
from qwt.qwt_legend_data import QwtLegendData

QwtDoubleInterval = QwtInterval

# to be implemented:
# QwtPlotPrintFilter
class QwtPlotPrintFilter(object):
    pass
