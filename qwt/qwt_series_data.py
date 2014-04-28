# -*- coding: utf-8 -*-

from qwt.qwt_sample import QwtIntervalSample, QwtSetSample, QwtOHLCSample

from qwt.qt.QtCore import QRectF, QPointF


def qwtBoundingRect(sample):
    if isinstance(sample, (QPointF, QwtPoint3d)):
        return QRectF(sample.x(), sample.y(), 0.0, 0.0)
    elif isinstance(sample, QwtPointPolar):
        return QRectF(sample.x(), sample.y(), 0.0, 0.0)
    elif isinstance(sample, QwtIntervalSample):
        return QRectF(sample.interval.minValue(), sample.value,
                      sample.interval.maxValue()-sample.interval.minValue(), 0.)
    elif isinstance(sample, QwtSetSample):
        minY = sample.set[0]
        maxY = sample.set[0]
        for val in sample.set:
            if val < minY:
                minY = val
            if val > maxY:
                maxY = val
        minX = sample.value
        maxX = sample.value
        return QRectF(minX, minY, maxX-minX, maxY-minY)
    elif isinstance(sample, QwtOHLCSample):
        interval = sample.boundingInterval()
        return QRectF(interval.minValue(), sample.time, interval.width(), 0.)


