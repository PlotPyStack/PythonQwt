.. _examples:

Examples
========

The test launcher
-----------------

A lot of examples are available in the ``qwt.tests`` module ::

    from qwt import tests
    tests.run()

The two lines above execute the ``PythonQwt-tests`` test launcher:

.. image:: /../qwt/tests/data/testlauncher.png

GUI-based test launcher can be executed from the command line thanks to the
``PythonQwt-tests`` test script.

Unit tests may be executed from the command line thanks to the console-based script
``PythonQwt-tests``: ``PythonQwt-tests --mode unattended``.

Tests
-----



Here are some examples from the `qwt.tests` module:

.. toctree::
    :maxdepth: 2

    bodedemo
    cartesian
    cpudemo
    curvebenchmark1
    curvebenchmark2
    curvedemo1
    curvedemo2
    data
    errorbar
    eventfilter
    image
    logcurve
    mapdemo
    multidemo
    simple
    vertical
