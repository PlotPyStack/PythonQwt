# -*- coding: utf-8 -*-

SHOW = True  # Show test in GUI-based test launcher

import os.path as osp

import numpy as np
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

import qwt
from qwt.tests import utils


class BaseSymbolPlot(qwt.QwtPlot):
    TITLE = "Base Symbol Example"
    SYMBOL_CLASS = qwt.QwtSymbol

    def __init__(self):
        super().__init__()
        self.setTitle(self.TITLE)
        self.setAxisScale(self.yLeft, -20, 20)
        self.setAxisScale(self.xBottom, -20, 20)
        self.setup_plot()

    def setup_plot(self):
        samples = ([-15, 0, 15, -15], [0, 15, 0, 0])
        self.add_curve(self.TITLE, samples, self.SYMBOL_CLASS())
        self.resize(400, 400)

    def add_curve(self, title, samples, symbol=None):
        """Add a curve to the plot"""
        curve = qwt.QwtPlotCurve(title)
        curve.setSamples(*samples)
        if symbol is not None:
            curve.setSymbol(symbol)
        curve.attach(self)
        self.replot()


class BuiltinSymbolPlot(BaseSymbolPlot):
    TITLE = "Built-in Symbol Example"

    def setup_plot(self):
        colors = (QC.Qt.red, QC.Qt.green, QC.Qt.blue, QC.Qt.yellow, QC.Qt.magenta)
        for index, symbol_name in enumerate(
            (
                "Ellipse",
                "Rect",
                "Diamond",
                "Triangle",
                "DTriangle",
                "UTriangle",
                "LTriangle",
                "RTriangle",
                "Cross",
                "XCross",
                "HLine",
                "VLine",
                "Star1",
                "Star2",
                "Hexagon",
            )
        ):
            symbol = qwt.symbol.QwtSymbol(getattr(qwt.QwtSymbol, symbol_name))
            symbol.setSize(7, 7)
            symbol.setPen(QG.QPen(colors[index % 3]))
            symbol.setBrush(QG.QBrush(QG.QColor(colors[index % 3]).lighter(150)))
            x = np.linspace(-10, 10, 100)
            y = np.sin(x + index * np.pi / 10)
            samples = (x, y)
            qwt.plot_marker.QwtPlotMarker.make(
                xvalue=index * 2 - 10,
                yvalue=index * 2 - 10,
                label=qwt.text.QwtText.make(
                    "Marker",
                    color=QC.Qt.black,
                    borderradius=2,
                    brush=QC.Qt.lightGray,
                ),
                symbol=symbol,
                plot=self,
            )
            self.add_curve(symbol_name, samples, symbol)
        self.setAxisAutoScale(self.yLeft, True)
        self.setAxisAutoScale(self.xBottom, True)


class CustomGraphicSymbol(qwt.QwtSymbol):
    def __init__(self):
        super(CustomGraphicSymbol, self).__init__(qwt.QwtSymbol.Graphic)

        # Use a built-in Qt icon as QPixmap for demonstration
        icon = QW.QApplication.style().standardIcon(QW.QStyle.SP_FileIcon)
        pixmap = icon.pixmap(20, 20)

        # Convert the QPixmap to a QwtGraphic
        graphic = qwt.graphic.QwtGraphic()
        graphic.setDefaultSize(pixmap.size())
        painter = QG.QPainter(graphic)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        # Set the QwtGraphic as the graphic for the symbol
        self.setGraphic(graphic)


class GraphicPlot(BaseSymbolPlot):
    TITLE = "Custom QwtGraphic Symbol Example"
    SYMBOL_CLASS = CustomGraphicSymbol


class CustomPixmapSymbol(qwt.QwtSymbol):
    def __init__(self):
        super(CustomPixmapSymbol, self).__init__(qwt.QwtSymbol.Pixmap)

        # Use a built-in Qt icon as QPixmap for demonstration
        icon = QW.QApplication.style().standardIcon(QW.QStyle.SP_DialogYesButton)
        pixmap = icon.pixmap(20, 20)

        # Set the QPixmap for the symbol
        self.setPixmap(pixmap)


class PixmapPlot(BaseSymbolPlot):
    TITLE = "Custom QPixmap Symbol Example"
    SYMBOL_CLASS = CustomPixmapSymbol


class CustomPathSymbol(qwt.QwtSymbol):
    def __init__(self):
        super(CustomPathSymbol, self).__init__(qwt.QwtSymbol.Path)

        path = QG.QPainterPath()
        path.moveTo(0, -10)  # Top vertex of the triangle
        path.lineTo(-10, 10)  # Bottom-left vertex
        path.lineTo(10, 10)  # Bottom-right vertex
        path.closeSubpath()  # Close the triangle

        self.setPath(path)
        self.setSize(20, 20)


class PathPlot(BaseSymbolPlot):
    TITLE = "Custom Path Symbol Example"
    SYMBOL_CLASS = CustomPathSymbol


class CustomSvgSymbol(qwt.QwtSymbol):
    FNAME = osp.join(osp.dirname(__file__), "data", "symbol.svg")

    def __init__(self):
        super(CustomSvgSymbol, self).__init__(qwt.QwtSymbol.SvgDocument)

        # Load the SVG document from the given file
        self.setSvgDocument(self.FNAME)


class SvgDocumentPlot(BaseSymbolPlot):
    TITLE = "Custom SVG Symbol Example"
    SYMBOL_CLASS = CustomSvgSymbol


def test_base():
    """Base symbol test"""
    utils.test_widget(BaseSymbolPlot, size=(600, 400))


def test_builtin():
    """Built-in symbol test"""
    utils.test_widget(BuiltinSymbolPlot, size=(600, 400))


def test_graphic():
    """Graphic symbol test"""
    utils.test_widget(GraphicPlot, size=(600, 400))


def test_pixmap():
    """Pixmap test"""
    utils.test_widget(PixmapPlot, size=(600, 400))


def test_path():
    """Path symbol test"""
    utils.test_widget(PathPlot, size=(600, 400))


def test_svg():
    """SVG test"""
    utils.test_widget(SvgDocumentPlot, size=(600, 400))


if __name__ == "__main__":
    # test_base()
    test_builtin()
    # test_graphic()
    # test_pixmap()
    # test_path()
    # test_svg()
