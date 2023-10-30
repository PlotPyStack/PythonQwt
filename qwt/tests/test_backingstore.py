# -*- coding: utf-8 -*-

SHOW = False  # Do not show test in GUI-based test launcher

from qwt.tests import utils
from qwt.tests.test_simple import SimplePlot


class BackingStorePlot(SimplePlot):
    TEST_EXPORT = False

    def __init__(self):
        SimplePlot.__init__(self)
        self.canvas().setPaintAttribute(self.canvas().BackingStore, True)


def test_backingstore():
    """Test for backing store"""
    utils.test_widget(BackingStorePlot, size=(600, 400))


if __name__ == "__main__":
    test_backingstore()
