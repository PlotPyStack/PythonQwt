#!/usr/bin/env python

from qwt.qt.QtCore import QRectF
from qwt.qt.QtGui import QPolygonF

import numpy as np
import time

N = 50000000


def solution1(x, y):
    xmin = x.min()
    xmax = x.max()
    ymin = y.min()
    ymax = y.max()
    return QRectF(xmin, ymin, xmax-xmin, ymax-ymin)
    
def solution2(x, y):
    size = x.size
    try:
        info = np.finfo(x.dtype)
    except ValueError:
        info = np.iinfo(x.dtype)
    polygon = QPolygonF(size)
    pointer = polygon.data()
    pointer.setsize(2*size*info.dtype.itemsize)
    memory = np.frombuffer(pointer, np.float)
    memory[0::2] = x
    memory[1::2] = y
    return polygon.boundingRect()

def timeit(func, x, y):
    t0 = time.time()
    out = func(x,y)
    print("%r:" % func)
    print("  Elapsed time: %dms" % int((time.time()-t0)*1000))
    print("  Result: %r" % out)

if __name__ == '__main__':
    x = np.linspace(-10, 10, N)
    y = np.cos(x)
    timeit(solution1, x, y)
    timeit(solution2, x, y)
    