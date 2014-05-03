# -*- coding: utf-8 -*-

from qwt.qt.QtGui import QPaintEngine, QPainterPath, QPaintDevice


class QwtNullPaintDevice_PrivateData(object):
    def __init__(self):
        self.mode = QwtNullPaintDevice.NormalMode


class QwtNullPaintDevice_PaintEngine(QPaintEngine):
    def __init__(self):
        super(QwtNullPaintDevice_PaintEngine, self
              ).__init__(QPaintEngine.AllFeatures)
    
    def begin(self, paintdevice):
        self.setActive(True)
        return True
    
    def end(self):
        self.setActive(False)
        return True
    
    def type(self):
        return QPaintEngine.User
    
    def drawRects(self, rects, rectCount):
        device = self.nullDevice()
        if device is None:
            return
        if device.mode() != QwtNullPaintDevice.NormalMode:
            QPaintEngine.drawRects(rects, rectCount)
            return
        device.drawRects(rects, rectCount)
    
    def drawLines(self, lines, lineCount):
        device = self.nullDevice()
        if device is None:
            return
        if device.mode() != QwtNullPaintDevice.NormalMode:
            QPaintEngine.drawLines(lines, lineCount)
            return
        device.drawLines(lines, lineCount)
    
    def drawEllipse(self, rect):
        device = self.nullDevice()
        if device is None:
            return
        if device.mode() != QwtNullPaintDevice.NormalMode:
            QPaintEngine.drawEllipse(rect)
            return
        device.drawEllipse(rect)
    
    def drawPath(self, path):
        device = self.nullDevice()
        if device is None:
            return
        device.drawPath(path)
        
    def drawPoints(self, points, pointCount):
        device = self.nullDevice()
        if device is None:
            return
        if device.mode() != QwtNullPaintDevice.NormalMode:
            QPaintEngine.drawPoints(points, pointCount)
            return
        device.drawPoints(points, pointCount)
        
    def drawPolygon(self, points, pointCount, mode):
        device = self.nullDevice()
        if device is None:
            return
        if device.mode() == QwtNullPaintDevice.PathMode:
            path = QPainterPath()
            if pointCount > 0:
                path.moveTo(points[0])
                for i in range(pointCount):
                    path.lineTo(points[i])
                if mode != QPaintEngine.PolylineMode:
                    path.closeSubpath()
            device.drawPath(path)
            return
        device.drawPolygon(points, pointCount, mode)
    
    def drawPixmap(self, rect, pm, subRect):
        device = self.nullDevice()
        if device is None:
            return
        device.drawPixmap(rect, pm, subRect)
    
    def drawTextItem(self, pos, textItem):
        device = self.nullDevice()
        if device is None:
            return
        if device.mode() != QwtNullPaintDevice.NormalMode:
            QPaintEngine.drawTextItem(pos, textItem)
            return
        device.drawTextItem(pos, textItem)
    
    def drawTiledPixmap(self, rect, pixmap, subRect):
        device = self.nullDevice()
        if device is None:
            return
        if device.mode() != QwtNullPaintDevice.NormalMode:
            QPaintEngine.drawTiledPixmap(rect, pixmap, subRect)
            return
        device.drawTiledPixmap(rect, pixmap, subRect)
    
    def drawImage(self, rect, image, subRect, flags):
        device = self.nullDevice()
        if device is None:
            return
        device.drawImage(rect, image, subRect, flags)

    def updateState(self, state):
        device = self.nullDevice()
        if device is None:
            return
        device.updateState(state)
    
    def nullDevice(self):
        if not self.isActive():
            return
        return QwtNullPaintDevice(self.paintDevice())


class QwtNullPaintDevice(QPaintDevice):
    
    # enum Mode
    NormalMode, PolygonPathMode, PathMode = range(3)
    
    def __init__(self):
        super(QwtNullPaintDevice, self).__init__()
        self.__engine = None
        self.__data = QwtNullPaintDevice_PrivateData()
    
    def setMode(self, mode):
        self.__data.mode = mode
    
    def mode(self):
        return self.__data.mode
    
    def paintEngine(self):
        if self.__engine is None:
            self.__engine = QwtNullPaintDevice_PaintEngine()
        return self.__engine
    
    def metric(self, deviceMetric):
        if deviceMetric == QPaintDevice.PdmWidth:
            value = self.sizeMetrics().width()
        elif deviceMetric == QPaintDevice.PdmHeight:
            value = self.sizeMetrics().height()
        elif deviceMetric == QPaintDevice.PdmNumColors:
            value = 0xffffffff
        elif deviceMetric == QPaintDevice.PdmDepth:
            value = 32
        elif deviceMetric in (QPaintDevice.PdmPhysicalDpiX,
                              QPaintDevice.PdmPhysicalDpiY,
                              QPaintDevice.PdmDpiY, QPaintDevice.PdmDpiX):
            value = 72
        elif deviceMetric == QPaintDevice.PdmWidthMM:
            value = round(self.metric(QPaintDevice.PdmWidth)*25.4/self.metric(QPaintDevice.PdmDpiX))
        elif deviceMetric == QPaintDevice.PdmHeightMM:
            value = round(self.metric(QPaintDevice.PdmHeight)*25.4/self.metric(QPaintDevice.PdmDpiY))
        else:
            value = 0
        return value
    
    def drawRects(self, rects, rectCount):
        super(QwtNullPaintDevice, self).drawRects(rects, rectCount)
    
    def drawLines(self, lines, lineCount):
        super(QwtNullPaintDevice, self).drawLines(lines, lineCount)
        
    def drawEllipse(self, rect):
        super(QwtNullPaintDevice, self).drawEllipse(rect)
        
    def drawPath(self, path):
        super(QwtNullPaintDevice, self).drawPath(path)
    
    def drawPoints(self, points, pointCount):
        super(QwtNullPaintDevice, self).drawPoints(points, pointCount)
    
    def drawPolygon(self, points, pointCount, mode):
        super(QwtNullPaintDevice, self).drawPolygon(points, pointCount, mode)
    
    def drawPixmap(self, rect, pm, subRect):
        super(QwtNullPaintDevice, self).drawPixmap(rect, pm, subRect)
    
    def drawTextItem(self, pos, textItem):
        super(QwtNullPaintDevice, self).drawPolygon(pos, textItem)
    
    def drawTiledPixmap(self, rect, pm, subRect):
        super(QwtNullPaintDevice, self).drawTiledPixmap(rect, pm, subRect)
    
    def drawImage(self, rect, image, subRect, flags):
        super(QwtNullPaintDevice, self).drawImage(rect, image, subRect, flags)
    
    def updateState(self, state):
        super(QwtNullPaintDevice, self).updateState(state)

    