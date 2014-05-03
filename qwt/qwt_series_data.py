# -*- coding: utf-8 -*-

from qwt.qwt_sample import QwtIntervalSample, QwtSetSample, QwtOHLCSample

from qwt.qt.QtCore import QRectF, QPointF


class QwtPoint3d(object):
    pass  # Fake / to be implemented

class QwtPointPolar(object):
    pass  # Fake / to be implemented


def qwtBoundingRect(*args):
    if args:
        sample = args[0]
    if len(args) == 1 and isinstance(sample, (QPointF, QwtPoint3d)):
        return QRectF(sample.x(), sample.y(), 0.0, 0.0)
    elif len(args) == 1 and isinstance(sample, QwtPointPolar):
        return QRectF(sample.x(), sample.y(), 0.0, 0.0)
    elif len(args) == 1 and isinstance(sample, QwtIntervalSample):
        return QRectF(sample.interval.minValue(), sample.value,
                      sample.interval.maxValue()-sample.interval.minValue(), 0.)
    elif len(args) == 1 and isinstance(sample, QwtSetSample):
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
    elif len(args) == 1 and isinstance(sample, QwtOHLCSample):
        interval = sample.boundingInterval()
        return QRectF(interval.minValue(), sample.time, interval.width(), 0.)
    elif len(args) in (1, 2, 3):
        series = args[0]
        from_ = 0
        to = -1
        if len(args) > 1:
            from_ = args[1]
            if len(args) > 2:
                to = args[2]
        return qwtBoundingRectT(series, from_, to)
    else:
        raise TypeError("%s() takes 1 or 3 argument(s) (%s given)"\
                        % ("qwtBoundingRect", len(args)))


def qwtBoundingRectT(series, from_, to):
    boundingRect = QRectF(1.0, 1.0, -2.0, -2.0)
    if from_ < 0:
        from_ = 0
    if to < 0:
        to = series.size()-1
    if to < from_:
        return boundingRect
    first_stage = True
    for i in range(from_, to+1):
        rect = qwtBoundingRect(series.sample(i))
        if rect.width() >= 0. and rect.height() >= 0.:
            if first_stage:
                boundingRect = rect
                first_stage = False
                continue
            else:
                boundingRect.setLeft(min([boundingRect.left(), rect.left()]))
                boundingRect.setRight(max([boundingRect.right(), rect.right()]))
                boundingRect.setTop(min([boundingRect.top(), rect.top()]))
                boundingRect.setBottom(max([boundingRect.bottom(), rect.bottom()]))
    return boundingRect


class QwtSeriesData(object):
    def __init__(self):
        self._boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
    
    def setRectOfInterest(self, rect):
        raise NotImplementedError
    
    def size(self):
        raise NotImplementedError
        
    def sample(self, i):
        raise NotImplementedError


class QwtArraySeriesData(QwtSeriesData):
    def __init__(self, samples=None):
        QwtSeriesData.__init__(self)
        self.__samples = []
        if samples is not None:
            self.__samples = samples
        
    def setSamples(self, samples):
        self._boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.__samples = samples
    
    def samples(self):
        return self.__samples
    
    def size(self):
        return len(self.__samples)
    
    def sample(self, i):
        return self.__samples[i]
    

class QwtPointSeriesData(QwtArraySeriesData):
    def __init__(self, samples=[]):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self._boundingRect.width() < 0.:
            self._boundingRect = qwtBoundingRect(self)
        return self._boundingRect


class QwtPoint3DSeriesData(QwtArraySeriesData):
    def __init__(self, samples):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self._boundingRect.width() < 0.:
            self._boundingRect = qwtBoundingRect(self)
        return self._boundingRect


class QwtIntervalSeriesData(QwtArraySeriesData):
    def __init__(self, samples):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self._boundingRect.width() < 0.:
            self._boundingRect = qwtBoundingRect(self)
        return self._boundingRect


class QwtSetSeriesData(QwtArraySeriesData):
    def __init__(self, samples):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self._boundingRect.width() < 0.:
            self._boundingRect = qwtBoundingRect(self)
        return self._boundingRect


class QwtTradingChartData(QwtArraySeriesData):
    def __init__(self, samples):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self._boundingRect.width() < 0.:
            self._boundingRect = qwtBoundingRect(self)
        return self._boundingRect

