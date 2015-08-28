# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

from qwt.qt.QtCore import qFuzzyCompare

import numpy as np


def qwtFuzzyCompare(value1, value2, intervalSize):
    eps = abs(1.e-6*intervalSize)
    if value2 - value1 > eps:
        return -1
    elif value1 - value2 > eps:
        return 1
    else:
        return 0

def qwtFuzzyGreaterOrEqual(d1, d2):
    return (d1 >= d2) or qFuzzyCompare(d1, d2)

def qwtFuzzyLessOrEqual(d1, d2):
    return (d1 <= d2) or qFuzzyCompare(d1, d2)

def qwtSign(x):
    if x > 0.:
        return 1
    elif x < 0.:
        return -1
    else:
        return 0

def qwtSqr(x):
    return x**2

def qwtFastAtan(x):
    if x < -1.:
        return -.5*np.pi - x/(x**2 + .28)
    elif x > 1.:
        return .5*np.pi - x/(x**2 + .28)
    else:
        return x/(1. + x**2*.28)

def qwtFastAtan2(y, x):
    if x > 0:
        return qwtFastAtan(y/x)
    elif x < 0:
        d = qwtFastAtan(y/x)
        if y >= 0:
            return d + np.pi
        else:
            return d - np.pi
    elif y < 0.:
        return -.5*np.pi
    elif y > 0.:
        return .5*np.pi
    else:
        return 0.

def qwtRadians(degrees):
    return degrees * np.pi/180.

def qwtDegrees(radians):
    return radians * 180./np.pi

