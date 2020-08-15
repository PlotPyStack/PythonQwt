from qwt.qt.QtGui import QApplication, QPen, QPainterPath, QTransform
from qwt.qt.QtCore import Qt, QPointF
from qwt import QwtPlot, QwtPlotCurve, QwtSymbol
import numpy as np
import os.path as osp

app = QApplication([])

# --- Construct custom symbol ---

path = QPainterPath()
path.moveTo(0, 8)
path.lineTo(0, 5)
path.lineTo(-3, 5)
path.lineTo(0, 0)
path.lineTo(3, 5)
path.lineTo(0, 5)

transform = QTransform()
transform.rotate(-30.0)
path = transform.map(path)

pen = QPen(Qt.black, 2)
pen.setJoinStyle(Qt.MiterJoin)

symbol = QwtSymbol()
symbol.setPen(pen)
symbol.setBrush(Qt.red)
symbol.setPath(path)
symbol.setPinPoint(QPointF(0.0, 0.0))
symbol.setSize(10, 14)

# --- Test it within a simple plot ---

curve = QwtPlotCurve()
curve_pen = QPen(Qt.blue)
curve_pen.setStyle(Qt.DotLine)
curve.setPen(curve_pen)
curve.setSymbol(symbol)
x = np.linspace(0, 10, 10)
curve.setData(x, np.sin(x))

plot = QwtPlot()
curve.attach(plot)
plot.resize(600, 300)
plot.replot()
plot.show()

plot.grab().save(
    osp.join(osp.abspath(osp.dirname(__file__)), "images", "symbol_path_example.png")
)

app.exec_()
