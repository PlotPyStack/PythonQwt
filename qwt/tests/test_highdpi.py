# -*- coding: utf-8 -*-
#
# Licensed under the terms of the PyQwt License
# Copyright (C) 2003-2009 Gerard Vermeulen, for the original PyQwt example
# Copyright (c) 2015 Pierre Raybaut, for the PyQt5/PySide port and further
# developments (e.g. ported to PythonQwt API)
# (see LICENSE file for more details)

SHOW = True  # Show test in GUI-based test launcher

import os

import pytest

from qwt.tests import utils
from qwt.tests.test_simple import SimplePlot


class HighDPIPlot(SimplePlot):
    NUM_POINTS = 5000000  # 5 million points needed to test high DPI support


@pytest.mark.skip(reason="This test is not relevant for the automated test suite")
def test_highdpi():
    """Test high DPI support"""

    # Performance should be the same with "1" and "2" scale factors:
    # (as of today, this is not the case, but it has to be fixed in the future:
    #  https://github.com/PlotPyStack/PythonQwt/issues/83)
    os.environ["QT_SCALE_FACTOR"] = "2"

    utils.test_widget(HighDPIPlot, (800, 480))


if __name__ == "__main__":
    test_highdpi()
