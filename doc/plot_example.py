import qwt
import numpy as np

app = qtpy.QtGui.QApplication([])
x = np.linspace(-10, 10, 500)
plot = qwt.QwtPlot("Trigonometric functions")
plot.insertLegend(qwt.QwtLegend(), qwt.QwtPlot.BottomLegend)
qwt.QwtPlotCurve.make(x, np.cos(x), "Cosinus", plot, linecolor="red", antialiased=True)
qwt.QwtPlotCurve.make(x, np.sin(x), "Sinus", plot, linecolor="blue", antialiased=True)
plot.resize(600, 300)
plot.show()

import os.path as osp

plot.grab().save(
    osp.join(osp.abspath(osp.dirname(__file__)), "images", "QwtPlot_example.png")
)

app.exec_()
