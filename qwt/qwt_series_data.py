# -*- coding: utf-8 -*-

from qwt.qwt_sample import QwtIntervalSample, QwtSetSample, QwtOHLCSample

from qwt.qt.QtCore import QRectF, QPointF


def qwtBoundingRect(*args):
    if len(args) == 1:
        sample, = args
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
    elif len(args) == 3:
        series, from_, to = args
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
        self.d_boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
    
    def setRectOfInterest(self, rect):
        raise NotImplementedError
    
    def size(self):
        raise NotImplementedError
        
    def sample(self, i):
        raise NotImplementedError


class QwtArraySeriesData(QwtSeriesData):
    def __init__(self, samples=None):
        QwtSeriesData.__init__(self)
        self.d_samples = []
        if samples is not None:
            self.d_samples = samples
        
    def setSamples(self, samples):
        self.d_boundingRect = QRectF(0.0, 0.0, -1.0, -1.0)
        self.d_samples = samples
    
    def samples(self):
        return self.d_samples
    
    def size(self):
        return len(self.d_samples)
    
    def sample(self, i):
        return self.d_samples[i]
    

class QwtPointSeriesData(QwtArraySeriesData):
    def __init__(self, samples=[]):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self.d_boundingRect.width() < 0.:
            self.d_boundingRect = qwtBoundingRect(self)
        return self.d_boundingRect


class QwtPoint3DSeriesData(QwtArraySeriesData):
    def __init__(self, samples):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self.d_boundingRect.width() < 0.:
            self.d_boundingRect = qwtBoundingRect(self)
        return self.d_boundingRect


class QwtIntervalSeriesData(QwtArraySeriesData):
    def __init__(self, samples):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self.d_boundingRect.width() < 0.:
            self.d_boundingRect = qwtBoundingRect(self)
        return self.d_boundingRect


class QwtSetSeriesData(QwtArraySeriesData):
    def __init__(self, samples):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self.d_boundingRect.width() < 0.:
            self.d_boundingRect = qwtBoundingRect(self)
        return self.d_boundingRect


class QwtTradingChartData(QwtArraySeriesData):
    def __init__(self, samples):
        QwtArraySeriesData.__init__(self, samples)
    
    def boundingRect(self):
        if self.d_boundingRect.width() < 0.:
            self.d_boundingRect = qwtBoundingRect(self)
        return self.d_boundingRect

