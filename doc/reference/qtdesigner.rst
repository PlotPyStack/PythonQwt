Qt Designer
===========

PythonQwt ships a Qt Designer plugin which makes the :class:`qwt.QwtPlot`
widget available directly inside Qt Designer's widget box, in the "PythonQwt"
group.

Installing the plugin
---------------------

The plugin file ``qwtplugin.py`` lives in the ``qtdesigner`` directory at the
root of the PythonQwt source tree. To make it available in Qt Designer, add
that directory to the ``PYQTDESIGNERPATH`` environment variable before
starting Qt Designer:

.. code-block:: bash

    # Linux/macOS
    export PYQTDESIGNERPATH=<path to PythonQwt>/qtdesigner
    designer

.. code-block:: bat

    rem Windows
    set PYQTDESIGNERPATH=<path to PythonQwt>\qtdesigner
    designer

.. note::

    Qt Designer custom widget plugins require PyQt5 or PyQt6. PySide6 does not
    expose ``QPyDesignerCustomWidgetPlugin``.

Loading a ``.ui`` file at runtime
---------------------------------

The :mod:`qwt.qtdesigner` module provides helper functions to load or compile
``.ui`` files embedding :class:`qwt.QwtPlot` widgets:

.. code-block:: python

    from qwt.qtdesigner import loadui

    FormClass = loadui("myform.ui")
    form = FormClass()
    form.plotwidget.setTitle("Loaded from Qt Designer")

Reference
---------

.. automodule:: qwt.qtdesigner
