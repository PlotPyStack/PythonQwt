# -*- coding: utf-8 -*-

import numpy as np


class QwtTransform(object):
    def __init__(self):
        pass
    
    def bounded(self, value):
        return value
    
    def transform(self, value):
        raise NotImplementedError
    
    def invTransform(self, value):
        raise NotImplementedError
    
    def copy(self):
        raise NotImplementedError


class QwtNullTransform(QwtTransform):
    def transform(self, value):
        return value
    
    def invTransform(self, value):
        return value
    
    def copy(self):
        return QwtNullTransform()


class QwtLogTransform(QwtTransform):
    LogMin = 1.0e-150
    LogMax = 1.0e150
    def bounded(self, value):
        return np.clip(value, self.LogMin, self.LogMax)

    def transform(self, value):
        return np.log(value)
    
    def invTransform(self, value):
        return np.exp(value)
    
    def copy(self):
        return QwtLogTransform()


class QwtPowerTransform(QwtTransform):
    def __init__(self, exponent):
        self.__exponent = exponent
        super(QwtPowerTransform, self).__init__()

    def transform(self, value):
        if value < 0.:
            return -np.pow(-value, 1./self.__exponent)
        else:
            return np.pow(value, 1./self.__exponent)
    
    def invTransform(self, value):
        if value < 0.:
            return -np.pow(-value, self.__exponent)
        else:
            return np.pow(value, self.__exponent)
    
    def copy(self):
        return QwtPowerTransform()
