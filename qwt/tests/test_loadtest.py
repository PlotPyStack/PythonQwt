# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License
# Copyright (c) 2015-2021 Pierre Raybaut
# (see LICENSE file for more details)

"""Load test"""

SHOW = True  # Show test in GUI-based test launcher

import time

# Local imports
from qwt.tests import test_curvebenchmark1 as cb
from qwt.tests import utils

NCOLS, NROWS = 6, 5
NPLOTS = NCOLS * NROWS * 5 * 3


class LTWidget(cb.BMWidget):
    def params(self, *args, **kwargs):
        return tuple([("Lines", None)] * NCOLS * NROWS)


class LoadTest(cb.CurveBenchmark1):
    TITLE = "Load test [%d plots]" % NPLOTS
    SIZE = (1600, 700)

    def __init__(self, max_n=100, parent=None, unattended=False, **kwargs):
        super(LoadTest, self).__init__(
            max_n=max_n, parent=parent, unattended=unattended, **kwargs
        )

    def run_benchmark(self, max_n, unattended, **kwargs):
        points, symbols = 100, False
        iterator = range(0, 1) if unattended else range(int(NPLOTS / (NCOLS * NROWS)))
        for _i_page in iterator:
            t0 = time.time()
            symtext = "with%s symbols" % ("" if symbols else "out")
            widget = LTWidget(NCOLS, points, symbols, **kwargs)
            title = "%d points" % points
            description = "%d plots with %d curves of %d points, %s" % (
                widget.plot_nb,
                widget.curve_nb,
                points,
                symtext,
            )
            self.process_iteration(title, description, widget, t0)


def test_loadtest():
    """Load test"""
    utils.test_widget(LoadTest, options=False)


if __name__ == "__main__":
    test_loadtest()
