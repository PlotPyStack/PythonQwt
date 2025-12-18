# PythonQwt AI Coding Agent Instructions

## Project Overview

**PythonQwt** is a pure Python implementation of the Qwt C++ plotting library. It provides low-level Qt plotting widgets that form the foundation for higher-level libraries like PlotPy.

### Technology Stack

- **Python**: 3.9+
- **Core**: NumPy (≥1.19), QtPy (≥1.9)
- **GUI**: Qt via QtPy (PyQt5/PyQt6/PySide6)
- **Testing**: pytest
- **Linting**: Ruff, Pylint

### Architecture

```
qwt/
├── plot.py           # QwtPlot main widget
├── plot_canvas.py    # Plot canvas
├── plot_curve.py     # QwtPlotCurve
├── plot_marker.py    # QwtPlotMarker
├── plot_grid.py      # QwtPlotGrid
├── scale_*.py        # Scale engine, map, division, drawing
├── symbol.py         # QwtSymbol for markers
├── legend.py         # QwtLegend
├── text.py           # QwtText, QwtTextLabel
├── graphic.py        # QwtGraphic
└── tests/            # pytest suite
```

## Development Workflows

### Running Commands

Use batch scripts in `scripts/`:

```powershell
scripts\run_pytest.bat        # Run tests
scripts\run_ruff.bat          # Format and lint
scripts\run_pylint.bat        # Pylint checks
scripts\run_coverage.bat      # Coverage report
scripts\take_screenshots.bat  # Generate doc images
```

Or directly:

```powershell
python -m pytest qwt --ff
python -m ruff format
python -m ruff check --fix
```

### Running Test Launcher

```powershell
PythonQwt                           # GUI test launcher
PythonQwt-tests --mode unattended   # Headless tests
```

Or from Python:

```python
from qwt import tests
tests.run()
```

## Core Patterns

### Basic Plot Creation

```python
import numpy as np
from qtpy import QtWidgets as QW
import qwt

app = QW.QApplication([])

# Create plot widget
plot = qwt.QwtPlot("My Plot Title")
plot.insertLegend(qwt.QwtLegend(), qwt.QwtPlot.BottomLegend)

# Add curves
x = np.linspace(0, 10, 100)
qwt.QwtPlotCurve.make(x, np.sin(x), "Sine", plot,
                       linecolor="blue", antialiased=True)

# Add grid
grid = qwt.QwtPlotGrid()
grid.attach(plot)

plot.resize(600, 400)
plot.show()
app.exec_()
```

### QwtPlotCurve Factory Method

The `make` class method simplifies curve creation:

```python
curve = qwt.QwtPlotCurve.make(
    x, y,                    # Data arrays
    title="My Curve",        # Legend title
    plot=plot,               # Parent plot (auto-attaches)
    linecolor="red",         # Line color
    linewidth=2,             # Line width
    linestyle=Qt.DashLine,   # Qt line style
    antialiased=True,        # Anti-aliasing
    marker=qwt.QwtSymbol.Ellipse,  # Marker symbol
    markersize=8,            # Marker size
)
```

### Key Classes

| Class | Purpose |
|-------|---------|
| `QwtPlot` | Main plot widget |
| `QwtPlotCurve` | 2D curve item |
| `QwtPlotMarker` | Point/line markers |
| `QwtPlotGrid` | Grid lines |
| `QwtLegend` | Legend widget |
| `QwtSymbol` | Marker symbols |
| `QwtScaleEngine` | Scale calculations |
| `QwtScaleMap` | Scale transformations |
| `QwtText` | Rich text labels |

### Scale Configuration

```python
# Set axis titles
plot.setAxisTitle(qwt.QwtPlot.xBottom, "Time (s)")
plot.setAxisTitle(qwt.QwtPlot.yLeft, "Amplitude")

# Set axis scale
plot.setAxisScale(qwt.QwtPlot.xBottom, 0, 100)

# Logarithmic scale
plot.setAxisScaleEngine(qwt.QwtPlot.yLeft, qwt.QwtLogScaleEngine())
```

### Symbols and Markers

```python
# Create marker
marker = qwt.QwtPlotMarker()
marker.setSymbol(qwt.QwtSymbol(
    qwt.QwtSymbol.Diamond,
    QBrush(Qt.yellow),
    QPen(Qt.red, 2),
    QSize(10, 10)
))
marker.setValue(x_pos, y_pos)
marker.attach(plot)
```

## Coding Conventions

### Qt Imports

Use QtPy for Qt binding abstraction:

```python
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QPen, QBrush, QColor
from qtpy.QtWidgets import QWidget
```

### Docstrings

Standard Python docstrings:

```python
def setData(self, x, y):
    """Set curve data.

    :param x: X coordinates (array-like)
    :param y: Y coordinates (array-like)
    """
```

## Key Files Reference

| File | Purpose |
|------|---------|
| `qwt/plot.py` | QwtPlot implementation |
| `qwt/plot_curve.py` | QwtPlotCurve with `make()` factory |
| `qwt/scale_engine.py` | Linear/log scale engines |
| `qwt/scale_map.py` | Scale transformations |
| `qwt/symbol.py` | QwtSymbol definitions |
| `qwt/tests/__init__.py` | Test launcher |

## Limitations vs C++ Qwt

The following are **not implemented** (PlotPy provides these):

- `QwtPlotZoomer` - Use PlotPy's zoom tools
- `QwtPicker` - Use PlotPy's interactive tools
- `QwtPlotPicker` - Use PlotPy's selection tools

Only essential plot items are implemented:
- `QwtPlotItem` (base)
- `QwtPlotCurve`
- `QwtPlotMarker`
- `QwtPlotGrid`
- `QwtPlotSeriesItem`

## Related Projects

- **guidata**: Dataset/parameter framework (sibling)
- **PlotPy**: High-level plotting using PythonQwt (downstream)
